<#
.SYNOPSIS
    セッション終了時に、そのセッションでユーザーが出した指示を .claude/instruction_log.md へ追記し、
    Git 管理下であればそのままコミット〜マージまで行う。

.DESCRIPTION
    SessionEnd フックから呼ばれる。フック入力（JSON）を標準入力で受け取り、
    セッションのトランスクリプト（JSONL）から人間が入力した指示だけを抜き出して記録する。

    記録のあと、次の条件をすべて満たすときだけ commit-flow スキルと同じ流れでコミットする。
    満たさなければ記録のみで終わる。
      - .claude が Git リポジトリの中にある
      - instruction_log.md が .gitignore で除外されていない
      - instruction_log.md に差分がある
      - 現在のブランチが既定ブランチ（main 等）である（作業中の feature ブランチには手を出さない）

    NOTE: 指示の判定は origin.kind == "human"。
          ツール結果・スラッシュコマンドの内部ブロック・タスク通知はこの印を持たないため自然に除外される。

    NOTE: JSONL は UTF-8。Get-Content の既定エンコーディングだと日本語が壊れるため
          ReadLines で明示的に UTF-8 を指定している。

    NOTE: SessionEnd フックは既定で 1.5 秒しか待ってもらえない。push まで終えるには
          settings の timeout を 60（上限）にしておくこと。

    NOTE: 失敗してもセッション終了を妨げないよう、例外は握りつぶして常に 0 で終わる。
#>
Set-StrictMode -Off
$ErrorActionPreference = "Stop"

# 記録済みセッションを見分ける印。追記のたびに同じ節を作り直せるようにする
$MARKER_PREFIX = "<!-- session:"

$LOG_NAME = "instruction_log.md"

function Write-ErrorNote {
    <#
    .SYNOPSIS
        失敗の内容を .claude/instruction_log.error.txt に残す（最後の1件だけ）。
    .PARAMETER Message
        残す内容。
    #>
    param([string]$Message)

    try {
        $errFile = Join-Path (Split-Path -Parent $PSScriptRoot) "instruction_log.error.txt"
        [System.IO.File]::WriteAllText($errFile, "$(Get-Date -Format s) $Message`n", (New-Object System.Text.UTF8Encoding($false)))
    } catch {}
}

function Get-HumanPrompts {
    <#
    .SYNOPSIS
        トランスクリプトから人間が入力した指示を取り出す。
    .PARAMETER Path
        セッションのトランスクリプト（JSONL）のパス。
    .OUTPUTS
        時刻（ローカル）と本文を持つオブジェクトの並び。指示が無ければ空。
    #>
    param([string]$Path)

    $prompts = @()

    foreach ($line in [System.IO.File]::ReadLines($Path, [System.Text.Encoding]::UTF8)) {
        if (-not $line.Trim()) { continue }

        try { $record = $line | ConvertFrom-Json } catch { continue }

        if ($record.type -ne "user") { continue }
        if ($record.origin.kind -ne "human") { continue }

        # 人間の指示は content が文字列。配列（tool_result など）は対象外
        $text = $record.message.content
        if ($text -isnot [string]) { continue }
        if (-not $text.Trim()) { continue }

        $at = $null
        if ($record.timestamp) {
            try { $at = ([datetime]$record.timestamp).ToLocalTime() } catch { $at = $null }
        }

        $prompts += [pscustomobject]@{ At = $at; Text = $text.Trim() }
    }

    return $prompts
}

function Format-Section {
    <#
    .SYNOPSIS
        1セッション分の節を組み立てる。
    .PARAMETER SessionId
        セッションID（節を作り直すときの目印に使う）。
    .PARAMETER Prompts
        Get-HumanPrompts が返した指示の並び（1件以上）。
    .OUTPUTS
        Markdown の節（末尾は空行）。
    #>
    param([string]$SessionId, $Prompts)

    $times = @($Prompts | Where-Object { $_.At } | ForEach-Object { $_.At })
    $short = if ($SessionId.Length -ge 8) { $SessionId.Substring(0, 8) } else { $SessionId }

    # 見出しは「日付 開始-終了 (セッションIDの先頭8桁)」。時刻が1つも取れなければ日付を省く
    if ($times.Count -gt 0) {
        $first = ($times | Sort-Object)[0]
        $last = ($times | Sort-Object)[-1]
        $span = if ($first.ToString("HH:mm") -eq $last.ToString("HH:mm")) {
            $first.ToString("HH:mm")
        } else {
            "$($first.ToString('HH:mm'))-$($last.ToString('HH:mm'))"
        }
        $heading = "## $($first.ToString('yyyy-MM-dd')) $span ($short)"
    } else {
        $heading = "## ($short)"
    }

    $lines = @("$MARKER_PREFIX$SessionId -->", $heading, "")

    foreach ($p in $Prompts) {
        $stamp = if ($p.At) { $p.At.ToString("HH:mm") } else { "--:--" }

        # 複数行の指示は箇条書きが途切れないよう継続行を字下げする
        $body = ($p.Text -split "`r?`n") -join "`n  "
        $lines += "- **$stamp** $body"
    }

    $lines += ""
    return $lines
}

function Invoke-Git {
    <#
    .SYNOPSIS
        .claude ディレクトリを起点に git を実行する。
    .PARAMETER GitArgs
        git に渡す引数。
    .OUTPUTS
        Code（終了コード）と Out（標準出力を1つの文字列にしたもの）。
    #>
    param([string[]]$GitArgs)

    # NOTE: PowerShell 5.1 は外部コマンドの stderr を 2>&1 で拾うと例外にしてしまうため、
    #       stderr はリダイレクトせずそのまま流し、成否は終了コードだけで判断する
    $ErrorActionPreference = "Continue"
    $out = & git -C (Split-Path -Parent $PSScriptRoot) @GitArgs
    return [pscustomobject]@{ Code = $LASTEXITCODE; Out = (@($out) -join "`n").Trim() }
}

function Invoke-CommitFlow {
    <#
    .SYNOPSIS
        instruction_log.md だけを commit-flow スキルと同じ流れでコミットし、既定ブランチへマージして push する。
    .PARAMETER Heading
        コミットメッセージの本文に入れるセッションの見出し（例: 2026-10-15 09:00-10:00 (abcd1234)）。
    .DESCRIPTION
        feature ブランチ作成 → コミット → 既定ブランチへ --no-ff マージ → ブランチ削除 → push。
        NOTE: commit-flow は feature ブランチも push してから消すが、push 直後に消すので
              リモートに残る結果は同じ。終了時の待ち時間を減らすため既定ブランチの push だけにしている。
        条件を満たさないときは何もしない（記録のみで終わる）。
    #>
    param([string]$Heading)

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { return }

    # Git 管理外なら記録のみ
    if ((Invoke-Git @("rev-parse", "--is-inside-work-tree")).Out -ne "true") { return }

    # .gitignore で除外されている（各自の手元に残す運用）なら記録のみ
    if ((Invoke-Git @("check-ignore", "-q", "--", $LOG_NAME)).Code -eq 0) { return }

    # 差分が無ければコミットするものが無い
    if (-not (Invoke-Git @("status", "--porcelain", "--", $LOG_NAME)).Out) { return }

    # 衝突の解消途中などは触らない
    if ((Invoke-Git @("ls-files", "-u")).Out) { return }

    $default = (Invoke-Git @("symbolic-ref", "--short", "refs/remotes/origin/HEAD")).Out -replace "^origin/", ""
    if (-not $default) {
        $default = if ((Invoke-Git @("rev-parse", "--verify", "-q", "refs/heads/main")).Code -eq 0) { "main" } else { "master" }
    }

    # 作業中の feature ブランチ（や detached HEAD）では記録のみ
    $current = (Invoke-Git @("symbolic-ref", "--short", "-q", "HEAD")).Out
    if ($current -ne $default) { return }

    $branch = "feature/instruction-log-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    $message = @(
        "リポジトリ共通: 指示履歴を記録",
        "",
        "セッション終了時のフック（.claude/hooks/save_instruction_log.ps1）による自動コミット。",
        "",
        "- .claude/$LOG_NAME に $($Heading -replace '^## ', '') の指示を追記"
    ) -join "`n"

    if ((Invoke-Git @("switch", "-c", $branch)).Code -ne 0) {
        Write-ErrorNote "ブランチ $branch を作れなかったためコミットしていない"
        return
    }

    # パスを指定したコミットはそのファイルだけを対象にする（他にステージ済みの変更があっても巻き込まない）
    # NOTE: 未追跡のファイルはパス指定のコミットで拾えないため、先に add しておく
    Invoke-Git @("add", "--", $LOG_NAME) | Out-Null
    if ((Invoke-Git @("commit", "-m", $message, "--", $LOG_NAME)).Code -ne 0) {
        Invoke-Git @("switch", $default) | Out-Null
        Invoke-Git @("branch", "-D", $branch) | Out-Null
        Write-ErrorNote "$LOG_NAME のコミットに失敗した（$default に戻してブランチは削除済み）"
        return
    }

    if ((Invoke-Git @("switch", $default)).Code -ne 0) {
        Write-ErrorNote "$default に戻れなかった。$branch にコミットが残っている"
        return
    }

    if ((Invoke-Git @("merge", "--no-ff", $branch, "-m", "$($branch)をマージ")).Code -ne 0) {
        Invoke-Git @("merge", "--abort") | Out-Null
        Write-ErrorNote "$branch を $default にマージできなかった（マージは中止、ブランチは残している）"
        return
    }

    Invoke-Git @("branch", "-d", $branch) | Out-Null

    # リモートが無ければローカルのマージまでで終わる
    if ((Invoke-Git @("remote", "get-url", "origin")).Code -ne 0) { return }

    # 認証の入力待ちで固まらないようにする（ターミナルが無いので答えられない）
    $env:GIT_TERMINAL_PROMPT = "0"
    if ((Invoke-Git @("push", "origin", $default)).Code -ne 0) {
        Write-ErrorNote "$default の push に失敗した。マージはローカルに済んでいるので、次回の push で反映される"
    }
}

try {
    # NOTE: フック入力は UTF-8。[Console]::In だとコンソール既定（CP932）で読まれ、
    #       日本語パスの「ト」等の2バイト目が直後の \ を巻き込んで JSON のエスケープが壊れる
    $stdin = New-Object System.IO.StreamReader(
        [Console]::OpenStandardInput(), (New-Object System.Text.UTF8Encoding($false)))
    $raw = $stdin.ReadToEnd()
    $input_ = $raw | ConvertFrom-Json

    $sessionId = $input_.session_id
    $transcript = $input_.transcript_path

    # トランスクリプトの場所が渡らない場合に備え、セッションIDから探す
    if ((-not $transcript) -or (-not (Test-Path -LiteralPath $transcript))) {
        if (-not $sessionId) { exit 0 }

        $projects = Join-Path $HOME ".claude\projects"
        if (-not (Test-Path -LiteralPath $projects)) { exit 0 }

        $found = Get-ChildItem $projects -Recurse -Filter "$sessionId.jsonl" -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if (-not $found) { exit 0 }

        $transcript = $found.FullName
    }

    $prompts = Get-HumanPrompts -Path $transcript
    if ($prompts.Count -eq 0) { exit 0 }

    # 出力先は「このスクリプトが置かれている .claude」の直下に固定する
    # NOTE: フック入力の cwd を使わないのは、セッション中に作業ディレクトリが移っていても
    #       .claude を移植した先へ確実に書くため
    $claudeDir = Split-Path -Parent $PSScriptRoot
    $logFile = Join-Path $claudeDir $LOG_NAME

    $header = "# CLI 指示履歴"

    # NOTE: ファイルの有無ではなく中身で判定する。移植のたびに空の instruction_log.md が
    #       先に置かれることがあり、存在だけで既存扱いにするとヘッダーが永久に付かない
    $current = if (Test-Path -LiteralPath $logFile) {
        [System.IO.File]::ReadAllText($logFile, [System.Text.Encoding]::UTF8)
    } else {
        ""
    }
    $existing = if ($current.Trim()) {
        $current -split "`r?`n"
    } else {
        @($header, "", "このファイルはセッション終了時に自動で追記される（.claude/hooks/save_instruction_log.ps1）。", "")
    }

    # 同じセッションの節が既にあれば、その節だけを差し替える（終了処理が複数回走っても重複しない）
    $marker = "$MARKER_PREFIX$sessionId -->"
    $start = [Array]::IndexOf($existing, $marker)

    # NOTE: 範囲演算子は 0..-1 が @(0, -1) になり配列を逆順に取り出してしまう。
    #       先頭・末尾を切り落とす箇所では必ず件数を先に確かめる
    if ($start -ge 0) {
        $end = $existing.Length
        for ($i = $start + 1; $i -lt $existing.Length; $i++) {
            if ($existing[$i].StartsWith($MARKER_PREFIX)) { $end = $i; break }
        }
        $before = if ($start -gt 0) { @($existing[0..($start - 1)]) } else { @() }
        $after = if ($end -lt $existing.Length) { @($existing[$end..($existing.Length - 1)]) } else { @() }
        $kept = $before + $after
    } else {
        $kept = @($existing)
    }

    # 末尾の空行を1つにそろえてから節を足す
    while ($kept.Length -gt 1 -and -not $kept[-1].Trim()) {
        $kept = @($kept[0..($kept.Length - 2)])
    }
    if ($kept.Length -eq 1 -and -not $kept[0].Trim()) { $kept = @() }

    $section = Format-Section -SessionId $sessionId -Prompts $prompts
    $out = @($kept) + @("") + $section

    # BOM 無しの UTF-8 で書く（BOM 付きだと他のツールが読むときに先頭が壊れる）
    # NOTE: 改行は LF にする。ファイル全体を書き直すため、CRLF にすると
    #       .gitattributes（eol=lf）のリポジトリで追記のたびに全行が改行コードだけの差分になる
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($logFile, ($out -join "`n"), $utf8)

    # 記録が済んでからコミットする（コミット側の失敗で記録が失われないように分けている）
    try {
        Invoke-CommitFlow -Heading $section[1]
    } catch {
        Write-ErrorNote "コミット中に例外: $_`n$($_.ScriptStackTrace)"
    }
}
catch {
    # セッション終了を妨げない。原因は隣にメモだけ残す
    Write-ErrorNote "$_`n$($_.ScriptStackTrace)"
}

exit 0

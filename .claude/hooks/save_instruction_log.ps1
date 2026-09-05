<#
.SYNOPSIS
    セッション終了時に、そのセッションでユーザーが出した指示を .claude/instruction_log.md へ追記する。

.DESCRIPTION
    SessionEnd フックから呼ばれる。フック入力（JSON）を標準入力で受け取り、
    セッションのトランスクリプト（JSONL）から人間が入力した指示だけを抜き出して記録する。

    NOTE: 指示の判定は origin.kind == "human"。
          ツール結果・スラッシュコマンドの内部ブロック・タスク通知はこの印を持たないため自然に除外される。

    NOTE: JSONL は UTF-8。Get-Content の既定エンコーディングだと日本語が壊れるため
          ReadLines で明示的に UTF-8 を指定している。

    NOTE: 失敗してもセッション終了を妨げないよう、例外は握りつぶして常に 0 で終わる。
#>
Set-StrictMode -Off
$ErrorActionPreference = "Stop"

# 記録済みセッションを見分ける印。追記のたびに同じ節を作り直せるようにする
$MARKER_PREFIX = "<!-- session:"

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
    $logFile = Join-Path $claudeDir "instruction_log.md"

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

    $out = @($kept) + @("") + (Format-Section -SessionId $sessionId -Prompts $prompts)

    # BOM 無しの UTF-8 で書く（BOM 付きだと他のツールが読むときに先頭が壊れる）
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($logFile, ($out -join "`r`n"), $utf8)
}
catch {
    # セッション終了を妨げない。原因は隣にメモだけ残す
    try {
        $errFile = Join-Path (Split-Path -Parent $PSScriptRoot) "instruction_log.error.txt"
        [System.IO.File]::WriteAllText($errFile, "$(Get-Date -Format s) $_`r`n$($_.ScriptStackTrace)", (New-Object System.Text.UTF8Encoding($false)))
    } catch {}
}

exit 0

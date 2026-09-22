# convert.ps1 - invoked by the PowerShell tool by dot-sourcing:
#   . convert.ps1
# Requires $In and $Out. Optionally set $DumpPages to a file path to receive one
# line per caption: "<kind>|<number>|<page>".
$log = "C:\Users\Administrator\Desktop\JC2001-SF-Assessment\.workbuddy\build\convert.log"
"=== $(Get-Date -Format s) ===" | Set-Content $log -Encoding UTF8
"In : $In" | Add-Content $log
"Out: $Out" | Add-Content $log

$doc = $null
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    ("word version " + $word.Version) | Add-Content $log

    $doc = $word.Documents.Open($In, $false, $true)
    "opened document" | Add-Content $log

    for ($i = 1; $i -le 3; $i++) {
        $doc.Fields.Update() | Out-Null
        $n = 0
        foreach ($t in $doc.TablesOfContents) { $t.Update() | Out-Null; $n++ }
        $doc.Repaginate()
        ("pass $i  pages=" + $doc.ComputeStatistics(2) + "  words=" + $doc.ComputeStatistics(0) + "  tocFields=" + $n) | Add-Content $log
    }

    if ($DumpPages) {
        $lines = New-Object System.Collections.Generic.List[string]
        foreach ($p in $doc.Paragraphs) {
            $t = $p.Range.Text
            # Caption labels are "Figure"/"Table" in English and a single CJK glyph in
            # Chinese. Windows PowerShell 5.1 has no \u escape and reading non-ASCII
            # from this file is unreliable, so the glyph is identified by its code
            # point: U+56FE is the label for figures and U+8868 for tables.
            if ($t -match '^(\S+) ([0-9A-B]+\.[0-9]+)[ \t]') {
                $lab = $matches[1]
                $kind = $lab
                if ($lab -notmatch '^[A-Za-z]') {
                    switch ([int][char]$lab[0]) {
                        22270 { $kind = 'ZH_FIG' }
                        34920 { $kind = 'ZH_TAB' }
                        default { $kind = 'OTHER' }
                    }
                }
                if ($kind -ne 'OTHER') {
                    $lines.Add(($kind + "|" + $matches[2] + "|" + $p.Range.Information(3)))
                }
            }
        }
        $lines | Set-Content $DumpPages -Encoding UTF8
        ("captions dumped: " + $lines.Count) | Add-Content $log
    }

    # Body page range, without depending on the language of the headings: chapter 1
    # is the first numbered Heading 1, and the References section is the first
    # Heading 1 after the seventh numbered chapter.
    $first = 0; $last = 0; $numbered = 0
    foreach ($p in $doc.Paragraphs) {
        if ($p.OutlineLevel -ne 1) { continue }
        $t = $p.Range.Text.Trim()
        if ($t -match '^[0-9]+[ \t]+\S') {
            $numbered++
            if ($numbered -eq 1) { $first = $p.Range.Information(3) }
            continue
        }
        if ($numbered -ge 7 -and $last -eq 0) { $last = $p.Range.Information(3) }
    }
    if ($last -eq 0) { $last = $doc.ComputeStatistics(2) }
    ("body pages: chapter1Start=$first  referencesStart=$last  bodyCount=" + ($last - $first)) | Add-Content $log

    $doc.SaveAs2($Out, 17)
    "PDF written" | Add-Content $log
    $doc.Close(0)
    $doc = $null
    "RESULT: OK" | Add-Content $log
}
catch {
    ("RESULT: FAILED " + $_.Exception.Message) | Add-Content $log
    ("AT LINE " + $_.InvocationInfo.ScriptLineNumber) | Add-Content $log
}
finally {
    if ($doc -ne $null) { try { $doc.Close(0) } catch {} }
    if ($word -ne $null) { try { $word.Quit() } catch {} }
}

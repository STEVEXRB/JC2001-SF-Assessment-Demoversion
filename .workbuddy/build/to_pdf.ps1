param(
    [Parameter(Mandatory=$true)][string]$In,
    [Parameter(Mandatory=$true)][string]$Out
)

$log = Join-Path (Split-Path -Parent $PSCommandPath) "convert.log"
"=== convert $(Get-Date -Format s) ===" | Set-Content -Path $log -Encoding UTF8
"In : $In"  | Add-Content -Path $log
"Out: $Out" | Add-Content -Path $log

$ErrorActionPreference = "Continue"
$doc = $null
$word = $null

try {
    Add-Content -Path $log -Value "creating Word.Application"
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    Add-Content -Path $log -Value ("word version: " + $word.Version)

    $doc = $word.Documents.Open($In, $false, $true)
    Add-Content -Path $log -Value "opened document"

    for ($i = 1; $i -le 3; $i++) {
        $doc.Fields.Update() | Out-Null
        $n = 0
        foreach ($toc in $doc.TablesOfContents) { $toc.Update() | Out-Null; $n++ }
        $doc.Repaginate()
        Add-Content -Path $log -Value ("pass $i : fields updated, TOCs=$n, pages=" + $doc.ComputeStatistics(2))
    }

    if (Test-Path $Out) { Remove-Item $Out -Force }
    $doc.SaveAs2($Out, 17)
    Add-Content -Path $log -Value "saved pdf"
    $doc.Close(0)
    $doc = $null
    Add-Content -Path $log -Value "RESULT: OK"
}
catch {
    Add-Content -Path $log -Value ("RESULT: FAILED - " + $_.Exception.GetType().FullName)
    Add-Content -Path $log -Value ("MESSAGE: " + $_.Exception.Message)
    Add-Content -Path $log -Value ("STACK: " + $_.ScriptStackTrace)
}
finally {
    if ($doc -ne $null) { try { $doc.Close(0) } catch {} }
    if ($word -ne $null) { try { $word.Quit() } catch {} }
}
exit 0

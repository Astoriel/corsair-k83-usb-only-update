#requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('NXP', 'Nordic')]
    [string] $Stage,

    [Parameter(Mandatory)]
    [string] $Updater,

    [Parameter(Mandatory)]
    [string] $FirmwareDirectory,

    [string] $Python = 'python',
    [string] $Confirmation = '',
    [string] $LogDirectory = (Join-Path $PSScriptRoot '../runs')
)

$ErrorActionPreference = 'Stop'
$Stage = $Stage.ToUpperInvariant()
if ($Confirmation -and $Confirmation -cne "FLASH $Stage") {
    throw "Confirmation must be exactly FLASH $Stage"
}
if (Get-Process -Name 'iCUE', 'CorsairFWUpd', 'CorsairFwUpdMc' -ErrorAction SilentlyContinue) {
    throw 'Close iCUE and any updater before continuing.'
}
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot '../firmware/manifest.json') -Raw |
    ConvertFrom-Json
$imageEntry = $manifest.files | Where-Object { $_.stage -eq $Stage }
$image = (Resolve-Path -LiteralPath (Join-Path $FirmwareDirectory $imageEntry.name)).ProviderPath
$Updater = (Resolve-Path -LiteralPath $Updater).ProviderPath
if ((Get-FileHash -LiteralPath $image -Algorithm SHA256).Hash -ine $imageEntry.sha256 -or
    (Get-Item -LiteralPath $image).Length -ne $imageEntry.size) {
    throw 'The firmware image does not match this experiment.'
}
if ((Get-FileHash -LiteralPath $Updater -Algorithm SHA256).Hash -ine $manifest.updater.sha256 -or
    (Get-AuthenticodeSignature -LiteralPath $Updater).Status -ne 'Valid') {
    throw 'The original updater hash or signature does not match.'
}

$diagnostic = & $Python -I -B (Join-Path $PSScriptRoot 'inspect-hid.py')
if ($LASTEXITCODE -ne 0) { throw 'Read-only HID inspection failed.' }
$device = ($diagnostic -join [Environment]::NewLine) | ConvertFrom-Json
$inputChannel = @($device.collections | Where-Object {
    $_.vendor_id -eq 0x1B1C -and $_.product_id -eq 0x1B42 -and
    $_.usage_page -eq 0xFFC2 -and $_.usage -eq 3
})
$outputChannel = @($device.collections | Where-Object {
    $_.vendor_id -eq 0x1B1C -and $_.product_id -eq 0x1B42 -and
    $_.usage_page -eq 0xFFC2 -and $_.usage -eq 4
})
if ($inputChannel.Count -ne 1 -or $outputChannel.Count -ne 1) {
    throw 'Expected exactly one input channel and one output channel.'
}
$inputChannel = $inputChannel[0]
$outputChannel = $outputChannel[0]
$revision = if ($Stage -eq 'NXP') { '0313' } else { '0326' }
if (-not $inputChannel.usb_parent -or
    $inputChannel.usb_parent -ine $outputChannel.usb_parent -or
    $inputChannel.revision -ne $revision -or $outputChannel.revision -ne $revision -or
    $inputChannel.input_bytes -ne 64 -or $outputChannel.output_bytes -ne 65 -or
    $outputChannel.protocol -cne 'P05') {
    throw 'Parent, revision, report size or protocol differs from the recorded experiment.'
}
$arguments = @(
    '--usb-vid=1b1c', '--usb-pid=1b42', '--hid-up=ffc2',
    "--path=$($inputChannel.path.ToLowerInvariant())",
    "--path=$($outputChannel.path.ToLowerInvariant())",
    "--image=$image"
)
Write-Output $Updater
Write-Output $arguments
if (-not $Confirmation) {
    Write-Output 'Preflight passed. No updater process was started.'
    return
}
if (Get-Process -Name 'iCUE', 'CorsairFWUpd', 'CorsairFwUpdMc' -ErrorAction SilentlyContinue) {
    throw 'iCUE or an updater started during preflight.'
}

$runDirectory = Join-Path $LogDirectory ($Stage + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$null = [IO.Directory]::CreateDirectory($LogDirectory)
$null = New-Item -ItemType Directory -Path $runDirectory
$metadata = Join-Path $runDirectory 'run.log'
$diagnostic | Set-Content -LiteralPath (Join-Path $runDirectory 'hid-before.json')
@("Started: $((Get-Date).ToString('o'))", "Stage: $Stage", "Updater: $Updater", $arguments) |
    Set-Content -LiteralPath $metadata
$start = [Diagnostics.ProcessStartInfo]::new($Updater)
$start.WorkingDirectory = Split-Path -Parent $Updater
$start.UseShellExecute = $false
$start.RedirectStandardOutput = $true
$start.RedirectStandardError = $true
foreach ($argument in $arguments) { $start.ArgumentList.Add($argument) }
$process = [Diagnostics.Process]::new()
$process.StartInfo = $start
$stdout = $null
$stderr = $null
Write-Output "Private operation logs: $runDirectory"
try {
    $stdout = [IO.File]::Open((Join-Path $runDirectory 'stdout.log'), 'CreateNew', 'Write', 'Read')
    $stderr = [IO.File]::Open((Join-Path $runDirectory 'stderr.log'), 'CreateNew', 'Write', 'Read')
    if (-not $process.Start()) { throw 'The updater did not start.' }
    "PID: $($process.Id)" | Add-Content -LiteralPath $metadata
    $outTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
    $errTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
    $process.WaitForExit()
    $exitCode = $process.ExitCode
    "Exit code: $exitCode" | Add-Content -LiteralPath $metadata
    $null = $outTask.GetAwaiter().GetResult()
    $null = $errTask.GetAwaiter().GetResult()
    "Finished: $((Get-Date).ToString('o'))" | Add-Content -LiteralPath $metadata
} catch {
    "Launcher error: $_" | Add-Content -LiteralPath $metadata
    throw
} finally {
    if ($stdout) { $stdout.Dispose() }
    if ($stderr) { $stderr.Dispose() }
    $process.Dispose()
}
Write-Output "Updater exit code: $exitCode. Inspect logs and recheck HID before any next stage."
exit $exitCode

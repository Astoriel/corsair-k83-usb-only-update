#requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string] $FirmwareDirectory
)

$ErrorActionPreference = 'Stop'
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot '../firmware/manifest.json') -Raw |
    ConvertFrom-Json
foreach ($file in $manifest.files) {
    $path = Join-Path $FirmwareDirectory $file.name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing original file: $path"
    }
    if ((Get-Item -LiteralPath $path).Length -ne $file.size -or
        (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ine $file.sha256) {
        throw "Size or SHA-256 mismatch: $path"
    }
    Write-Output "Verified $($file.name)"
}

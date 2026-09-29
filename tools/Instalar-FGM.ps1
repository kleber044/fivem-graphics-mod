param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("install", "uninstall", "repair", "switch")]
    [string]$Command,
    [ValidateSet("quality", "performance")]
    [string]$Edition = "",
    [string]$FiveMRoot = "",
    [string]$PackageRoot = "",
    [string]$RuntimeDll = ""
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "fgm-install-lib.ps1")
try {
    Invoke-FgmCommand -Command $Command -Edition $Edition -FiveMRoot $FiveMRoot -PackageRoot $PackageRoot -RuntimeDll $RuntimeDll -ScriptRoot $PSScriptRoot
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    [Console]::Error.WriteLine($_.ScriptStackTrace)
    exit 1
}

param(
    [switch]$Installer
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
.\.venv\Scripts\pyinstaller.exe --noconfirm --clean --windowed --name EmployeeCheck --onefile run_employee_check.py

Write-Host "Built dist\EmployeeCheck.exe"

if ($Installer) {
    $Version = (& .\.venv\Scripts\python.exe -c "from employee_check import __version__; print(__version__)").Trim()
    $Iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    $IsccPath = $null
    if (-not $Iscc) {
        $KnownPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
        if (Test-Path $KnownPath) {
            $IsccPath = $KnownPath
        }
    } else {
        $IsccPath = $Iscc.Source
    }
    if (-not $IsccPath) {
        throw "Inno Setup compiler ISCC.exe was not found. Install Inno Setup 6 or run this through the GitHub release workflow."
    }

    New-Item -ItemType Directory -Force -Path "dist\installers" | Out-Null
    & $IsccPath /DAppVersion="$Version" /DRoleName="Employer" /DRoleArg="employer" /DOutputBaseFilename="EmployeeCheck-Windows-Employer-Setup" "installer\windows\EmployeeCheck.iss"
    & $IsccPath /DAppVersion="$Version" /DRoleName="Employee" /DRoleArg="employee" /DOutputBaseFilename="EmployeeCheck-Windows-Employee-Setup" "installer\windows\EmployeeCheck.iss"
    Write-Host "Built Windows installers in dist\installers"
}

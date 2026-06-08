# Employee Check full uninstall script.
# Version: __VERSION__

param(
    [switch]$NoPause
)

$ErrorActionPreference = "Continue"

function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-SelfElevated {
    if (Test-Administrator) {
        return
    }
    $arguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"", "-NoPause")
    Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -Verb RunAs | Out-Null
    exit
}

function Invoke-TempCopy {
    if ($env:EMPLOYEE_CHECK_UNINSTALL_COPY -eq "1") {
        return
    }
    if (-not $PSCommandPath -or -not (Test-Path -LiteralPath $PSCommandPath)) {
        return
    }
    $tempScript = Join-Path $env:TEMP ("EmployeeCheck-Full-Uninstall-{0}.ps1" -f ([Guid]::NewGuid()))
    Copy-Item -LiteralPath $PSCommandPath -Destination $tempScript -Force
    $env:EMPLOYEE_CHECK_UNINSTALL_COPY = "1"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $tempScript -NoPause
    $exitCode = $LASTEXITCODE
    Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
    exit $exitCode
}

function Remove-PathSafe {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) {
        return
    }
    $expanded = [Environment]::ExpandEnvironmentVariables($Path)
    if ($expanded -match "^[A-Za-z]:\\?$") {
        Write-Warning "Refusing to remove drive root: $expanded"
        return
    }
    if ($expanded -in @("\", "/", ".", "..")) {
        Write-Warning "Refusing to remove unsafe path: $expanded"
        return
    }
    if (Test-Path -LiteralPath $expanded) {
        Remove-Item -LiteralPath $expanded -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed $expanded"
    }
}

function Stop-EmployeeCheck {
    Write-Host "Stopping Employee Check processes..."
    & "$env:SystemRoot\System32\taskkill.exe" /IM EmployeeCheck.exe /F /T 2>$null | Out-Null
}

function Split-UninstallCommand {
    param([string]$Command)
    $command = $Command.Trim()
    if (-not $command) {
        return $null
    }
    if ($command.StartsWith('"')) {
        $end = $command.IndexOf('"', 1)
        if ($end -gt 1) {
            return @{
                File = $command.Substring(1, $end - 1)
                Args = $command.Substring($end + 1).Trim()
            }
        }
    }
    $space = $command.IndexOf(" ")
    if ($space -lt 1) {
        return @{
            File = $command
            Args = ""
        }
    }
    return @{
        File = $command.Substring(0, $space)
        Args = $command.Substring($space + 1).Trim()
    }
}

function Invoke-RegisteredUninstall {
    $roots = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall"
    )
    $names = @("Employee Check Employer", "Employee Check Employee")
    foreach ($root in $roots) {
        if (-not (Test-Path -LiteralPath $root)) {
            continue
        }
        Get-ChildItem -LiteralPath $root -ErrorAction SilentlyContinue | ForEach-Object {
            $item = Get-ItemProperty -LiteralPath $_.PSPath -ErrorAction SilentlyContinue
            if ($null -eq $item -or $item.DisplayName -notin $names) {
                return
            }
            $rawCommand = if ($item.QuietUninstallString) { $item.QuietUninstallString } else { $item.UninstallString }
            $parsed = Split-UninstallCommand $rawCommand
            if ($null -eq $parsed -or -not (Test-Path -LiteralPath $parsed.File)) {
                return
            }
            $args = $parsed.Args
            if ($args -notmatch "/VERYSILENT") {
                $args = "$args /VERYSILENT /SUPPRESSMSGBOXES /NORESTART"
            }
            Write-Host "Running registered uninstaller for $($item.DisplayName)..."
            Start-Process -FilePath $parsed.File -ArgumentList $args -Wait -WindowStyle Hidden -ErrorAction SilentlyContinue
        }
    }
}

function Remove-StartupEntries {
    Write-Host "Removing startup entries..."
    $runKeys = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    )
    foreach ($key in $runKeys) {
        if (Test-Path -LiteralPath $key) {
            Remove-ItemProperty -LiteralPath $key -Name "EmployeeCheckEmployer" -ErrorAction SilentlyContinue
            Remove-ItemProperty -LiteralPath $key -Name "EmployeeCheckEmployee" -ErrorAction SilentlyContinue
        }
    }
    $profiles = Get-LocalProfiles
    foreach ($profile in $profiles) {
        Remove-PathSafe (Join-Path $profile "AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\EmployeeCheck-employer.cmd")
        Remove-PathSafe (Join-Path $profile "AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\EmployeeCheck-employee.cmd")
    }
}

function Get-LocalProfiles {
    $paths = New-Object System.Collections.Generic.HashSet[string]
    try {
        Get-CimInstance Win32_UserProfile -ErrorAction SilentlyContinue |
            Where-Object { $_.LocalPath -and (Test-Path -LiteralPath $_.LocalPath) } |
            ForEach-Object { [void]$paths.Add($_.LocalPath) }
    } catch {
    }
    $usersRoot = Join-Path $env:SystemDrive "Users"
    if (Test-Path -LiteralPath $usersRoot) {
        Get-ChildItem -LiteralPath $usersRoot -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { [void]$paths.Add($_.FullName) }
    }
    return $paths
}

Invoke-SelfElevated
Invoke-TempCopy

Write-Host "Employee Check full uninstall v__VERSION__"
Stop-EmployeeCheck
Invoke-RegisteredUninstall
Start-Sleep -Seconds 1
Remove-StartupEntries

Write-Host "Removing installed files..."
Remove-PathSafe "$env:ProgramFiles\Employee Check Employer"
Remove-PathSafe "$env:ProgramFiles\Employee Check Employee"
if (${env:ProgramFiles(x86)}) {
    Remove-PathSafe "${env:ProgramFiles(x86)}\Employee Check Employer"
    Remove-PathSafe "${env:ProgramFiles(x86)}\Employee Check Employee"
}
Remove-PathSafe "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Employee Check"
Remove-PathSafe "$env:Public\Desktop\Employee Check Employer.lnk"
Remove-PathSafe "$env:Public\Desktop\Employee Check Employee.lnk"
Remove-PathSafe "$env:ProgramData\EmployeeCheck"

Write-Host "Removing user config, reports, and local database..."
foreach ($profile in Get-LocalProfiles) {
    Remove-PathSafe (Join-Path $profile "AppData\Roaming\EmployeeCheck")
    Remove-PathSafe (Join-Path $profile "AppData\Local\EmployeeCheck")
    Remove-PathSafe (Join-Path $profile "Desktop\Employee Check Employer.lnk")
    Remove-PathSafe (Join-Path $profile "Desktop\Employee Check Employee.lnk")
}

Write-Host "Employee Check has been removed from this machine."
if (-not $NoPause) {
    Read-Host "Press Enter to close"
}

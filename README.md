# Employee Check

Employee Check is a cross-platform desktop monitoring app for corporate LANs.
It has two roles:

- **Employer**: desktop dashboard, local database, daily Excel reports, LAN server.
- **Employee**: visible agent with Check In, Check Out, Lunch, and Meeting statuses.

Employee and employer machines do **not** need Python installed. Download the
installer/package for the correct role from GitHub Releases.

The app is intentionally visible to employees. It can be configured to start with
the machine using normal OS startup mechanisms, but it does not implement stealth
persistence or prevent administrators from stopping/removing it.

## Download

[![Windows Employer](https://img.shields.io/badge/Windows-Employer_Setup-2563eb?logo=windows)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Windows-Employer-Setup.exe)
[![Windows Employee](https://img.shields.io/badge/Windows-Employee_Setup-2563eb?logo=windows)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Windows-Employee-Setup.exe)
[![macOS Employer](https://img.shields.io/badge/macOS-Employer_DMG-111827?logo=apple)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-macOS-Employer.dmg)
[![macOS Employee](https://img.shields.io/badge/macOS-Employee_DMG-111827?logo=apple)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-macOS-Employee.dmg)
[![Linux Employer](https://img.shields.io/badge/Linux-Employer_DEB-f97316?logo=linux)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Linux-Employer-amd64.deb)
[![Linux Employee](https://img.shields.io/badge/Linux-Employee_DEB-f97316?logo=linux)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Linux-Employee-amd64.deb)

| Platform | Employer machine | Employee machines |
| --- | --- | --- |
| Windows | `EmployeeCheck-Windows-Employer-Setup.exe` | `EmployeeCheck-Windows-Employee-Setup.exe` |
| macOS | `EmployeeCheck-macOS-Employer.dmg` | `EmployeeCheck-macOS-Employee.dmg` |
| Linux Debian/Ubuntu | `EmployeeCheck-Linux-Employer-amd64.deb` | `EmployeeCheck-Linux-Employee-amd64.deb` |

## Features

- Live LAN status updates without accounts or cloud services.
- Open process/app list.
- Active app and active window title.
- Idle detection with bands:
  - active: under 2 minutes
  - yellow: 2 minutes or more
  - orange: 5 minutes or more
  - red: 10 minutes or more
- Employee manual statuses: checked in, checked out, lunch, meeting.
- Employer report hour and data-retention settings.
- Daily Excel summary per employee.
- Startup behavior for Windows, macOS, and Linux.

## Limitations

Website URLs and Adobe project/document names are usually exposed through active
window titles. Some browsers and macOS can expose the current URL if the user has
granted automation permissions. Linux active-window data depends on desktop tools
such as `xdotool`, `xprop`, and `xprintidle`, and is less reliable on Wayland.

Unsigned Windows/macOS builds may show operating-system security warnings. For
company rollout, sign and notarize the release artifacts through your normal IT
process.

## Setup

1. Install the **Employer** package on the manager machine first.
2. Start Employee Check Employer. The first run asks for daily report hour and
   data-retention days.
3. Install the **Employee** package on each employee machine.
4. Start Employee Check Employee and enter the employee name. The app tries to
   find the employer machine automatically on the LAN; if discovery fails, enter
   the employer IP/hostname manually.

Windows installers and Linux DEB packages install startup entries for their
selected role. On macOS, launch the app once and use **Install Startup** in the
app window to create the LaunchAgent entry.

## GitHub Releases

The included GitHub Actions workflow builds all release files automatically.

1. Push this project to GitHub.
2. Create and push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow publishes these release assets:

- `EmployeeCheck-Windows-Employer-Setup.exe`
- `EmployeeCheck-Windows-Employee-Setup.exe`
- `EmployeeCheck-macOS-Employer.dmg`
- `EmployeeCheck-macOS-Employee.dmg`
- `EmployeeCheck-Linux-Employer-amd64.deb`
- `EmployeeCheck-Linux-Employee-amd64.deb`

## Developer Build

Python is only needed on developer/build machines.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Build a Windows portable executable:

```powershell
.\scripts\build.ps1
```

Build Windows setup installers. Requires Inno Setup 6:

```powershell
.\scripts\build.ps1 -Installer
```

Build macOS DMGs on macOS:

```bash
bash scripts/build_macos.sh
```

Build Linux DEB packages on Linux:

```bash
bash scripts/build_linux.sh
```

For true admin-managed deployment, package and deploy the app through normal IT
controls such as Group Policy, MDM, Jamf, Intune, or system-level services.

## Portable Commands

Portable builds can still run with explicit role arguments:

```text
EmployeeCheck employer
EmployeeCheck employee
```

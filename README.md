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

Latest release page:
https://github.com/artenisalija/employee-check/releases/latest

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

Direct download links:

- Windows Employer: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Windows-Employer-Setup.exe
- Windows Employee: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Windows-Employee-Setup.exe
- Linux Employer: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Linux-Employer-amd64.deb
- Linux Employee: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Linux-Employee-amd64.deb
- macOS Employer: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-macOS-Employer.dmg
- macOS Employee: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-macOS-Employee.dmg

## Install

### Windows

Manager/employer computer:

1. Download `EmployeeCheck-Windows-Employer-Setup.exe`.
2. Right-click the file and choose **Run as administrator**.
3. Complete the installer.
4. Start **Employee Check Employer** from the Start menu or desktop shortcut.
5. On first run, choose the daily Excel report hour and data-retention days.

Employee computer:

1. Download `EmployeeCheck-Windows-Employee-Setup.exe`.
2. Right-click the file and choose **Run as administrator**.
3. Complete the installer.
4. Start **Employee Check Employee**.
5. Enter the employee name. If auto-discovery does not find the employer machine,
   enter the manager computer IP address or hostname manually.

The Windows installers add startup entries automatically.

### Linux Debian/Ubuntu

Manager/employer computer:

```bash
wget https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Linux-Employer-amd64.deb
sudo apt install ./EmployeeCheck-Linux-Employer-amd64.deb
```

Employee computer:

```bash
wget https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Linux-Employee-amd64.deb
sudo apt install ./EmployeeCheck-Linux-Employee-amd64.deb
```

After installing, launch the app from the desktop application menu:

- Manager: **Employee Check Employer**
- Employee: **Employee Check Employee**

The Linux DEB packages add desktop startup entries automatically. Active-window
and idle detection work best on X11. On Linux, install these optional tools for
better detection:

```bash
sudo apt install xdotool xprintidle
```

### macOS

Manager/employer computer:

1. Download `EmployeeCheck-macOS-Employer.dmg`.
2. Open the DMG and launch **Employee Check Employer**.
3. If macOS blocks the app because it is unsigned, open **System Settings >
   Privacy & Security** and allow it.
4. Use **Install Startup** inside the app if you want it to start with the Mac.

Employee computer:

1. Download `EmployeeCheck-macOS-Employee.dmg`.
2. Open the DMG and launch **Employee Check Employee**.
3. Enter the employee name and employer machine address if auto-discovery fails.
4. Use **Install Startup** inside the app if you want it to start with the Mac.

macOS may ask for Accessibility or Automation permissions before active-window
titles or browser URLs are visible.

## Quick Test

For a first test with one Windows manager PC and one Linux employee machine:

1. Install the Windows Employer setup file on the manager PC.
2. Start **Employee Check Employer** and leave it running.
3. Install the Linux Employee DEB on the Linux machine:

```bash
wget https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-Linux-Employee-amd64.deb
sudo apt install ./EmployeeCheck-Linux-Employee-amd64.deb
```

4. Start **Employee Check Employee** on Linux.
5. Enter the employee name.
6. If auto-discovery fails, enter the Windows manager PC IP address.
7. Confirm the Linux employee appears in the Windows employer dashboard.

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

## Setup Notes

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

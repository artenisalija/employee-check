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

[![Windows Employer](https://img.shields.io/badge/Windows-Employer_Setup-2563eb?logo=windows)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Windows-Employer-Setup.exe)
[![Windows Employee](https://img.shields.io/badge/Windows-Employee_Setup-2563eb?logo=windows)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Windows-Employee-Setup.exe)
[![macOS Employer](https://img.shields.io/badge/macOS-Employer_DMG-111827?logo=apple)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-macOS-Employer.dmg)
[![macOS Employee](https://img.shields.io/badge/macOS-Employee_DMG-111827?logo=apple)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-macOS-Employee.dmg)
[![Linux Employer](https://img.shields.io/badge/Linux-Employer_DEB-f97316?logo=linux)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-amd64.deb)
[![Linux Employee](https://img.shields.io/badge/Linux-Employee_DEB-f97316?logo=linux)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-amd64.deb)
[![Linux Employer tar.gz](https://img.shields.io/badge/Linux-Employer_tar.gz-16a34a?logo=linux)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz)
[![Linux Employee tar.gz](https://img.shields.io/badge/Linux-Employee_tar.gz-16a34a?logo=linux)](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz)

| Platform | Employer machine | Employee machines |
| --- | --- | --- |
| Windows | `EmployeeCheck-v0.1.4-Windows-Employer-Setup.exe` | `EmployeeCheck-v0.1.4-Windows-Employee-Setup.exe` |
| macOS | `EmployeeCheck-v0.1.4-macOS-Employer.dmg` | `EmployeeCheck-v0.1.4-macOS-Employee.dmg` |
| Linux Debian/Ubuntu | `EmployeeCheck-v0.1.4-Linux-Employer-amd64.deb` | `EmployeeCheck-v0.1.4-Linux-Employee-amd64.deb` |
| Other Linux x86_64 | `EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz` | `EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz` |

Direct download links:

- Windows Employer: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Windows-Employer-Setup.exe
- Windows Employee: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Windows-Employee-Setup.exe
- Linux Employer: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-amd64.deb
- Linux Employee: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-amd64.deb
- Linux Employer tar.gz: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz
- Linux Employee tar.gz: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
- macOS Employer: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-macOS-Employer.dmg
- macOS Employee: https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-macOS-Employee.dmg

## Install

### Windows

Manager/employer computer:

1. Download `EmployeeCheck-v0.1.4-Windows-Employer-Setup.exe`.
2. Right-click the file and choose **Run as administrator**.
3. Complete the installer.
4. Start **Employee Check Employer** from the Start menu or desktop shortcut.
5. On first run, choose the daily Excel report hour and data-retention days.

Employee computer:

1. Download `EmployeeCheck-v0.1.4-Windows-Employee-Setup.exe`.
2. Right-click the file and choose **Run as administrator**.
3. Complete the installer.
4. Start **Employee Check Employee**.
5. Enter the employee name. If auto-discovery does not find the employer machine,
   enter the manager computer IP address or hostname manually.

The Windows installers add startup entries automatically.

Updating on Windows:

1. Download the newest setup file for the same role.
2. Right-click it and choose **Run as administrator**.
3. The setup stops running Employee Check processes, removes the previous
   install for that role, clears old files from the install folder, and installs
   the new version.

### Linux Debian/Ubuntu

Manager/employer computer:

```bash
wget https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-amd64.deb
sudo apt install ./EmployeeCheck-v0.1.4-Linux-Employer-amd64.deb
```

Employee computer:

```bash
wget https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-amd64.deb
sudo apt install ./EmployeeCheck-v0.1.4-Linux-Employee-amd64.deb
```

### Fedora/RHEL/Rocky Linux

Manager/employer computer:

```bash
curl -L -o EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz
tar -xzf EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz
sudo ./EmployeeCheck-v0.1.4-Linux-Employer-x86_64/install.sh
```

Employee computer:

```bash
curl -L -o EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
tar -xzf EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
sudo ./EmployeeCheck-v0.1.4-Linux-Employee-x86_64/install.sh
```

Optional X11 idle/window helpers:

```bash
sudo dnf install xdotool xprintidle
```

### openSUSE

Manager/employer computer:

```bash
curl -L -o EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz
tar -xzf EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz
sudo ./EmployeeCheck-v0.1.4-Linux-Employer-x86_64/install.sh
```

Employee computer:

```bash
curl -L -o EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
tar -xzf EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
sudo ./EmployeeCheck-v0.1.4-Linux-Employee-x86_64/install.sh
```

Optional X11 idle/window helpers:

```bash
sudo zypper install xdotool xprintidle
```

### Arch Linux/Manjaro

Manager/employer computer:

```bash
curl -L -o EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz
tar -xzf EmployeeCheck-v0.1.4-Linux-Employer-x86_64.tar.gz
sudo ./EmployeeCheck-v0.1.4-Linux-Employer-x86_64/install.sh
```

Employee computer:

```bash
curl -L -o EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
tar -xzf EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
sudo ./EmployeeCheck-v0.1.4-Linux-Employee-x86_64/install.sh
```

Optional X11 idle/window helpers:

```bash
sudo pacman -S xdotool xprintidle
```

### Generic Linux x86_64

Use the same `.tar.gz` package for any other x86_64 desktop Linux distro:

```bash
curl -L -o EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
tar -xzf EmployeeCheck-v0.1.4-Linux-Employee-x86_64.tar.gz
sudo ./EmployeeCheck-v0.1.4-Linux-Employee-x86_64/install.sh
```

After installing, launch the app from the desktop application menu:

- Manager: **Employee Check Employer**
- Employee: **Employee Check Employee**

The Linux DEB and tar.gz installers add desktop startup entries automatically.
When installing an update, the package/install script stops the old role process
and replaces the old role binary, desktop entry, and startup entry before copying
the new version.
Active-window and idle detection work best on X11. On Debian/Ubuntu, install
these optional tools for better detection:

```bash
sudo apt install xdotool xprintidle
```

### macOS

Manager/employer computer:

1. Download `EmployeeCheck-v0.1.4-macOS-Employer.dmg`.
2. Open the DMG and launch **Employee Check Employer**.
3. If macOS blocks the app because it is unsigned, open **System Settings >
   Privacy & Security** and allow it.
4. Use **Install Startup** inside the app if you want it to start with the Mac.

Employee computer:

1. Download `EmployeeCheck-v0.1.4-macOS-Employee.dmg`.
2. Open the DMG and launch **Employee Check Employee**.
3. Enter the employee name and employer machine address if auto-discovery fails.
4. Use **Install Startup** inside the app if you want it to start with the Mac.

macOS may ask for Accessibility or Automation permissions before active-window
titles or browser URLs are visible.

Updating on macOS:

1. Download the newest DMG for the same role.
2. Quit the running Employee Check app.
3. Open the new DMG and launch the app from it, or replace the old app bundle if
   you copied it locally.

## Quick Test

For a first test with one Windows manager PC and one Linux employee machine:

1. Install the Windows Employer setup file on the manager PC.
2. Start **Employee Check Employer** and leave it running.
3. Install the Linux Employee DEB on the Linux machine:

```bash
wget https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.4-Linux-Employee-amd64.deb
sudo apt install ./EmployeeCheck-v0.1.4-Linux-Employee-amd64.deb
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
git tag vX.Y.Z
git push origin vX.Y.Z
```

The workflow publishes these release assets:

- `EmployeeCheck-vX.Y.Z-Windows-Employer-Setup.exe`
- `EmployeeCheck-vX.Y.Z-Windows-Employee-Setup.exe`
- `EmployeeCheck-vX.Y.Z-macOS-Employer.dmg`
- `EmployeeCheck-vX.Y.Z-macOS-Employee.dmg`
- `EmployeeCheck-vX.Y.Z-Linux-Employer-amd64.deb`
- `EmployeeCheck-vX.Y.Z-Linux-Employee-amd64.deb`
- `EmployeeCheck-vX.Y.Z-Linux-Employer-x86_64.tar.gz`
- `EmployeeCheck-vX.Y.Z-Linux-Employee-x86_64.tar.gz`

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

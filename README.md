# Employee Check

Employee Check is a visible cross-platform desktop monitoring app for corporate
LANs. It has two roles:

- **Employer**: manager dashboard, LAN server, local database, daily Excel reports.
- **Employee**: tray/menu agent with Check In, Check Out, Lunch, and Meeting.

Employees and managers do **not** need Python installed. Download the installer
or package for the correct role from GitHub Releases.

Latest release:
https://github.com/artenisalija/employee-check/releases/latest

## Downloads

Current documented version: `v0.1.6`

| Platform | Employer | Employee |
| --- | --- | --- |
| Windows | [Employer setup](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Windows-Employer-Setup.exe) | [Employee setup](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Windows-Employee-Setup.exe) |
| macOS | [Employer DMG](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-macOS-Employer.dmg) | [Employee DMG](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-macOS-Employee.dmg) |
| Debian/Ubuntu | [Employer DEB](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Linux-Employer-amd64.deb) | [Employee DEB](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Linux-Employee-amd64.deb) |
| Other Linux x86_64 | [Employer tar.gz](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Linux-Employer-x86_64.tar.gz) | [Employee tar.gz](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Linux-Employee-x86_64.tar.gz) |

Full uninstall files:

| Platform | Full wipe file |
| --- | --- |
| Windows | [EmployeeCheck-v0.1.6-Windows-Full-Uninstall.ps1](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Windows-Full-Uninstall.ps1) |
| macOS | [EmployeeCheck-v0.1.6-macOS-Full-Uninstall.sh](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-macOS-Full-Uninstall.sh) |
| Linux | [EmployeeCheck-v0.1.6-Linux-Full-Uninstall.sh](https://github.com/artenisalija/employee-check/releases/latest/download/EmployeeCheck-v0.1.6-Linux-Full-Uninstall.sh) |

## Quick Start

1. Install the **Employer** app on the manager computer first.
2. Start **Employee Check Employer** and choose the daily Excel report hour.
3. Install the **Employee** app on each employee computer.
4. Start **Employee Check Employee** and enter the employee name.
5. If LAN discovery fails, enter the manager computer IP address or hostname.

Use **Check Updates** to open the latest release page. Use **About** in the app
or tray menu to see the installed version.

## Install

### Windows

1. Download the correct setup file from the table above.
2. Right-click it and choose **Run as administrator**.
3. Complete the installer.
4. Start **Employee Check Employer** or **Employee Check Employee**.

Windows installers add startup entries automatically.

### macOS

1. Download the correct DMG from the table above.
2. Open the DMG and launch the app.
3. If macOS blocks the unsigned app, open **System Settings > Privacy & Security**
   and allow it.
4. Use **Install Startup** inside the app if it should start with the Mac.

macOS may ask for Accessibility or Automation permissions before active-window
titles or browser URLs are visible.

### Debian/Ubuntu

Set `ROLE` to `Employer` or `Employee`:

```bash
VERSION=0.1.6
ROLE=Employee
PACKAGE="EmployeeCheck-v${VERSION}-Linux-${ROLE}-amd64.deb"
wget "https://github.com/artenisalija/employee-check/releases/latest/download/${PACKAGE}"
sudo apt install "./${PACKAGE}"
```

Optional helpers for better X11 idle/window detection:

```bash
sudo apt install xdotool xprintidle
```

### Fedora/RHEL/Rocky Linux

```bash
VERSION=0.1.6
ROLE=Employee
PACKAGE="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64.tar.gz"
FOLDER="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64"
curl -L -o "${PACKAGE}" "https://github.com/artenisalija/employee-check/releases/latest/download/${PACKAGE}"
tar -xzf "${PACKAGE}"
sudo "./${FOLDER}/install.sh"
sudo dnf install xdotool xprintidle
```

### openSUSE

```bash
VERSION=0.1.6
ROLE=Employee
PACKAGE="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64.tar.gz"
FOLDER="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64"
curl -L -o "${PACKAGE}" "https://github.com/artenisalija/employee-check/releases/latest/download/${PACKAGE}"
tar -xzf "${PACKAGE}"
sudo "./${FOLDER}/install.sh"
sudo zypper install xdotool xprintidle
```

### Arch Linux/Manjaro

```bash
VERSION=0.1.6
ROLE=Employee
PACKAGE="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64.tar.gz"
FOLDER="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64"
curl -L -o "${PACKAGE}" "https://github.com/artenisalija/employee-check/releases/latest/download/${PACKAGE}"
tar -xzf "${PACKAGE}"
sudo "./${FOLDER}/install.sh"
sudo pacman -S xdotool xprintidle
```

### Generic Linux x86_64

```bash
VERSION=0.1.6
ROLE=Employee
PACKAGE="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64.tar.gz"
FOLDER="EmployeeCheck-v${VERSION}-Linux-${ROLE}-x86_64"
curl -L -o "${PACKAGE}" "https://github.com/artenisalija/employee-check/releases/latest/download/${PACKAGE}"
tar -xzf "${PACKAGE}"
sudo "./${FOLDER}/install.sh"
```

Linux packages and tar installers add desktop startup entries automatically.
The tar installer also prints the installed full-uninstall command.

## Update

Windows:

1. Download the newest setup file for the same role.
2. Right-click it and choose **Run as administrator**.
3. The setup stops Employee Check, removes the old same-role install, clears old
   files, and installs the new version.

Linux:

- DEB updates can be installed with `sudo apt install ./new-file.deb`.
- Tar updates can be installed by extracting the new tarball and running
  `sudo ./install.sh` again.
- Both update paths stop the old role process and replace old startup entries.

macOS:

1. Download the newest DMG for the same role.
2. Quit the running app.
3. Open the new DMG and launch the app, or replace the copied app bundle.

## Full Uninstall

The full uninstall files are destructive by design. They remove Employee Check,
startup entries, settings, the employer SQLite database, and generated Excel
reports from local user profiles.

### Windows Full Wipe

Download the Windows full uninstall file from the table above, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\EmployeeCheck-v0.1.6-Windows-Full-Uninstall.ps1
```

The script relaunches as administrator if needed.

### macOS Full Wipe

```bash
VERSION=0.1.6
SCRIPT="EmployeeCheck-v${VERSION}-macOS-Full-Uninstall.sh"
curl -L -o "${SCRIPT}" "https://github.com/artenisalija/employee-check/releases/latest/download/${SCRIPT}"
sudo bash "${SCRIPT}"
```

### Linux Full Wipe

Debian/Ubuntu:

```bash
VERSION=0.1.6
SCRIPT="EmployeeCheck-v${VERSION}-Linux-Full-Uninstall.sh"
curl -L -o "${SCRIPT}" "https://github.com/artenisalija/employee-check/releases/latest/download/${SCRIPT}"
sudo bash "${SCRIPT}"
```

Fedora/RHEL/Rocky Linux:

```bash
VERSION=0.1.6
SCRIPT="EmployeeCheck-v${VERSION}-Linux-Full-Uninstall.sh"
curl -L -o "${SCRIPT}" "https://github.com/artenisalija/employee-check/releases/latest/download/${SCRIPT}"
sudo bash "${SCRIPT}"
```

openSUSE:

```bash
VERSION=0.1.6
SCRIPT="EmployeeCheck-v${VERSION}-Linux-Full-Uninstall.sh"
curl -L -o "${SCRIPT}" "https://github.com/artenisalija/employee-check/releases/latest/download/${SCRIPT}"
sudo bash "${SCRIPT}"
```

Arch Linux/Manjaro:

```bash
VERSION=0.1.6
SCRIPT="EmployeeCheck-v${VERSION}-Linux-Full-Uninstall.sh"
curl -L -o "${SCRIPT}" "https://github.com/artenisalija/employee-check/releases/latest/download/${SCRIPT}"
sudo bash "${SCRIPT}"
```

Generic Linux x86_64:

```bash
VERSION=0.1.6
SCRIPT="EmployeeCheck-v${VERSION}-Linux-Full-Uninstall.sh"
curl -L -o "${SCRIPT}" "https://github.com/artenisalija/employee-check/releases/latest/download/${SCRIPT}"
sudo bash "${SCRIPT}"
```

If version `v0.1.6` or newer is already installed on Linux, you can also run the
role command installed with the package:

```bash
sudo employee-check-uninstall-employee
sudo employee-check-uninstall-employer
```

Either command wipes both roles from that machine.

## Features

- Live LAN status updates without accounts or cloud services.
- Open process/app list.
- Active app and active window title.
- Idle bands: active under 2 minutes, yellow at 2 minutes, orange at 5 minutes,
  red at 10 minutes.
- Employee statuses: checked in, checked out, lunch, meeting.
- Idle tracking pauses during lunch and meeting; reports count those durations
  as lunch/meeting time instead of idle time.
- Current status time and per-status minutes.
- Employer report hour and data-retention settings.
- Daily Excel summaries per employee.
- Visible tray/menu app with **Check Updates** and **About**.

## Limitations

Website URLs and Adobe project/document names are usually exposed through active
window titles. Some browsers and macOS can expose the current URL if the user
grants automation permissions.

Linux active-window data works best on X11 with `xdotool`, `xprop`, and
`xprintidle`. Wayland sessions can limit what the app can see.

Unsigned Windows/macOS builds may show operating-system security warnings. For
company rollout, sign and notarize the release artifacts through normal IT tools.

## Developer Build

Python is only needed on developer/build machines.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Build Windows:

```powershell
.\scripts\build.ps1
.\scripts\build.ps1 -Installer
```

Build macOS:

```bash
bash scripts/build_macos.sh
```

Build Linux:

```bash
bash scripts/build_linux.sh
```

Portable builds can run with explicit role arguments:

```text
EmployeeCheck employer
EmployeeCheck employee
```

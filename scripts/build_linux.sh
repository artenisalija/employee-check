#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt pyinstaller

VERSION="$(
  .venv/bin/python - <<'PY'
from employee_check import __version__
print(__version__)
PY
)"

rm -rf build dist
mkdir -p dist

.venv/bin/pyinstaller --noconfirm --clean --windowed --name EmployeeCheckEmployer --onefile run_employee_check_employer.py
.venv/bin/pyinstaller --noconfirm --clean --windowed --name EmployeeCheckEmployee --onefile run_employee_check_employee.py

build_tar() {
  local role_arg="$1"
  local role_name="$2"
  local exe_name="$3"
  local folder_name="EmployeeCheck-v${VERSION}-Linux-${role_name}-x86_64"
  local package_root="build/${folder_name}"
  local command_name="employee-check-${role_arg}"
  local desktop_id="employee-check-${role_arg}"

  rm -rf "$package_root"
  mkdir -p "$package_root"
  cp "dist/${exe_name}" "$package_root/${exe_name}"
  chmod 755 "$package_root/${exe_name}"

  cat > "$package_root/install.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail

if [ "\${EUID}" -ne 0 ]; then
  exec sudo "\$0" "\$@"
fi

SOURCE_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/employee-check"
EXE_NAME="${exe_name}"
ROLE_NAME="${role_name}"
COMMAND_NAME="${command_name}"
DESKTOP_ID="${desktop_id}"

mkdir -p "\${INSTALL_DIR}"
pkill -x "\${EXE_NAME}" 2>/dev/null || true
pkill -f "\${INSTALL_DIR}/\${EXE_NAME}" 2>/dev/null || true
rm -f "\${INSTALL_DIR}/\${EXE_NAME}"
rm -f "/usr/local/bin/\${COMMAND_NAME}"
rm -f "/usr/share/applications/\${DESKTOP_ID}.desktop"
rm -f "/etc/xdg/autostart/\${DESKTOP_ID}.desktop"
install -m 755 "\${SOURCE_DIR}/\${EXE_NAME}" "\${INSTALL_DIR}/\${EXE_NAME}"
ln -sf "\${INSTALL_DIR}/\${EXE_NAME}" "/usr/local/bin/\${COMMAND_NAME}"

mkdir -p /usr/share/applications /etc/xdg/autostart
cat > "/usr/share/applications/\${DESKTOP_ID}.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Employee Check \${ROLE_NAME}
Exec=\${INSTALL_DIR}/\${EXE_NAME}
Terminal=false
Categories=Office;Utility;
DESKTOP

cp "/usr/share/applications/\${DESKTOP_ID}.desktop" "/etc/xdg/autostart/\${DESKTOP_ID}.desktop"
echo "Installed Employee Check \${ROLE_NAME}."
echo "Run it from the application menu or with: \${COMMAND_NAME}"
EOF
  chmod 755 "$package_root/install.sh"

  tar -C build -czf "dist/${folder_name}.tar.gz" "$folder_name"
}

build_deb() {
  local role_arg="$1"
  local role_name="$2"
  local exe_name="$3"
  local package_name="employee-check-${role_arg}"
  local package_root="build/deb-${role_arg}"
  local output_name="EmployeeCheck-v${VERSION}-Linux-${role_name}-amd64.deb"

  rm -rf "$package_root"
  mkdir -p "$package_root/DEBIAN"
  mkdir -p "$package_root/opt/employee-check"
  mkdir -p "$package_root/usr/share/applications"
  mkdir -p "$package_root/etc/xdg/autostart"

  cp "dist/${exe_name}" "$package_root/opt/employee-check/${exe_name}"
  chmod 755 "$package_root/opt/employee-check/${exe_name}"

  cat > "$package_root/DEBIAN/control" <<EOF
Package: ${package_name}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Employee Check
Description: Employee Check ${role_name} desktop app
EOF

  cat > "$package_root/DEBIAN/preinst" <<EOF
#!/usr/bin/env sh
set -e
pkill -x "${exe_name}" 2>/dev/null || true
pkill -f "/opt/employee-check/${exe_name}" 2>/dev/null || true
rm -f "/opt/employee-check/${exe_name}"
rm -f "/usr/local/bin/employee-check-${role_arg}"
rm -f "/usr/share/applications/employee-check-${role_arg}.desktop"
rm -f "/etc/xdg/autostart/employee-check-${role_arg}.desktop"
exit 0
EOF
  chmod 755 "$package_root/DEBIAN/preinst"

  cat > "$package_root/DEBIAN/prerm" <<EOF
#!/usr/bin/env sh
set -e
if [ "\$1" = "remove" ] || [ "\$1" = "deconfigure" ] || [ "\$1" = "upgrade" ]; then
  pkill -x "${exe_name}" 2>/dev/null || true
  pkill -f "/opt/employee-check/${exe_name}" 2>/dev/null || true
fi
exit 0
EOF
  chmod 755 "$package_root/DEBIAN/prerm"

  cat > "$package_root/usr/share/applications/employee-check-${role_arg}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Employee Check ${role_name}
Exec=/opt/employee-check/${exe_name}
Terminal=false
Categories=Office;Utility;
EOF

  cp "$package_root/usr/share/applications/employee-check-${role_arg}.desktop" "$package_root/etc/xdg/autostart/employee-check-${role_arg}.desktop"

  dpkg-deb --build "$package_root" "dist/${output_name}"
}

build_deb "employer" "Employer" "EmployeeCheckEmployer"
build_deb "employee" "Employee" "EmployeeCheckEmployee"
build_tar "employer" "Employer" "EmployeeCheckEmployer"
build_tar "employee" "Employee" "EmployeeCheckEmployee"

echo "Built Linux DEB and tar.gz packages in dist/"

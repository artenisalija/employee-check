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

build_deb() {
  local role_arg="$1"
  local role_name="$2"
  local exe_name="$3"
  local package_name="employee-check-${role_arg}"
  local package_root="build/deb-${role_arg}"
  local output_name="EmployeeCheck-Linux-${role_name}-amd64.deb"

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

echo "Built Linux DEB packages in dist/"

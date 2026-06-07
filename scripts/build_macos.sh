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
hdiutil create -volname "Employee Check Employer" -srcfolder "dist/EmployeeCheckEmployer.app" -ov -format UDZO "dist/EmployeeCheck-v${VERSION}-macOS-Employer.dmg"

.venv/bin/pyinstaller --noconfirm --clean --windowed --name EmployeeCheckEmployee --onefile run_employee_check_employee.py
hdiutil create -volname "Employee Check Employee" -srcfolder "dist/EmployeeCheckEmployee.app" -ov -format UDZO "dist/EmployeeCheck-v${VERSION}-macOS-Employee.dmg"

echo "Built macOS DMGs in dist/"

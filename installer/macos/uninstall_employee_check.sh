#!/usr/bin/env bash
set -euo pipefail

VERSION="__VERSION__"

if [ "${EMPLOYEE_CHECK_UNINSTALL_COPY:-}" != "1" ]; then
  temp_script="/tmp/employee-check-macos-full-uninstall-$$.sh"
  cp "$0" "$temp_script"
  chmod 700 "$temp_script"
  exec env EMPLOYEE_CHECK_UNINSTALL_COPY=1 "$temp_script" "$@"
fi

if [ "$(id -u)" -ne 0 ]; then
  exec sudo -E bash "$0" "$@"
fi

trap 'rm -f "$0" 2>/dev/null || true' EXIT

remove_path() {
  for target in "$@"; do
    if [ -z "${target}" ] || [ "${target}" = "/" ] || [ "${target}" = "." ] || [ "${target}" = ".." ]; then
      echo "Refusing to remove unsafe path: ${target}" >&2
      continue
    fi
    if [ -e "${target}" ] || [ -L "${target}" ]; then
      rm -rf -- "${target}"
      echo "Removed ${target}"
    fi
  done
}

remove_user_files() {
  home_dir="$1"
  remove_path \
    "${home_dir}/Library/Application Support/EmployeeCheck" \
    "${home_dir}/Library/LaunchAgents/com.employeecheck.agent.employer.plist" \
    "${home_dir}/Library/LaunchAgents/com.employeecheck.agent.employee.plist"
}

echo "Employee Check full uninstall v${VERSION}"
echo "Stopping Employee Check processes..."
pkill -f "EmployeeCheckEmployer" 2>/dev/null || true
pkill -f "EmployeeCheckEmployee" 2>/dev/null || true
pkill -f "Employee Check Employer" 2>/dev/null || true
pkill -f "Employee Check Employee" 2>/dev/null || true

echo "Removing app bundles and launch agents..."
remove_path \
  "/Applications/EmployeeCheckEmployer.app" \
  "/Applications/EmployeeCheckEmployee.app" \
  "/Applications/Employee Check Employer.app" \
  "/Applications/Employee Check Employee.app" \
  "/Library/Application Support/EmployeeCheck" \
  "/Library/LaunchAgents/com.employeecheck.agent.employer.plist" \
  "/Library/LaunchAgents/com.employeecheck.agent.employee.plist"

echo "Removing user config, reports, local database, and startup entries..."
remove_user_files "/var/root"
for home_dir in /Users/*; do
  [ -d "${home_dir}" ] || continue
  remove_user_files "${home_dir}"
done

echo "Employee Check has been removed from this Mac."

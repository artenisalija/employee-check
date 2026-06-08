#!/usr/bin/env bash
set -euo pipefail

VERSION="__VERSION__"

if [ "${EMPLOYEE_CHECK_UNINSTALL_COPY:-}" != "1" ]; then
  temp_script="/tmp/employee-check-full-uninstall-$$.sh"
  cp "$0" "$temp_script"
  chmod 700 "$temp_script"
  exec env EMPLOYEE_CHECK_UNINSTALL_COPY=1 "$temp_script" "$@"
fi

if [ "${EUID}" -ne 0 ]; then
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

purge_deb_package() {
  package_name="$1"
  if command -v dpkg-query >/dev/null 2>&1 && dpkg-query -W -f='${Status}' "${package_name}" 2>/dev/null | grep -q "install ok installed"; then
    echo "Purging ${package_name}..."
    dpkg --purge "${package_name}" >/dev/null 2>&1 || true
  fi
}

remove_user_files() {
  home_dir="$1"
  remove_path \
    "${home_dir}/.config/EmployeeCheck" \
    "${home_dir}/.local/share/EmployeeCheck" \
    "${home_dir}/.config/autostart/employee-check-employer.desktop" \
    "${home_dir}/.config/autostart/employee-check-employee.desktop" \
    "${home_dir}/.config/systemd/user/employee-check-employer.service" \
    "${home_dir}/.config/systemd/user/employee-check-employee.service"
}

echo "Employee Check full uninstall v${VERSION}"
echo "Stopping Employee Check processes..."
pkill -x EmployeeCheckEmployer 2>/dev/null || true
pkill -x EmployeeCheckEmployee 2>/dev/null || true
pkill -f "/opt/employee-check/EmployeeCheckEmployer" 2>/dev/null || true
pkill -f "/opt/employee-check/EmployeeCheckEmployee" 2>/dev/null || true

purge_deb_package "employee-check-employer"
purge_deb_package "employee-check-employee"

echo "Removing installed files and startup entries..."
remove_path \
  "/opt/employee-check/EmployeeCheckEmployer" \
  "/opt/employee-check/EmployeeCheckEmployee" \
  "/opt/employee-check/uninstall-employer.sh" \
  "/opt/employee-check/uninstall-employee.sh" \
  "/usr/bin/employee-check-uninstall-employer" \
  "/usr/bin/employee-check-uninstall-employee" \
  "/usr/local/bin/employee-check-employer" \
  "/usr/local/bin/employee-check-employee" \
  "/usr/local/bin/employee-check-uninstall-employer" \
  "/usr/local/bin/employee-check-uninstall-employee" \
  "/usr/share/applications/employee-check-employer.desktop" \
  "/usr/share/applications/employee-check-employee.desktop" \
  "/etc/xdg/autostart/employee-check-employer.desktop" \
  "/etc/xdg/autostart/employee-check-employee.desktop"

rmdir /opt/employee-check 2>/dev/null || true

echo "Removing user config, reports, local database, and user startup entries..."
remove_user_files "/root"
for home_dir in /home/*; do
  [ -d "${home_dir}" ] || continue
  remove_user_files "${home_dir}"
done

echo "Employee Check has been removed from this machine."

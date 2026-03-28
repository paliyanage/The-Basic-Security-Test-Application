import os
import psutil
import platform
import subprocess
from utils import stream_cmd, logger


def check_open_ports():
    logger.info("Running check_open_ports")
    out = stream_cmd(["ss", "-tuln"])
    result = {"open_ports": out}
    logger.info(f"check_open_ports output: {result}")
    logger.info("Completed check_open_ports")
    return result


def check_firewall_status():
    logger.info("Running check_firewall_status")
    try:
        out = stream_cmd(["ufw", "status"])
    except Exception:
        out = "ufw not installed"
    result = {"firewall": out}
    logger.info(f"check_firewall_status output: {result}")
    logger.info("Completed check_firewall_status")
    return result


def check_installed_packages():
    logger.info("Running check_installed_packages")
    try:
        out = stream_cmd(["dpkg", "-l"])
        pkgs = out.splitlines()[:20]
    except Exception:
        out = stream_cmd(["rpm", "-qa"])
        pkgs = out.splitlines()[:20]
    result = {"packages": pkgs}
    logger.info(f"check_installed_packages output: {result}")
    logger.info("Completed check_installed_packages")
    return result


def check_service_status():
    logger.info("Running check_service_status")
    out = stream_cmd(["systemctl", "list-units", "--type=service", "--state=running"])
    result = {"services": out}
    logger.info(f"check_service_status output: {result}")
    logger.info("Completed check_service_status")
    return result


def check_sshd_config():
    logger.info("Running check_sshd_config")
    try:
        content = open("/etc/ssh/sshd_config").read()
    except Exception:
        content = "sshd_config not found"
    result = {"sshd_config": content}
    logger.info(f"check_sshd_config output: {result}")
    logger.info("Completed check_sshd_config")
    return result


def check_cron_jobs():
    logger.info("Running check_cron_jobs")
    try:
        out = stream_cmd(["crontab", "-l"])
    except Exception:
        out = "no cron jobs or crontab not available"
    result = {"cron_jobs": out}
    logger.info(f"check_cron_jobs output: {result}")
    logger.info("Completed check_cron_jobs")
    return result


def check_sudoers():
    logger.info("Running check_sudoers")
    try:
        content = open("/etc/sudoers", "r").read()
    except Exception:
        content = "sudoers file not found"
    result = {"sudoers": content}
    logger.info(f"check_sudoers output: {result}")
    logger.info("Completed check_sudoers")
    return result


def check_world_writable_files():
    logger.info("Running check_world_writable_files")
    out = stream_cmd(["find", "/", "-xdev", "-type", "f", "-perm", "-0002"])
    count = len(out.splitlines())
    result = {"world_writable_files": count}
    logger.info(f"check_world_writable_files output: {result}")
    logger.info("Completed check_world_writable_files")
    return result


def check_suid_files():
    logger.info("Running check_suid_files")
    out = stream_cmd(["find", "/", "-xdev", "-type", "f", "-perm", "+4000"])
    count = len(out.splitlines())
    result = {"suid_files": count}
    logger.info(f"check_suid_files output: {result}")
    logger.info("Completed check_suid_files")
    return result


def check_etc_passwd_permissions():
    logger.info("Running check_etc_passwd_permissions")
    mode = oct(os.stat("/etc/passwd").st_mode & 0o777)
    result = {"passwd_mode": mode}
    logger.info(f"check_etc_passwd_permissions output: {result}")
    logger.info("Completed check_etc_passwd_permissions")
    return result


def check_etc_shadow_permissions():
    logger.info("Running check_etc_shadow_permissions")
    mode = oct(os.stat("/etc/shadow").st_mode & 0o777)
    result = {"shadow_mode": mode}
    logger.info(f"check_etc_shadow_permissions output: {result}")
    logger.info("Completed check_etc_shadow_permissions")
    return result


def check_root_login_allowed():
    logger.info("Running check_root_login_allowed")
    try:
        out = stream_cmd(["grep", "^PermitRootLogin", "/etc/ssh/sshd_config"]).strip()
    except Exception:
        out = "PermitRootLogin config not found"
    result = {"PermitRootLogin": out}
    logger.info(f"check_root_login_allowed output: {result}")
    logger.info("Completed check_root_login_allowed")
    return result


def check_password_policy():
    logger.info("Running check_password_policy")
    try:
        out = stream_cmd(["grep", "^PASS_MAX_DAYS", "/etc/login.defs"]).strip()
    except Exception:
        out = "login.defs not found"
    result = {"password_policy": out}
    logger.info(f"check_password_policy output: {result}")
    logger.info("Completed check_password_policy")
    return result


def check_auditd_status():
    logger.info("Running check_auditd_status")
    try:
        out = stream_cmd(["systemctl", "status", "auditd"])
    except Exception:
        out = "auditd not installed"
    result = {"auditd_status": out}
    logger.info(f"check_auditd_status output: {result}")
    logger.info("Completed check_auditd_status")
    return result


def check_sysctl_hardening():
    logger.info("Running check_sysctl_hardening")
    out = stream_cmd(["sysctl", "-a"])
    result = {"sysctl_all": out[:1000]}
    logger.info(f"check_sysctl_hardening output: {result}")
    logger.info("Completed check_sysctl_hardening")
    return result


def check_kernel_version():
    logger.info("Running check_kernel_version")
    ver = platform.release()
    result = {"kernel_version": ver}
    logger.info(f"check_kernel_version output: {result}")
    logger.info("Completed check_kernel_version")
    return result


def check_disk_inodes_usage():
    logger.info("Running check_disk_inodes_usage")
    out = stream_cmd(["df", "-i"])
    result = {"inodes": out}
    logger.info(f"check_disk_inodes_usage output: {result}")
    logger.info("Completed check_disk_inodes_usage")
    return result


def check_swap_usage():
    logger.info("Running check_swap_usage")
    s = psutil.swap_memory()
    result = {"swap_total_mb": s.total // (1024**2), "swap_used_mb": s.used // (1024**2)}
    logger.info(f"check_swap_usage output: {result}")
    logger.info("Completed check_swap_usage")
    return result


def check_selinux_status():
    logger.info("Running check_selinux_status")
    try:
        out = stream_cmd(["sestatus"])
    except Exception:
        out = "sestatus not available"
    result = {"selinux_status": out}
    logger.info(f"check_selinux_status output: {result}")
    logger.info("Completed check_selinux_status")
    return result


def check_iptables_rules():
    logger.info("Running check_iptables_rules")
    try:
        out = stream_cmd(["iptables", "-L"])
    except Exception:
        out = "iptables not installed"
    result = {"iptables_rules": out}
    logger.info(f"check_iptables_rules output: {result}")
    logger.info("Completed check_iptables_rules")
    return result


def check_docker_socket_permissions():
    logger.info("Running check_docker_socket_permissions")
    path = "/var/run/docker.sock"
    try:
        mode = oct(os.stat(path).st_mode & 0o777)
    except Exception:
        mode = f"{path} not found"
    result = {"docker_socket_mode": mode}
    logger.info(f"check_docker_socket_permissions output: {result}")
    logger.info("Completed check_docker_socket_permissions")
    return result


def check_rootkit_with_chkrootkit():
    logger.info("Running check_rootkit_with_chkrootkit")
    try:
        out = stream_cmd(["chkrootkit", "--sk"])
    except Exception:
        out = "chkrootkit not installed"
    result = {"chkrootkit_summary": out.splitlines()[:10]}
    logger.info(f"check_rootkit_with_chkrootkit output: {result}")
    logger.info("Completed check_rootkit_with_chkrootkit")
    return result


def check_wifi_interfaces():
    logger.info("Running check_wifi_interfaces")
    try:
        out = stream_cmd(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"])
    except Exception:
        out = "nmcli not available"
    result = {"wifi_devices": out.splitlines()}
    logger.info(f"check_wifi_interfaces output: {result}")
    logger.info("Completed check_wifi_interfaces")
    return result


def check_connected_wifi_ssid():
    logger.info("Running check_connected_wifi_ssid")
    try:
        ssid = stream_cmd(["iwgetid", "-r"]).strip()
    except Exception:
        ssid = "not connected or iwgetid unavailable"
    result = {"connected_ssid": ssid}
    logger.info(f"check_connected_wifi_ssid output: {result}")
    logger.info("Completed check_connected_wifi_ssid")
    return result


def scan_nearby_wifi_networks():
    logger.info("Running scan_nearby_wifi_networks")
    try:
        out = stream_cmd(["nmcli", "device", "wifi", "list"])
    except Exception:
        out = "nmcli not available"
    result = {"wifi_scan": out.splitlines()}
    logger.info(f"scan_nearby_wifi_networks output: {result}")
    logger.info("Completed scan_nearby_wifi_networks")
    return result


linux_checks = [
    check_open_ports,
    check_firewall_status,
    check_installed_packages,
    check_service_status,
    check_sshd_config,
    check_cron_jobs,
    check_sudoers,
    check_world_writable_files,
    check_suid_files,
    check_etc_passwd_permissions,
    check_etc_shadow_permissions,
    check_root_login_allowed,
    check_password_policy,
    check_auditd_status,
    check_sysctl_hardening,
    check_kernel_version,
    check_disk_inodes_usage,
    check_swap_usage,
    check_selinux_status,
    check_iptables_rules,
    check_docker_socket_permissions,
    check_rootkit_with_chkrootkit,
    check_wifi_interfaces,
    check_connected_wifi_ssid,
    scan_nearby_wifi_networks
]

import os
import platform
import subprocess
from utils import stream_cmd, logger


def check_open_ports():
    logger.info("Running check_open_ports")
    out = stream_cmd(["lsof", "-i", "-P", "-n"])
    result = {"open_ports": out}
    logger.info(f"check_open_ports output: {result}")
    logger.info("Completed check_open_ports")
    return result


def check_firewall_pfctl():
    logger.info("Running check_firewall_pfctl")
    try:
        out = stream_cmd(["pfctl", "-sr"])
    except Exception:
        out = "pfctl not available"
    result = {"pf_rules": out}
    logger.info(f"check_firewall_pfctl output: {result}")
    logger.info("Completed check_firewall_pfctl")
    return result


def check_installed_homebrew():
    logger.info("Running check_installed_homebrew")
    try:
        out = stream_cmd(["brew", "list", "--versions"])
        pkgs = out.splitlines()
    except Exception:
        pkgs = []
        out = "brew not installed"
    result = {"brew_pkgs": pkgs or out}
    logger.info(f"check_installed_homebrew output: {result}")
    logger.info("Completed check_installed_homebrew")
    return result


def check_launchd_services():
    logger.info("Running check_launchd_services")
    out = stream_cmd(["launchctl", "list"])
    result = {"launchd_services": out}
    logger.info(f"check_launchd_services output: {result}")
    logger.info("Completed check_launchd_services")
    return result


def check_system_integrity():
    logger.info("Running check_system_integrity")
    try:
        out = stream_cmd(["csrutil", "status"])
    except Exception:
        out = "csrutil not available"
    result = {"sip_status": out.strip()}
    logger.info(f"check_system_integrity output: {result}")
    logger.info("Completed check_system_integrity")
    return result


def check_filevault_status():
    logger.info("Running check_filevault_status")
    try:
        out = stream_cmd(["fdesetup", "status"])
    except Exception:
        out = "fdesetup not available"
    result = {"filevault": out.strip()}
    logger.info(f"check_filevault_status output: {result}")
    logger.info("Completed check_filevault_status")
    return result


def check_time_machine():
    logger.info("Running check_time_machine")
    try:
        out = stream_cmd(["tmutil", "status"])
    except Exception:
        out = "tmutil not available"
    result = {"timemachine_status": out}
    logger.info(f"check_time_machine output: {result}")
    logger.info("Completed check_time_machine")
    return result


def check_spotlight():
    logger.info("Running check_spotlight")
    try:
        out = stream_cmd(["mdutil", "-s", "/"])
    except Exception:
        out = "mdutil not available"
    result = {"spotlight": out.strip()}
    logger.info(f"check_spotlight output: {result}")
    logger.info("Completed check_spotlight")
    return result


def check_user_accounts():
    logger.info("Running check_user_accounts")
    out = stream_cmd(["dscl", ".", "list", "/Users"])
    result = {"users": out.splitlines()}
    logger.info(f"check_user_accounts output: {result}")
    logger.info("Completed check_user_accounts")
    return result


def check_usb_devices():
    logger.info("Running check_usb_devices")
    out = stream_cmd(["system_profiler", "SPUSBDataType"])
    result = {"usb_devices": out}
    logger.info(f"check_usb_devices output: {result}")
    logger.info("Completed check_usb_devices")
    return result


def check_system_updates():
    logger.info("Running check_system_updates")
    try:
        out = stream_cmd(["softwareupdate", "-l"])
    except Exception:
        out = "softwareupdate not available"
    result = {"updates": out}
    logger.info(f"check_system_updates output: {result}")
    logger.info("Completed check_system_updates")
    return result


def check_host_name():
    logger.info("Running check_host_name")
    result = {"hostname": platform.node()}
    logger.info(f"check_host_name output: {result}")
    logger.info("Completed check_host_name")
    return result


def check_docker_socket_permissions():
    logger.info("Running check_docker_socket_permissions")
    path = "/var/run/docker.sock"
    try:
        mode = oct(os.stat(path).st_mode & 0o777)
    except FileNotFoundError:
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


def check_wifi_info():
    logger.info("Running check_wifi_info")
    airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    try:
        out = stream_cmd([airport, "-I"])
    except Exception:
        out = "airport utility not found"
    result = {"wifi_info": out.splitlines()}
    logger.info(f"check_wifi_info output: {result}")
    logger.info("Completed check_wifi_info")
    return result


darwin_checks = [
    check_open_ports,
    check_firewall_pfctl,
    check_installed_homebrew,
    check_launchd_services,
    check_system_integrity,
    check_filevault_status,
    check_time_machine,
    check_spotlight,
    check_user_accounts,
    check_usb_devices,
    check_system_updates,
    check_host_name,
    check_docker_socket_permissions,
    check_rootkit_with_chkrootkit,
    check_wifi_info
]

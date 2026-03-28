# agent/audits/system.py
import platform
from utils import stream_cmd, logger

def check_firewall_scan():
    logger.info("Running check_firewall_scan")
    if platform.system() == "Linux":
        out = stream_cmd(["iptables", "-L"])
    else:
        out = stream_cmd(["pfctl", "-sr"])
    result = {"firewall_rules": out}
    logger.info(f"check_firewall_scan output: {result}")
    logger.info("Completed check_firewall_scan")
    return result

def check_system_users():
    logger.info("Running check_system_users")
    out = stream_cmd(["cat", "/etc/passwd"])
    result = {"system_users": out.splitlines()}
    logger.info(f"check_system_users output: {result}")
    logger.info("Completed check_system_users")
    return result

def check_kernel_modules():
    logger.info("Running check_kernel_modules")
    if platform.system() == "Linux":
        out = stream_cmd(["lsmod"])
    else:
        out = stream_cmd(["kextstat"])
    result = {"kernel_modules": out}
    logger.info(f"check_kernel_modules output: {result}")
    logger.info("Completed check_kernel_modules")
    return result

def check_password_policies():
    logger.info("Running check_password_policies")
    if platform.system() == "Linux":
        try:
            out = stream_cmd(["grep", "-E", "^PASS_MAX_DAYS", "/etc/login.defs"])
        except Exception:
            out = "login.defs not found"
    else:
        out = "Password policy check not implemented on macOS"
    result = {"password_policies": out}
    logger.info(f"check_password_policies output: {result}")
    logger.info("Completed check_password_policies")
    return result

def check_suid_sgid_files():
    logger.info("Running check_suid_sgid_files")
    if platform.system() == "Linux":
        out = stream_cmd([
            "find", "/", "-xdev", "(", "-perm", "-4000", "-o", "-perm", "-2000", ")", "-print"
        ])
    else:
        out = stream_cmd([
            "find", "/", "-xdev", "-perm", "+4000"
        ])
    count = len(out.splitlines())
    result = {"suid_sgid_files_count": count}
    logger.info(f"check_suid_sgid_files output: {result}")
    logger.info("Completed check_suid_sgid_files")
    return result

system_checks = [
    check_firewall_scan,
    check_system_users,
    check_kernel_modules,
    check_password_policies,
    check_suid_sgid_files,
]
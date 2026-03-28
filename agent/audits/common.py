import os
import psutil
import platform
import socket
from datetime import datetime
from utils import stream_cmd, logger


def detect_system():
    logger.info("Running detect_system")
    info = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    logger.info(f"detect_system output: {info}")
    logger.info("Completed detect_system")
    return info


def check_cpu_usage():
    logger.info("Running check_cpu_usage")
    result = {"cpu_percent": psutil.cpu_percent(interval=1)}
    logger.info(f"check_cpu_usage output: {result}")
    logger.info("Completed check_cpu_usage")
    return result


def check_memory():
    logger.info("Running check_memory")
    m = psutil.virtual_memory()
    result = {"total_mb": m.total // (1024**2), "used_mb": m.used // (1024**2), "percent": m.percent}
    logger.info(f"check_memory output: {result}")
    logger.info("Completed check_memory")
    return result


def check_disk_usage():
    logger.info("Running check_disk_usage")
    du = psutil.disk_usage("/")
    result = {"total_gb": du.total // (1024**3), "used_gb": du.used // (1024**3), "percent": du.percent}
    logger.info(f"check_disk_usage output: {result}")
    logger.info("Completed check_disk_usage")
    return result


def check_disk_inodes():
    logger.info("Running check_disk_inodes")
    out = stream_cmd(["df", "-i"])
    result = {"inodes": out}
    logger.info(f"check_disk_inodes output: {result}")
    logger.info("Completed check_disk_inodes")
    return result


def check_network_interfaces():
    logger.info("Running check_network_interfaces")
    result = {iface: addrs for iface, addrs in psutil.net_if_addrs().items()}
    logger.info(f"check_network_interfaces output: {result}")
    logger.info("Completed check_network_interfaces")
    return result


def check_open_sockets():
    logger.info("Running check_open_sockets")
    result = {"connections": [c._asdict() for c in psutil.net_connections()]}
    logger.info(f"check_open_sockets output: {result}")
    logger.info("Completed check_open_sockets")
    return result


def check_uptime():
    logger.info("Running check_uptime")
    result = {"boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()}
    logger.info(f"check_uptime output: {result}")
    logger.info("Completed check_uptime")
    return result


def check_time_sync():
    logger.info("Running check_time_sync")
    out = stream_cmd(["timedatectl", "show"])
    result = {"time_info": out}
    logger.info(f"check_time_sync output: {result}")
    logger.info("Completed check_time_sync")
    return result


def check_hostname_resolution():
    logger.info("Running check_hostname_resolution")
    result = {"fqdn": socket.getfqdn(), "hostname": socket.gethostname()}
    logger.info(f"check_hostname_resolution output: {result}")
    logger.info("Completed check_hostname_resolution")
    return result


def check_users():
    logger.info("Running check_users")
    result = {"users": [u.name for u in psutil.users()]}
    logger.info(f"check_users output: {result}")
    logger.info("Completed check_users")
    return result


def check_groups():
    logger.info("Running check_groups")
    import grp
    result = {"groups": [g.gr_name for g in grp.getgrall()]}
    logger.info(f"check_groups output: {result}")
    logger.info("Completed check_groups")
    return result


def check_environment_vars():
    logger.info("Running check_environment_vars")
    import os
    result = {"env": {k: os.environ.get(k) for k in ["PATH", "HOME", "SHELL"] if k in os.environ}}
    logger.info(f"check_environment_vars output: {result}")
    logger.info("Completed check_environment_vars")
    return result


def check_locale():
    logger.info("Running check_locale")
    import locale
    result = {"locale": locale.getdefaultlocale()}
    logger.info(f"check_locale output: {result}")
    logger.info("Completed check_locale")
    return result


def check_vmstat():
    logger.info("Running check_vmstat")
    out = stream_cmd(["vmstat", "-s"])
    result = {"vmstat": out}
    logger.info(f"check_vmstat output: {result}")
    logger.info("Completed check_vmstat")
    return result


def check_cpu_temperature():
    logger.info("Running check_cpu_temperature")
    temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else None
    result = {"temps": temps}
    logger.info(f"check_cpu_temperature output: {result}")
    logger.info("Completed check_cpu_temperature")
    return result


common_checks = [
    detect_system, check_cpu_usage, check_memory, check_disk_usage,
    check_disk_inodes, check_network_interfaces, check_open_sockets,
    check_uptime, check_time_sync, check_hostname_resolution,
    check_users, check_groups, check_environment_vars, check_locale,
    check_vmstat, check_cpu_temperature
]

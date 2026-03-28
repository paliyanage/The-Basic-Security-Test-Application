# agent/audits/network.py
import platform
from utils import stream_cmd, logger

def check_ping_test():
    logger.info("Running check_ping_test")
    host = "8.8.8.8"
    cmd = ["ping", "-c", "4", host] if platform.system() != "Windows" else ["ping", "-n", "4", host]
    out = stream_cmd(cmd)
    result = {"ping_test": out}
    logger.info(f"check_ping_test output: {result}")
    logger.info("Completed check_ping_test")
    return result

def check_port_scan():
    logger.info("Running check_port_scan")
    try:
        out = stream_cmd(["nmap", "-Pn", "127.0.0.1"])
    except Exception:
        out = "nmap not installed"
    result = {"port_scan": out}
    logger.info(f"check_port_scan output: {result}")
    logger.info("Completed check_port_scan")
    return result

def check_dns_lookup():
    logger.info("Running check_dns_lookup")
    domain = "example.com"
    try:
        out = stream_cmd(["dig", "+short", domain])
    except Exception:
        out = "dig not available"
    result = {"dns_lookup": out.splitlines()}
    logger.info(f"check_dns_lookup output: {result}")
    logger.info("Completed check_dns_lookup")
    return result

def check_active_connections():
    logger.info("Running check_active_connections")
    out = stream_cmd(["ss", "-tunap"])
    result = {"active_connections": out}
    logger.info(f"check_active_connections output: {result}")
    logger.info("Completed check_active_connections")
    return result

def check_packet_analysis():
    logger.info("Running check_packet_analysis")
    try:
        out = stream_cmd(["tcpdump", "-c", "20", "-nn", "-i", "any"])
    except Exception:
        out = "tcpdump not available or requires privileges"
    result = {"packet_capture_sample": out}
    logger.info(f"check_packet_analysis output: {result}")
    logger.info("Completed check_packet_analysis")
    return result

def check_traceroute():
    logger.info("Running check_traceroute")
    target = "8.8.8.8"
    cmd = ["traceroute", target] if platform.system() != "Windows" else ["tracert", target]
    out = stream_cmd(cmd)
    result = {"network_traceroute": out}
    logger.info(f"check_traceroute output: {result}")
    logger.info("Completed check_traceroute")
    return result

network_checks = [
    check_ping_test,
    check_port_scan,
    check_dns_lookup,
    check_active_connections,
    check_packet_analysis,
    check_traceroute,
]
import platform
import click
import requests
import json
import os
import logging
import subprocess
from datetime import datetime
from rich import print
from rich.console import Console
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from audits.common import common_checks
from audits.linux import linux_checks
from audits.darwin import darwin_checks
from audits.network import network_checks
from audits.system import system_checks

# Initialize Rich console
console = Console()

# Module-level logger
logger = logging.getLogger("audit")

#Run terminal commands and logs their output line by line.
def stream_cmd(cmd: list[str]) -> str:
    """
    Run cmd, log and return full output.
    """
    logger.info(f"⟳ Executing: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    out_lines = []
    for line in proc.stdout:
        line = line.rstrip()
        logger.info(f"    {line}")
        out_lines.append(line)
    proc.wait()
    return "\n".join(out_lines)

#How to detect the OS of a system
def save_report_locally(auditor_code: str, report: dict):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"audit_{auditor_code}_{ts}.json"
    with open(fname, "w") as f:
        json.dump({"auditor_code": auditor_code, "report": report}, f, indent=2)
    print(f"[yellow]Saved JSON locally to {fname}[/]")

#generate simple PDF summery
def save_report_pdf(auditor_code: str, report: dict, log_file: str = None):
    """
    Save a basic PDF of the report and optionally embed the log file.
    """
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"audit_{auditor_code}_{ts}.pdf"
    c = canvas.Canvas(fname, pagesize=letter)
    text = c.beginText(40, 750)
    header = f"Audit Report — {auditor_code} ({ts})"
    text.textLine(header)
    text.textLine("-" * len(header))
    # Add JSON summary
    for key, value in report.items():
        line = f"{key}: {value}"
        for chunk in [line[i : i + 100] for i in range(0, len(line), 100)]:
            text.textLine(chunk)
        if text.getY() < 50:
            c.drawText(text)
            c.showPage()
            text = c.beginText(40, 750)
    # Optionally embed raw log
    if log_file and os.path.exists(log_file):
        text.textLine("")
        text.textLine("Raw Log:")
        with open(log_file) as lf:
            for log_line in lf:
                for chunk in [log_line.rstrip()[i : i + 100] for i in range(0, len(log_line), 100)]:
                    text.textLine(chunk)
                if text.getY() < 50:
                    c.drawText(text)
                    c.showPage()
                    text = c.beginText(40, 750)
    c.drawText(text)
    c.showPage()
    c.save()
    print(f"[yellow]Saved PDF locally to {fname}[/]")

@click.command()
@click.option("--auditor-code",   required=True, help="Your auditor code")
@click.option("--server-url",     required=True, help="API base URL")
@click.option("--client-company", required=True, help="Client’s company name")
@click.option("--it-manager",     required=True, help="Name of the IT manager")
def run_audit(auditor_code: str, server_url: str, client_company: str, it_manager: str):
    """
    Validate auditor code, run security checks, and submit or save report.
    """
    print(f"[bold]Connecting to[/] {server_url} with code {auditor_code}…")
    try:
        # Health check connect to backend
        resp = requests.get(f"{server_url.rstrip('/')}/health")
        resp.raise_for_status()
        print("[green]✓ Server is reachable[/]")

        # Auditor validation
        resp = requests.get(f"{server_url.rstrip('/')}/auditors/{auditor_code}")
        resp.raise_for_status()
        auditor = resp.json()
        print(f"[green]✓ Auditor code is valid for[/] {auditor.get('name')}")
        logger.info(f"Auditor code {auditor_code} is valid for {auditor.get('name')}")

        # Prepare logging
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        log_file = f"audit_{auditor_code}_{ts}.log"
        logger.setLevel(logging.INFO)
        # Clear existing handlers
        logger.handlers.clear()
        handler_file = logging.FileHandler(log_file)
        handler_console = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler_file.setFormatter(formatter)
        handler_console.setFormatter(formatter)
        logger.addHandler(handler_file)
        logger.addHandler(handler_console)
        logger.info(f"Starting audit for {auditor_code}")

        # Build checks
        checks = list(common_checks)
        os_name = platform.system()
        print(f"[green]✓ OS detected:[/] {os_name}")
        if os_name == "Windows":
            print("[red]✗ Windows not supported[/]")
            return
        elif os_name == "Linux":
            checks += linux_checks
            print("[green]✓ Linux checks loaded[/]")
            logger.info("green]✓ Linux checks loaded")
        elif os_name == "Darwin":
            checks += darwin_checks
            print("[green]✓ macOS checks loaded[/]")
            logger.info(" green]✓ macOS checks loaded")
        else:
            print(f"[red]✗ Unsupported OS: {os_name}[/]")
            return

        checks += network_checks
        checks += system_checks
        # Run checks
        report = {}
        for fn in checks:
            logger.info(f"Starting {fn.__name__}")
            try:
                report[fn.__name__] = fn()
                logger.info(f"Completed {fn.__name__}")
            except Exception as e:
                report[fn.__name__] = {"error": str(e)}
                logger.error(f"Error in {fn.__name__}: {e}")

        # Submit report
        # 5) Submit report
        payload = {
        "auditor_code":    auditor_code,
        "client_company":  client_company,
        "it_manager_name": it_manager,
        "log_path":        os.path.abspath(log_file),
        }
        print(f"[green]✓ Report ready for submission[/]")
        print(f"[green]✓ Client company:[/] {client_company}")
        print(f"[green]✓ IT manager:[/] {it_manager}")
        logger.info(f"Submitting report to {server_url}")
        logger.info(f"Client company: {client_company}")
        logger.info(f"IT manager: {it_manager}")
        
        try:
            resp = requests.post(
                f"{server_url.rstrip('/')}/reports",
                json=payload
            )
            resp.raise_for_status()
            if resp.status_code != 200:
                print(f"[red]✗ Failed to send report:[/] {resp.text}")
                return
            print(f"[green]✓ Report sent! ID =[/] {resp.json().get('report_id')}")
            save_report_locally(auditor_code, report)
            save_report_pdf(auditor_code, report, log_file)
        except Exception as e:
            print(f"[red]✗ Failed to send report:[/] {e}")
            save_report_locally(auditor_code, report)
            save_report_pdf(auditor_code, report, log_file)

        # Always save local copies
        save_report_locally(auditor_code, report)
        save_report_pdf(auditor_code, report, log_file)

    except Exception as e:
        print(f"[red]✗ Audit initialization failed:[/] {e}")


if __name__ == "__main__":
    run_audit()

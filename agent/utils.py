# agent/utils.py
import logging, subprocess
from datetime import datetime
import json, os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- Logger setup (module‐level, but configured later) ---
logger = logging.getLogger("audit")

def init_logger(log_file: str):
    """Call this once in cli to configure file + console handlers."""
    logger.setLevel(logging.INFO)
    # Remove old handlers, if any
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)

def stream_cmd(cmd: list[str]) -> str:
    logger.info(f"⟳ Executing: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines = []
    for line in proc.stdout:
        line = line.rstrip()
        logger.info(f"    {line}")
        lines.append(line)
    proc.wait()
    return "\n".join(lines)

def save_report_locally(auditor_code: str, report: dict):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"audit_{auditor_code}_{ts}.json"
    with open(fname, "w") as f:
        json.dump({"auditor_code": auditor_code, "report": report}, f, indent=2)
    logger.info(f"Saved JSON locally to {fname}")

def save_report_pdf(auditor_code: str, report: dict, log_file: str = None):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"audit_{auditor_code}_{ts}.pdf"
    c = canvas.Canvas(fname, pagesize=letter)
    text = c.beginText(40, 750)
    header = f"Audit Report — {auditor_code} ({ts})"
    text.textLine(header)
    text.textLine("-" * len(header))
    # JSON summary
    for key, val in report.items():
        for chunk in [str(val)[i:i+100] for i in range(0, len(str(val)), 100)]:
            text.textLine(f"{key}: {chunk}")
            if text.getY() < 50:
                c.drawText(text); c.showPage()
                text = c.beginText(40, 750)
    # embed raw log
    if log_file and os.path.exists(log_file):
        text.textLine(""); text.textLine("Raw Log:")
        with open(log_file) as lf:
            for line in lf:
                for chunk in [line.rstrip()[i:i+100] for i in range(0, len(line), 100)]:
                    text.textLine(chunk)
                    if text.getY() < 50:
                        c.drawText(text); c.showPage()
                        text = c.beginText(40, 750)
    c.drawText(text); c.showPage(); c.save()
    logger.info(f"Saved PDF locally to {fname}")
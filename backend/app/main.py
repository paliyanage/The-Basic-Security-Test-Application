# backend/app/main.py

import os
import io
import traceback
from uuid import uuid4
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy
from databases import Database
from sqlalchemy import select
from typing import Any, Dict, List, Optional

# Load .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Missing DATABASE_URL in environment")

# --- Database setup ---
database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

auditors = sqlalchemy.Table(
    "auditors", metadata,
    sqlalchemy.Column("id",             sqlalchemy.Integer,     primary_key=True),
    sqlalchemy.Column("auditor_code",   sqlalchemy.CHAR(8),     unique=True, nullable=False),
    sqlalchemy.Column("name",           sqlalchemy.Text,        nullable=False),
    sqlalchemy.Column("email",          sqlalchemy.Text,        nullable=False),
    sqlalchemy.Column("team",           sqlalchemy.Text,        nullable=False),
    sqlalchemy.Column("team_manager",   sqlalchemy.Text,        nullable=False),
    sqlalchemy.Column("registered_at",  sqlalchemy.TIMESTAMP(timezone=True),
                      server_default=sqlalchemy.func.now(), nullable=False),
)

reports = sqlalchemy.Table(
    "reports", metadata,
    sqlalchemy.Column("id",              sqlalchemy.Uuid(as_uuid=True),
                      primary_key=True,
                      server_default=sqlalchemy.text("gen_random_uuid()")),
    sqlalchemy.Column("auditor_id",      sqlalchemy.Integer,
                      sqlalchemy.ForeignKey("auditors.id", ondelete="CASCADE"),
                      nullable=False),
    sqlalchemy.Column("client_company",  sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("it_manager_name", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("log_path",        sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("received_at",     sqlalchemy.TIMESTAMP(timezone=True), nullable=False),
    sqlalchemy.Column("created_at",      sqlalchemy.TIMESTAMP(timezone=True),
                      server_default=sqlalchemy.func.now(), nullable=False),
)  

app = FastAPI()

# CORS settings
origins = [
    "http://localhost:3000",
    "https://your-production-domain.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic models ---

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    team: str
    team_manager: str

class RegisterResponse(BaseModel):
    auditor_code: str

class ReportRequest(BaseModel):
    auditor_code:    str
    client_company:  str
    it_manager_name: str
    log_path:        str

class ReportResponse(BaseModel):
    report_id:       str
    received_at:     datetime
    client_company:  str
    it_manager_name: str
    log_path:        str

class ReportSummary(BaseModel):
    report_id:       str
    client_company:  str
    it_manager_name: str
    received_at:     datetime
    log_path:        Optional[str] = None

# --- Startup / Shutdown ---

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    try:
        code = uuid4().hex[:8].upper()
        query = auditors.insert().values(
            auditor_code=code,
            name=request.name,
            email=request.email,
            team=request.team,
            team_manager=request.team_manager,
        )
        await database.execute(query)
        return {"auditor_code": code}
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Failed to register auditor")

@app.get("/auditors/{code}")
async def validate_auditor(code: str):
    try:
        code = code.upper()
        query = select(auditors).where(auditors.c.auditor_code == code)
        row = await database.fetch_one(query)
        if not row:
            raise HTTPException(404, "Auditor code not found")
        return {
            "valid": True,
            "name": row["name"],
            "email": row["email"],
            "team": row["team"],
            "team_manager": row["team_manager"],
        }
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Error validating auditor code")

@app.post("/reports", response_model=ReportResponse)
async def submit_report(payload: ReportRequest):
    try:
        # 1) Lookup auditor ID
        q = select(auditors.c.id).where(
            auditors.c.auditor_code == payload.auditor_code
        )
        aud = await database.fetch_one(q)
        if not aud:
            raise HTTPException(404, "Auditor code not found")

        # 2) Generate ID & timestamp
        rid = str(uuid4())
        now = datetime.utcnow()

        # 3) Insert only the log_path
        await database.execute(
            reports.insert().values(
                id               = rid,
                auditor_id       = aud["id"],
                client_company   = payload.client_company,
                it_manager_name  = payload.it_manager_name,
                log_path         = payload.log_path,
                received_at      = now,
            )
        )

        return ReportResponse(
            report_id       = rid,
            received_at     = now,
            client_company  = payload.client_company,
            it_manager_name = payload.it_manager_name,
            log_path        = payload.log_path,
        )

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Failed to save report")
    
#Return all reports specific auditor
@app.get("/reports", response_model=List[ReportSummary])
async def list_reports(auditor_code: str = Query(..., description="Auditor code")):
    try:
        # 1) Verify auditor exists
        q1 = select(auditors.c.id).where(auditors.c.auditor_code == auditor_code)
        aud = await database.fetch_one(q1)
        if not aud:
            raise HTTPException(404, "Auditor code not found")

        # 2) Fetch all reports for this auditor
        q2 = (
            select(reports)
            .where(reports.c.auditor_id == aud["id"])
            .order_by(reports.c.received_at.desc())
        )
        rows = await database.fetch_all(q2)

        # 3) Convert to summary
        return [
            ReportSummary(
                report_id       = str(row["id"]),
                client_company  = row["client_company"],
                it_manager_name = row["it_manager_name"],
                received_at     = row["received_at"],
                log_path        = row["log_path"],
            )
            for row in rows
        ]

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Could not retrieve reports")


@app.get("/reports/{rid}/log")
async def download_report_log(rid: str):
    try:
        rec = await database.fetch_one(
            select(reports.c.log_path).where(reports.c.id == rid)
        )
        if not rec:
            raise HTTPException(404, f"Report {rid} not found")

        log_path = rec["log_path"]
        if not log_path:
            raise HTTPException(404, f"No log_path recorded for report {rid}")

        if not os.path.isfile(log_path):
            # now we can see exactly which path is missing
            raise HTTPException(404, f"Log file not found on server: {log_path}")

        return FileResponse(
            path=log_path,
            media_type="text/plain",
            filename=os.path.basename(log_path),
        )

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Could not retrieve log file")
    
@app.get("/reports/{rid}/pdf")
async def get_report_pdf(rid: str):
    try:
        # fetch report
        q = select(reports).where(reports.c.id == rid)
        rec = await database.fetch_one(q)
        if not rec:
            raise HTTPException(404, "Report not found")

        # read and render the log file into a PDF
        buffer = io.BytesIO()
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(buffer, pagesize=letter)
        text = c.beginText(40, 750)
        header = f"Audit Report — {rec['client_company']} / {rec['it_manager_name']} ({rid})"
        text.textLine(header)
        text.textLine(f"Received: {rec['received_at'].isoformat()}")
        text.textLine("-" * len(header))

        # embed the raw log
        with open(rec["log_path"], "r") as lf:
            for line in lf:
                for chunk in [line[i:i+1000] for i in range(0, len(line), 1000)]:
                    text.textLine(chunk)
                    if text.getY() < 50:
                        c.drawText(text)
                        c.showPage()
                        text = c.beginText(40, 750)

        c.drawText(text)
        c.showPage()
        c.save()
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf")

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Could not generate PDF")
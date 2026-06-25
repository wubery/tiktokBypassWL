from datetime import datetime

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import Job, PublishLog
from app.api.deps import require_panel_auth
from app.scheduler import schedule_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/", dependencies=[Depends(require_panel_auth)])
def list_jobs(session: Session = Depends(get_session)):
    return session.exec(select(Job)).all()


@router.post("/", dependencies=[Depends(require_panel_auth)])
def create_jobs(
    video_id: int = Form(...),
    account_ids: str = Form(...),
    scheduled_at: str | None = Form(None),
    session: Session = Depends(get_session),
):
    scheduled_dt = datetime.fromisoformat(scheduled_at) if scheduled_at else None
    ids = [int(x.strip()) for x in account_ids.split(",") if x.strip()]

    for account_id in ids:
        job = Job(video_id=video_id, account_id=account_id, scheduled_at=scheduled_dt)
        session.add(job)
        session.commit()
        session.refresh(job)
        schedule_job(job.id, scheduled_dt)

    return RedirectResponse("/", status_code=303)


@router.get("/{job_id}/logs", dependencies=[Depends(require_panel_auth)])
def job_logs(job_id: int, session: Session = Depends(get_session)):
    return session.exec(select(PublishLog).where(PublishLog.job_id == job_id)).all()

from datetime import datetime

from fastapi import APIRouter, Depends
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
    video_id: int,
    account_ids: list[int],
    scheduled_at: datetime | None = None,
    session: Session = Depends(get_session),
):
    created = []
    for account_id in account_ids:
        job = Job(video_id=video_id, account_id=account_id, scheduled_at=scheduled_at)
        session.add(job)
        session.commit()
        session.refresh(job)
        schedule_job(job.id, scheduled_at)
        created.append(job)
    return created


@router.get("/{job_id}/logs", dependencies=[Depends(require_panel_auth)])
def job_logs(job_id: int, session: Session = Depends(get_session)):
    return session.exec(select(PublishLog).where(PublishLog.job_id == job_id)).all()

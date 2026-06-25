import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select

from app.db import engine
from app.models import Job, Video, Account, Watermark, PublishLog
from app.video.watermark import apply_watermark
from app.auth.tiktok_oauth import get_cookies, get_proxy
from app.publisher.tiktok_client import publish_video, TikTokPublishError

logger = logging.getLogger("scheduler")
scheduler = AsyncIOScheduler()

MAX_RETRIES = 3


def schedule_job(job_id: int, run_at: datetime | None) -> None:
    if run_at:
        scheduler.add_job(run_job, "date", run_date=run_at, args=[job_id], id=f"job-{job_id}", replace_existing=True)
    else:
        scheduler.add_job(run_job, args=[job_id], id=f"job-{job_id}", replace_existing=True)


async def run_job(job_id: int, attempt: int = 1) -> None:
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            return
        job.status = "processing"
        job.updated_at = datetime.utcnow()
        session.add(job)
        session.commit()

        try:
            video = session.get(Video, job.video_id)
            account = session.get(Account, job.account_id)

            processed_path = video.processed_path
            if not processed_path:
                watermark = session.get(Watermark, video.watermark_id) if video.watermark_id else None
                processed_path = apply_watermark(video.raw_path, watermark) if watermark else video.raw_path
                video.processed_path = processed_path
                session.add(video)
                session.commit()

            cookies_content = get_cookies(account)
            proxy = get_proxy(account)
            await publish_video(cookies_content, processed_path, caption=video.title, proxy=proxy)
            job.status = "published"

        except Exception as exc:  # noqa: BLE001
            logger.exception("Job %s failed (attempt %s)", job_id, attempt)
            job.status = "failed"
            job.error = str(exc)
            session.add(PublishLog(job_id=job_id, status="error", message=str(exc)))
            if attempt < MAX_RETRIES:
                delay = timedelta(seconds=30 * attempt)
                scheduler.add_job(
                    run_job, "date",
                    run_date=datetime.utcnow() + delay,
                    args=[job_id, attempt + 1],
                    id=f"job-{job_id}-retry-{attempt}",
                )
        else:
            session.add(PublishLog(job_id=job_id, status="published"))
        finally:
            job.updated_at = datetime.utcnow()
            session.add(job)
            session.commit()

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import init_db, get_session
from app.api.deps import require_panel_auth
from app.api import accounts, videos, jobs
from app.scheduler import scheduler
from app.models import Account, Video, Watermark, Job

app = FastAPI(title="TikTok Publisher")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(accounts.router)
app.include_router(videos.router)
app.include_router(jobs.router)


@app.on_event("startup")
def on_startup():
    init_db()
    scheduler.start()


@app.get("/", dependencies=[Depends(require_panel_auth)])
def index(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "accounts": session.exec(select(Account)).all(),
            "videos": session.exec(select(Video)).all(),
            "watermarks": session.exec(select(Watermark)).all(),
            "jobs": session.exec(select(Job)).all(),
        },
    )

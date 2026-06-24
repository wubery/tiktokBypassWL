from fastapi import APIRouter, Depends, UploadFile, Form
from sqlmodel import Session, select

from app.db import get_session
from app.models import Video, Watermark
from app.api.deps import require_panel_auth
from app.video.ingest import save_uploaded_file, download_own_youtube_video

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("/", dependencies=[Depends(require_panel_auth)])
def list_videos(session: Session = Depends(get_session)):
    return session.exec(select(Video)).all()


@router.post("/upload", dependencies=[Depends(require_panel_auth)])
async def upload_video(
    title: str = Form(...),
    watermark_id: int | None = Form(None),
    file: UploadFile | None = None,
    youtube_url: str | None = Form(None),
    session: Session = Depends(get_session),
):
    if file is not None:
        content = await file.read()
        raw_path = save_uploaded_file(file.filename, content)
    elif youtube_url:
        raw_path = download_own_youtube_video(youtube_url)
    else:
        raise ValueError("Provide either a file or youtube_url")

    video = Video(title=title, raw_path=raw_path, watermark_id=watermark_id)
    session.add(video)
    session.commit()
    session.refresh(video)
    return video


@router.post("/watermarks", dependencies=[Depends(require_panel_auth)])
async def upload_watermark(
    name: str = Form(...),
    position: str = Form("bottom_right"),
    opacity: float = Form(0.8),
    scale: float = Form(0.15),
    file: UploadFile = None,
    session: Session = Depends(get_session),
):
    content = await file.read()
    from app.video.ingest import save_uploaded_file as _save
    import os
    from app.config import STORAGE_WATERMARKS

    os.makedirs(STORAGE_WATERMARKS, exist_ok=True)
    path = os.path.join(STORAGE_WATERMARKS, file.filename)
    with open(path, "wb") as f:
        f.write(content)

    watermark = Watermark(name=name, file_path=path, position=position, opacity=opacity, scale=scale)
    session.add(watermark)
    session.commit()
    session.refresh(watermark)
    return watermark

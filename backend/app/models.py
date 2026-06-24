from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    label: str
    cookies_enc: Optional[bytes] = None  # содержимое cookies.txt, зашифрованное
    cookies_updated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    raw_path: str
    processed_path: Optional[str] = None
    watermark_id: Optional[int] = Field(default=None, foreign_key="watermark.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Watermark(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    file_path: str
    position: str = "bottom_right"  # top_left/top_right/bottom_left/bottom_right
    opacity: float = 0.8
    scale: float = 0.15  # доля ширины видео
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: int = Field(foreign_key="video.id")
    account_id: int = Field(foreign_key="account.id")
    scheduled_at: Optional[datetime] = None
    status: str = "queued"  # queued/processing/published/failed
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PublishLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    status: str
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

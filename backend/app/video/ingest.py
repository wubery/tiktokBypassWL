"""Приём видео в систему.

Загрузка собственного файла — основной путь. Импорт по ссылке на YouTube
поддерживается только для видео, которыми пользователь владеет на своём
канале (он сам указывает URL своего ролика); это не сервис скрапинга чужого
контента.
"""
import os
import uuid

from app.config import STORAGE_RAW


def save_uploaded_file(filename: str, content: bytes) -> str:
    os.makedirs(STORAGE_RAW, exist_ok=True)
    ext = os.path.splitext(filename)[1] or ".mp4"
    dest = os.path.join(STORAGE_RAW, f"{uuid.uuid4().hex}{ext}")
    with open(dest, "wb") as f:
        f.write(content)
    return dest


def download_own_youtube_video(url: str) -> str:
    """Скачивает видео по ссылке, указанной пользователем как принадлежащее ему.

    Ответственность за то, что пользователь владеет правами на видео,
    лежит на пользователе панели (внутренний инструмент, не публичный сервис).
    """
    import yt_dlp

    os.makedirs(STORAGE_RAW, exist_ok=True)
    out_template = os.path.join(STORAGE_RAW, f"{uuid.uuid4().hex}.%(ext)s")
    ydl_opts = {
        "outtmpl": out_template,
        "format": "mp4/bestvideo+bestaudio",
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

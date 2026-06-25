"""Публикация через открытый проект tiktok-uploader (wkaisertexas/tiktok-uploader).

В отличие от официального Content Posting API, эта библиотека работает через
браузерную автоматизацию (Selenium + Chromium) с подменой cookies сессии — то
есть имитирует залогиненного пользователя в браузере, а не использует OAuth.
Поэтому: без client_key/secret и без review приложения, но с риском детекта
автоматизации платформой (капча/блокировка), особенно при частой публикации
из множества аккаунтов с одного IP. Используйте умеренный темп и проксі при
необходимости.
"""
import asyncio
import logging
import os
import tempfile
from typing import Optional

logger = logging.getLogger("tiktok_publisher")


class TikTokPublishError(Exception):
    pass


def _upload_sync(video_path: str, caption: str, cookies_path: str, proxy: Optional[dict]) -> None:
    from tiktok_uploader.upload import upload_video

    kwargs = {"filename": video_path, "description": caption, "cookies": cookies_path}
    if proxy:
        kwargs["proxy"] = proxy

    failed = upload_video(**kwargs)
    if failed:
        raise TikTokPublishError(f"Upload reported as failed: {failed}")


async def publish_video(
    cookies_content: str,
    video_path: str,
    caption: str = "",
    proxy: Optional[dict] = None,
) -> None:
    """Публикует видео в аккаунт, чьи cookies переданы в `cookies_content`.

    cookies_content — содержимое cookies.txt (Netscape format), экспортированного
    из браузера после входа в нужный TikTok-аккаунт.
    proxy — опциональный dict {"host", "port", "user", "pass"}, передаётся
    в Selenium-сессию, чтобы публикация шла с отдельного IP на каждый аккаунт
    (снижает риск детекта автоматизации при множестве аккаунтов).
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write(cookies_content)
        cookies_path = tmp.name

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _upload_sync, video_path, caption, cookies_path, proxy)
    finally:
        os.unlink(cookies_path)

"""Хранение cookies TikTok-аккаунтов для tiktok-uploader.

Каждый аккаунт подключается вручную: пользователь логинится в TikTok в своём
браузере, экспортирует cookies.txt (например, расширением "Get cookies.txt")
и загружает файл в панель. Никакого автоматического логина по паролю здесь
нет и не предполагается.
"""
import json
from datetime import datetime
from typing import Optional

from sqlmodel import Session

from app.crypto import encrypt, decrypt
from app.models import Account


def store_cookies(session: Session, account: Account, cookies_content: str) -> None:
    account.cookies_enc = encrypt(cookies_content)
    account.cookies_updated_at = datetime.utcnow()
    session.add(account)
    session.commit()


def get_cookies(account: Account) -> str:
    if not account.cookies_enc:
        raise ValueError(f"Account {account.id} has no cookies uploaded")
    return decrypt(account.cookies_enc)


def store_proxy(
    session: Session,
    account: Account,
    host: str,
    port: str,
    user: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    proxy = {"host": host, "port": port}
    if user:
        proxy["user"] = user
    if password:
        proxy["pass"] = password
    account.proxy_enc = encrypt(json.dumps(proxy))
    session.add(account)
    session.commit()


def clear_proxy(session: Session, account: Account) -> None:
    account.proxy_enc = None
    session.add(account)
    session.commit()


def get_proxy(account: Account) -> Optional[dict]:
    if not account.proxy_enc:
        return None
    return json.loads(decrypt(account.proxy_enc))

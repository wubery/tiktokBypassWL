from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from sqlmodel import Session, select

from app.db import get_session
from app.models import Account
from app.api.deps import require_panel_auth
from app.auth.tiktok_oauth import store_cookies

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("/", dependencies=[Depends(require_panel_auth)])
def list_accounts(session: Session = Depends(get_session)):
    return session.exec(select(Account)).all()


@router.post("/", dependencies=[Depends(require_panel_auth)])
def create_account(label: str = Form(...), session: Session = Depends(get_session)):
    account = Account(label=label)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.post("/{account_id}/cookies", dependencies=[Depends(require_panel_auth)])
async def upload_cookies(account_id: int, file: UploadFile, session: Session = Depends(get_session)):
    """Загрузка cookies.txt, экспортированного из браузера после логина в аккаунт."""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(404, "Account not found")
    content = (await file.read()).decode("utf-8")
    store_cookies(session, account, content)
    return {"status": "ok", "account_id": account_id}

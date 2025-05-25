from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.oidc import OIDCService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
oidc_service = OIDCService()

@router.get("/oidc/login")
async def oidc_login(
    is_login: bool = True
):
    login_url = oidc_service.get_login_url()
    if is_login:
        return RedirectResponse(url=login_url)
    else:
        return {"url": login_url}

@router.get("/oidc/callback")
async def oidc_callback(
    code: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    client_host = request.client.host
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        xffs = xff.split(',')
        if len(xffs) > 0:
            client_host = xffs[0].strip()

    try:
        tokens = oidc_service.handle_callback(code, db, client_host)
        print(f"OIDC回调处理成功: {tokens}")
        return RedirectResponse(
            url=f"{settings.CONSOLE_WEB_URL}/signin?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}")
    except Exception as e:
        logger.exception("OIDC回调处理失败: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) 

@router.post("/oidc/logout")
async def oidc_logout(
    db: Session = Depends(get_db),
    request: Request = None
):
    login_id = request.loginID
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        xffs = xff.split(',')
        if len(xffs) > 0:
            login_id = xffs[0].strip()

    try:
        oidc_service.handle_logout(db, login_id)
        return {"message": "Logout successful"}
    except Exception as e:
        logger.exception("OIDC登出处理失败: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/oidc/userinfo")
async def oidc_userinfo(
    access_token: str,
    db: Session = Depends(get_db)
):
    try:
        user_info = oidc_service.get_user_info(access_token)
        print(f"获取用户信息成功: {user_info}")
        return user_info
    except Exception as e:
        logger.exception("获取用户信息失败: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
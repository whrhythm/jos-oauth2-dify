from fastapi import APIRouter
from app.api.endpoints import enterprise, health, sso

router = APIRouter()

router.include_router(sso.router, prefix="/api/v1/enterprise/sso") 
router.include_router(enterprise.router)
router.include_router(health.router)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import threading

# 每个请求独立 Session (线程局部变量)
local_session = threading.local()

logger = logging.getLogger(__name__)

DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600, pool_timeout=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    local_session.db = SessionLocal(bind=engine)
    try:
        yield local_session.db
    finally:
        local_session.db.close()

def check_database_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.exception("数据库连接检查失败: %s", str(e))
        return False
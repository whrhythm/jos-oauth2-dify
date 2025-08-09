from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"

# 延迟 engine 绑定，避免初始化时报错
engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

def get_engine():
    global engine
    if engine is None:
        try:
            engine = create_engine(DATABASE_URL)
        except Exception as e:
            logger.exception("数据库引擎创建失败: %s", str(e))
            raise
    return engine

def get_session():
    return SessionLocal(bind=get_engine())

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

def check_database_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.exception("数据库连接检查失败: %s", str(e))
        return False 
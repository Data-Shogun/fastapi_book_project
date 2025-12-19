from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config


SQL_DATABASE_URL = Config.SQL_DATABASE_URL

if SQL_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        url=SQL_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(url=SQL_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

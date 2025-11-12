from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import cidderbot.config as config

engine = create_engine(
    config.DATABASE_URL,
    echo=config.IS_SQL_DEBUG_ECHO,
)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

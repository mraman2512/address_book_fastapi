from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# creating the uri ./any name by which our sqlite db will  be crated at root location
SQLALCHEMY_DATABASE_URL = "sqlite:///./addressBook.db"

# The standard calling form is to send the :ref:`URL <database_urls>`
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# an Engine, which the Session will use for connection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

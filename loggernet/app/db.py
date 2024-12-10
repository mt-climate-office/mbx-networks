from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:////app/instruments.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Instruments(Base):
    __tablename__ = "instruments"

    id = Column(String, primary_key=True, index=True)
    long_name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    data = Column(JSON, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)

    with engine.connect() as connection:
        connection.execute("PRAGMA journal_mode=WAL;")  
        connection.execute("PRAGMA foreign_keys=ON;") 
        connection.execute("PRAGMA compile_options;")  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

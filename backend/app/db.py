from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./quality_gate.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ExecutionHistory(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True, index=True)
    prompt = Column(Text)
    context = Column(Text, nullable=True)
    expected_schema = Column(Text)
    final_response = Column(Text, nullable=True)
    success = Column(Boolean)
    recovery_strategy_used = Column(String, nullable=True)
    total_latency_ms = Column(Integer)
    trace = Column(Text) # JSON string of trace

def init_db():
    Base.metadata.create_all(bind=engine)

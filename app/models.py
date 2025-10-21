from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class AnalyzedString(Base):
    __tablename__ = "strings"

    id = Column(String, primary_key=True, index=True)  # sha256 hash
    value = Column(String, unique=True, nullable=False)
    length = Column(Integer)
    is_palindrome = Column(Boolean)
    unique_characters = Column(Integer)
    word_count = Column(Integer)
    sha256_hash = Column(String, unique=True)
    character_frequency_map = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

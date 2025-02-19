from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.infrastructure.database.database import Base


class MarkdownExtract(Base):
    __tablename__ = "markdowns"

    id = Column(Integer, primary_key=True, index=True)
    content_hash = Column(String(64), unique=True, index=True)
    extract_method = Column(String(50))
    markdown_content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

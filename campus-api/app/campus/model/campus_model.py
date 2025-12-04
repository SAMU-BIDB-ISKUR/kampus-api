# models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Campus(SQLModel, table=True):
    __tablename__ = "campuses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    city: str
    address: Optional[str] = None
    established_year: Optional[int] = None
    total_area: Optional[float] = None
    student_capacity: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# backend/app/models/staff.py

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class StaffRole(str, Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    ADMINISTRATIVE = "administrative"
    SUPPORT = "support"

class Department(str, Enum):
    EMERGENCY = "emergency"
    ICU = "icu"
    SURGERY = "surgery"
    PEDIATRICS = "pediatrics"
    CARDIOLOGY = "cardiology"
    GENERAL = "general"

class StaffMember(BaseModel):
    id: str
    name: str
    role: StaffRole
    department: Department
    skill_level: int = Field(ge=1, le=10, description="Skill level from 1-10")
    max_hours_per_week: int = Field(ge=20, le=60, description="Maximum working hours per week")
    preferred_shifts: List[str] = Field(default=[], description="Preferred shift times")
    unavailable_dates: List[str] = Field(default=[], description="Unavailable dates in YYYY-MM-DD format")
    certification_level: str = Field(default="basic", description="Certification level")
    experience_years: int = Field(ge=0, description="Years of experience")
    hourly_rate: float = Field(ge=15.0, description="Hourly rate in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "staff_001",
                "name": "Dr. Sarah Johnson",
                "role": "doctor",
                "department": "emergency",
                "skill_level": 9,
                "max_hours_per_week": 50,
                "preferred_shifts": ["morning", "evening"],
                "unavailable_dates": ["2024-07-20", "2024-07-21"],
                "certification_level": "senior",
                "experience_years": 8,
                "hourly_rate": 85.0
            }
        }

class StaffCreate(BaseModel):
    name: str
    role: StaffRole
    department: Department
    skill_level: int = Field(ge=1, le=10)
    max_hours_per_week: int = Field(ge=20, le=60)
    preferred_shifts: List[str] = []
    unavailable_dates: List[str] = []
    certification_level: str = "basic"
    experience_years: int = 0
    hourly_rate: float = 15.0

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[StaffRole] = None
    department: Optional[Department] = None
    skill_level: Optional[int] = None
    max_hours_per_week: Optional[int] = None
    preferred_shifts: Optional[List[str]] = None
    unavailable_dates: Optional[List[str]] = None
    certification_level: Optional[str] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
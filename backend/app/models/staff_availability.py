# backend/app/models/staff_availability.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    WORKING = "working"
    ON_BREAK = "on_break"
    UNAVAILABLE = "unavailable"

class StaffAvailability(BaseModel):
    id: str
    staff_id: str
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    current_shift_id: Optional[str] = Field(default=None, description="Current shift ID if working")
    available_from: Optional[str] = Field(default=None, description="Timestamp when staff becomes available (ISO format)")
    last_updated: str = Field(description="Last update timestamp (ISO format)")
    location: Optional[str] = Field(default=None, description="Current location/department")
    notes: Optional[str] = Field(default=None, description="Additional availability notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "availability_001",
                "staff_id": "staff_001",
                "status": "working",
                "current_shift_id": "shift_001",
                "available_from": "2024-07-15T16:00:00Z",
                "last_updated": "2024-07-15T08:00:00Z",
                "location": "emergency_dept",
                "notes": "Currently in surgery, will be available after 4 PM"
            }
        }

class StaffAvailabilityCreate(BaseModel):
    staff_id: str
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    current_shift_id: Optional[str] = None
    available_from: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class StaffAvailabilityUpdate(BaseModel):
    status: Optional[AvailabilityStatus] = None
    current_shift_id: Optional[str] = None
    available_from: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class AvailabilityTimeline(BaseModel):
    """Track availability changes over time"""
    id: str
    staff_id: str
    status: AvailabilityStatus
    changed_at: str = Field(description="Timestamp of status change (ISO format)")
    changed_by: Optional[str] = Field(default=None, description="Who made the change (system/user_id)")
    reason: Optional[str] = Field(default=None, description="Reason for status change")
    shift_id: Optional[str] = Field(default=None, description="Related shift ID if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "timeline_001",
                "staff_id": "staff_001",
                "status": "working",
                "changed_at": "2024-07-15T08:00:00Z",
                "changed_by": "system",
                "reason": "Automatic status update - shift started",
                "shift_id": "shift_001"
            }
        }
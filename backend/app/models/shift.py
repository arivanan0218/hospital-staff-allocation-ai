# # backend/app/models/shift.py

# from pydantic import BaseModel, Field
# from typing import List, Optional, Dict
# from enum import Enum
# from datetime import datetime, time

# class ShiftType(str, Enum):
#     MORNING = "morning"
#     AFTERNOON = "afternoon"
#     EVENING = "evening"
#     NIGHT = "night"
#     ON_CALL = "on_call"

# class Priority(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"
#     CRITICAL = "critical"

# class Shift(BaseModel):
#     id: str
#     date: str = Field(description="Date in YYYY-MM-DD format")
#     shift_type: ShiftType
#     department: str
#     start_time: str = Field(description="Start time in HH:MM format")
#     end_time: str = Field(description="End time in HH:MM format")
#     required_staff: Dict[str, int] = Field(description="Required staff by role")
#     minimum_skill_level: int = Field(ge=1, le=10, description="Minimum skill level required")
#     priority: Priority = Priority.MEDIUM
#     special_requirements: List[str] = Field(default=[], description="Special requirements for this shift")
#     max_capacity: int = Field(ge=1, description="Maximum number of staff for this shift")
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "id": "shift_001",
#                 "date": "2024-07-15",
#                 "shift_type": "morning",
#                 "department": "emergency",
#                 "start_time": "08:00",
#                 "end_time": "16:00",
#                 "required_staff": {
#                     "doctor": 2,
#                     "nurse": 4,
#                     "technician": 1
#                 },
#                 "minimum_skill_level": 6,
#                 "priority": "high",
#                 "special_requirements": ["trauma_certified", "bilingual"],
#                 "max_capacity": 8
#             }
#         }

# class ShiftCreate(BaseModel):
#     date: str
#     shift_type: ShiftType
#     department: str
#     start_time: str
#     end_time: str
#     required_staff: Dict[str, int]
#     minimum_skill_level: int = Field(ge=1, le=10)
#     priority: Priority = Priority.MEDIUM
#     special_requirements: List[str] = []
#     max_capacity: int = 5

# class ShiftUpdate(BaseModel):
#     date: Optional[str] = None
#     shift_type: Optional[ShiftType] = None
#     department: Optional[str] = None
#     start_time: Optional[str] = None
#     end_time: Optional[str] = None
#     required_staff: Optional[Dict[str, int]] = None
#     minimum_skill_level: Optional[int] = None
#     priority: Optional[Priority] = None
#     special_requirements: Optional[List[str]] = None
#     max_capacity: Optional[int] = None

# backend/app/models/shift.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime, time

class ShiftType(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    ON_CALL = "on_call"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ShiftStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Shift(BaseModel):
    id: str
    date: str = Field(description="Date in YYYY-MM-DD format")
    shift_type: ShiftType
    department: str
    start_time: str = Field(description="Start time in HH:MM format")
    end_time: str = Field(description="End time in HH:MM format")
    required_staff: Dict[str, int] = Field(description="Required staff by role")
    minimum_skill_level: int = Field(ge=1, le=10, description="Minimum skill level required")
    priority: Priority = Priority.MEDIUM
    special_requirements: List[str] = Field(default=[], description="Special requirements for this shift")
    max_capacity: int = Field(ge=1, description="Maximum number of staff for this shift")
    
    # NEW FIELDS FOR LIFECYCLE MANAGEMENT
    status: ShiftStatus = Field(default=ShiftStatus.SCHEDULED, description="Current shift status")
    actual_start_time: Optional[str] = Field(default=None, description="Actual start time in HH:MM format")
    actual_end_time: Optional[str] = Field(default=None, description="Actual end time in HH:MM format")
    is_extended: bool = Field(default=False, description="Whether shift was extended beyond scheduled time")
    completion_notes: Optional[str] = Field(default=None, description="Notes about shift completion")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "shift_001",
                "date": "2024-07-15",
                "shift_type": "morning",
                "department": "emergency",
                "start_time": "08:00",
                "end_time": "16:00",
                "required_staff": {
                    "doctor": 2,
                    "nurse": 4,
                    "technician": 1
                },
                "minimum_skill_level": 6,
                "priority": "high",
                "special_requirements": ["trauma_certified", "bilingual"],
                "max_capacity": 8,
                "status": "scheduled",
                "actual_start_time": None,
                "actual_end_time": None,
                "is_extended": False,
                "completion_notes": None
            }
        }

class ShiftCreate(BaseModel):
    date: str
    shift_type: ShiftType
    department: str
    start_time: str
    end_time: str
    required_staff: Dict[str, int]
    minimum_skill_level: int = Field(ge=1, le=10)
    priority: Priority = Priority.MEDIUM
    special_requirements: List[str] = []
    max_capacity: int = 5
    status: ShiftStatus = ShiftStatus.SCHEDULED

class ShiftUpdate(BaseModel):
    date: Optional[str] = None
    shift_type: Optional[ShiftType] = None
    department: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    required_staff: Optional[Dict[str, int]] = None
    minimum_skill_level: Optional[int] = None
    priority: Optional[Priority] = None
    special_requirements: Optional[List[str]] = None
    max_capacity: Optional[int] = None
    status: Optional[ShiftStatus] = None
    actual_start_time: Optional[str] = None
    actual_end_time: Optional[str] = None
    is_extended: Optional[bool] = None
    completion_notes: Optional[str] = None
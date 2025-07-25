# # backend/app/models/allocation.py

# from pydantic import BaseModel, Field
# from typing import List, Optional, Dict, Any
# from enum import Enum
# from datetime import datetime

# class AllocationStatus(str, Enum):
#     PENDING = "pending"
#     CONFIRMED = "confirmed"
#     REJECTED = "rejected"
#     COMPLETED = "completed"

# class AllocationRecord(BaseModel):
#     id: str
#     staff_id: str
#     shift_id: str
#     status: AllocationStatus = AllocationStatus.PENDING
#     assigned_at: Optional[str] = None
#     confidence_score: float = Field(ge=0.0, le=1.0, description="AI confidence in this allocation")
#     reasoning: str = Field(description="AI reasoning for this allocation")
#     constraints_met: List[str] = Field(default=[], description="List of constraints satisfied")
#     potential_issues: List[str] = Field(default=[], description="Potential issues with this allocation")
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "id": "allocation_001",
#                 "staff_id": "staff_001",
#                 "shift_id": "shift_001",
#                 "status": "confirmed",
#                 "assigned_at": "2024-07-13T10:30:00",
#                 "confidence_score": 0.92,
#                 "reasoning": "Dr. Johnson is highly skilled in emergency care and available during this time slot",
#                 "constraints_met": ["skill_level", "availability", "department_match"],
#                 "potential_issues": []
#             }
#         }

# class AllocationRequest(BaseModel):
#     shift_ids: List[str] = Field(description="List of shift IDs to allocate staff for")
#     preferences: Dict[str, Any] = Field(default={}, description="Allocation preferences")
#     constraints: Dict[str, Any] = Field(default={}, description="Hard constraints")
#     optimize_for: str = Field(default="balance", description="Optimization strategy: cost, quality, balance")

# class AllocationResult(BaseModel):
#     success: bool
#     message: str
#     allocations: List[AllocationRecord]
#     unallocated_shifts: List[str] = Field(default=[], description="Shifts that couldn't be allocated")
#     optimization_score: float = Field(ge=0.0, le=1.0, description="Overall optimization score")
#     total_cost: float = Field(ge=0.0, description="Total cost of allocations")
#     recommendations: List[str] = Field(default=[], description="AI recommendations for improvement")

# class AllocationSummary(BaseModel):
#     date_range: str
#     total_shifts: int
#     allocated_shifts: int
#     unallocated_shifts: int
#     total_staff_hours: float
#     average_utilization: float
#     departments: Dict[str, int]
#     cost_breakdown: Dict[str, float]

# backend/app/models/allocation.py

from pydantic import BaseModel, Field, computed_field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timedelta

class AllocationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    COMPLETED = "completed"

class AllocationRecord(BaseModel):
    id: str
    staff_id: str
    shift_id: str
    status: AllocationStatus = AllocationStatus.PENDING
    assigned_at: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0, description="AI confidence in this allocation")
    reasoning: str = Field(description="AI reasoning for this allocation")
    constraints_met: List[str] = Field(default=[], description="List of constraints satisfied")
    potential_issues: List[str] = Field(default=[], description="Potential issues with this allocation")
    
    # NEW FIELDS FOR ATTENDANCE TRACKING
    checked_in_at: Optional[str] = Field(default=None, description="Timestamp when staff checked in (ISO format)")
    checked_out_at: Optional[str] = Field(default=None, description="Timestamp when staff checked out (ISO format)")
    is_present: bool = Field(default=False, description="Whether staff is currently present for this shift")
    overtime_hours: float = Field(default=0.0, description="Number of overtime hours worked")
    
    @computed_field
    @property
    def hours_worked(self) -> float:
        """Calculate hours worked based on check-in and check-out times"""
        if not self.checked_in_at or not self.checked_out_at:
            return 0.0
        
        try:
            check_in = datetime.fromisoformat(self.checked_in_at.replace('Z', '+00:00'))
            check_out = datetime.fromisoformat(self.checked_out_at.replace('Z', '+00:00'))
            
            duration = check_out - check_in
            hours = duration.total_seconds() / 3600
            return round(hours, 2)
        except (ValueError, AttributeError):
            return 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "allocation_001",
                "staff_id": "staff_001",
                "shift_id": "shift_001",
                "status": "confirmed",
                "assigned_at": "2024-07-13T10:30:00",
                "confidence_score": 0.92,
                "reasoning": "Dr. Johnson is highly skilled in emergency care and available during this time slot",
                "constraints_met": ["skill_level", "availability", "department_match"],
                "potential_issues": [],
                "checked_in_at": "2024-07-15T08:00:00Z",
                "checked_out_at": "2024-07-15T16:00:00Z",
                "is_present": False,
                "overtime_hours": 0.0
            }
        }

class AllocationRequest(BaseModel):
    shift_ids: List[str] = Field(description="List of shift IDs to allocate staff for")
    preferences: Dict[str, Any] = Field(default={}, description="Allocation preferences")
    constraints: Dict[str, Any] = Field(default={}, description="Hard constraints")
    optimize_for: str = Field(default="balance", description="Optimization strategy: cost, quality, balance")

class AllocationResult(BaseModel):
    success: bool
    message: str
    allocations: List[AllocationRecord]
    unallocated_shifts: List[str] = Field(default=[], description="Shifts that couldn't be allocated")
    optimization_score: float = Field(ge=0.0, le=1.0, description="Overall optimization score")
    total_cost: float = Field(ge=0.0, description="Total cost of allocations")
    recommendations: List[str] = Field(default=[], description="AI recommendations for improvement")

class AllocationSummary(BaseModel):
    date_range: str
    total_shifts: int
    allocated_shifts: int
    unallocated_shifts: int
    total_staff_hours: float
    average_utilization: float
    departments: Dict[str, int]
    cost_breakdown: Dict[str, float]
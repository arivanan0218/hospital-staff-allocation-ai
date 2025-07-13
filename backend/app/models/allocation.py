# backend/app/models/allocation.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

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
                "potential_issues": []
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
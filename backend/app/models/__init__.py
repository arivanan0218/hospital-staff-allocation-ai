# backend/app/models/__init__.py
"""
Data models for the hospital staff allocation system
"""

from .staff import StaffMember, StaffCreate, StaffUpdate, StaffRole, Department
from .shift import Shift, ShiftCreate, ShiftUpdate, ShiftType, Priority
from .allocation import AllocationRecord, AllocationRequest, AllocationResult, AllocationSummary, AllocationStatus

__all__ = [
    "StaffMember", "StaffCreate", "StaffUpdate", "StaffRole", "Department",
    "Shift", "ShiftCreate", "ShiftUpdate", "ShiftType", "Priority",
    "AllocationRecord", "AllocationRequest", "AllocationResult", "AllocationSummary", "AllocationStatus"
]

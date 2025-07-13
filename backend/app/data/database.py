# backend/app/data/database.py

from typing import List, Optional, Dict, Any
from app.models.staff import StaffMember, StaffCreate, StaffUpdate
from app.models.shift import Shift, ShiftCreate, ShiftUpdate
from app.models.allocation import AllocationRecord
from app.data.mock_data import MOCK_STAFF, MOCK_SHIFTS, MOCK_ALLOCATIONS
import uuid
from datetime import datetime

class Database:
    """In-memory database for development and testing"""
    
    def __init__(self):
        self.staff: List[StaffMember] = MOCK_STAFF.copy()
        self.shifts: List[Shift] = MOCK_SHIFTS.copy()
        self.allocations: List[AllocationRecord] = MOCK_ALLOCATIONS.copy()
    
    # Staff Operations
    def get_all_staff(self) -> List[StaffMember]:
        return self.staff.copy()
    
    def get_staff_by_id(self, staff_id: str) -> Optional[StaffMember]:
        return next((staff for staff in self.staff if staff.id == staff_id), None)
    
    def create_staff(self, staff_data: StaffCreate) -> StaffMember:
        staff_id = f"staff_{uuid.uuid4().hex[:8]}"
        new_staff = StaffMember(id=staff_id, **staff_data.dict())
        self.staff.append(new_staff)
        return new_staff
    
    def update_staff(self, staff_id: str, staff_update: StaffUpdate) -> Optional[StaffMember]:
        staff = self.get_staff_by_id(staff_id)
        if staff:
            update_data = staff_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(staff, field, value)
            return staff
        return None
    
    def delete_staff(self, staff_id: str) -> bool:
        staff = self.get_staff_by_id(staff_id)
        if staff:
            self.staff.remove(staff)
            return True
        return False
    
    def get_staff_by_department(self, department: str) -> List[StaffMember]:
        return [staff for staff in self.staff if staff.department.value == department]
    
    def get_staff_by_role(self, role: str) -> List[StaffMember]:
        return [staff for staff in self.staff if staff.role.value == role]
    
    # Shift Operations
    def get_all_shifts(self) -> List[Shift]:
        return self.shifts.copy()
    
    def get_shift_by_id(self, shift_id: str) -> Optional[Shift]:
        return next((shift for shift in self.shifts if shift.id == shift_id), None)
    
    def create_shift(self, shift_data: ShiftCreate) -> Shift:
        shift_id = f"shift_{uuid.uuid4().hex[:8]}"
        new_shift = Shift(id=shift_id, **shift_data.dict())
        self.shifts.append(new_shift)
        return new_shift
    
    def update_shift(self, shift_id: str, shift_update: ShiftUpdate) -> Optional[Shift]:
        shift = self.get_shift_by_id(shift_id)
        if shift:
            update_data = shift_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(shift, field, value)
            return shift
        return None
    
    def delete_shift(self, shift_id: str) -> bool:
        shift = self.get_shift_by_id(shift_id)
        if shift:
            self.shifts.remove(shift)
            return True
        return False
    
    def get_shifts_by_date(self, date: str) -> List[Shift]:
        return [shift for shift in self.shifts if shift.date == date]
    
    def get_shifts_by_department(self, department: str) -> List[Shift]:
        return [shift for shift in self.shifts if shift.department == department]
    
    # Allocation Operations
    def get_all_allocations(self) -> List[AllocationRecord]:
        return self.allocations.copy()
    
    def get_allocation_by_id(self, allocation_id: str) -> Optional[AllocationRecord]:
        return next((alloc for alloc in self.allocations if alloc.id == allocation_id), None)
    
    def create_allocation(self, allocation: AllocationRecord) -> AllocationRecord:
        self.allocations.append(allocation)
        return allocation
    
    def get_allocations_by_staff(self, staff_id: str) -> List[AllocationRecord]:
        return [alloc for alloc in self.allocations if alloc.staff_id == staff_id]
    
    def get_allocations_by_shift(self, shift_id: str) -> List[AllocationRecord]:
        return [alloc for alloc in self.allocations if alloc.shift_id == shift_id]
    
    def get_allocations_by_date(self, date: str) -> List[AllocationRecord]:
        shift_ids = [shift.id for shift in self.get_shifts_by_date(date)]
        return [alloc for alloc in self.allocations if alloc.shift_id in shift_ids]
    
    def update_allocation_status(self, allocation_id: str, status: str) -> Optional[AllocationRecord]:
        allocation = self.get_allocation_by_id(allocation_id)
        if allocation:
            allocation.status = status
            if status == "confirmed":
                allocation.assigned_at = datetime.now().isoformat()
            return allocation
        return None
    
    def delete_allocation(self, allocation_id: str) -> bool:
        allocation = self.get_allocation_by_id(allocation_id)
        if allocation:
            self.allocations.remove(allocation)
            return True
        return False
    
    # Analytics and Summary Operations
    def get_staff_utilization(self) -> Dict[str, Any]:
        """Calculate staff utilization statistics"""
        total_staff = len(self.staff)
        allocated_staff = len(set(alloc.staff_id for alloc in self.allocations))
        
        return {
            "total_staff": total_staff,
            "allocated_staff": allocated_staff,
            "utilization_rate": allocated_staff / total_staff if total_staff > 0 else 0,
            "unallocated_staff": total_staff - allocated_staff
        }
    
    def get_shift_coverage(self) -> Dict[str, Any]:
        """Calculate shift coverage statistics"""
        total_shifts = len(self.shifts)
        covered_shifts = len(set(alloc.shift_id for alloc in self.allocations))
        
        return {
            "total_shifts": total_shifts,
            "covered_shifts": covered_shifts,
            "coverage_rate": covered_shifts / total_shifts if total_shifts > 0 else 0,
            "uncovered_shifts": total_shifts - covered_shifts
        }

# Global database instance
db = Database()
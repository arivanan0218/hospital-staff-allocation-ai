# # backend/app/data/database.py

# from typing import List, Optional, Dict, Any
# from app.models.staff import StaffMember, StaffCreate, StaffUpdate
# from app.models.shift import Shift, ShiftCreate, ShiftUpdate
# from app.models.allocation import AllocationRecord
# from app.data.mock_data import MOCK_STAFF, MOCK_SHIFTS, MOCK_ALLOCATIONS
# import uuid
# from datetime import datetime

# class Database:
#     """In-memory database for development and testing"""
    
#     def __init__(self):
#         self.staff: List[StaffMember] = MOCK_STAFF.copy()
#         self.shifts: List[Shift] = MOCK_SHIFTS.copy()
#         self.allocations: List[AllocationRecord] = MOCK_ALLOCATIONS.copy()
    
#     # Staff Operations
#     def get_all_staff(self) -> List[StaffMember]:
#         return self.staff.copy()
    
#     def get_staff_by_id(self, staff_id: str) -> Optional[StaffMember]:
#         return next((staff for staff in self.staff if staff.id == staff_id), None)
    
#     def create_staff(self, staff_data: StaffCreate) -> StaffMember:
#         staff_id = f"staff_{uuid.uuid4().hex[:8]}"
#         new_staff = StaffMember(id=staff_id, **staff_data.dict())
#         self.staff.append(new_staff)
#         return new_staff
    
#     def update_staff(self, staff_id: str, staff_update: StaffUpdate) -> Optional[StaffMember]:
#         staff = self.get_staff_by_id(staff_id)
#         if staff:
#             update_data = staff_update.dict(exclude_unset=True)
#             for field, value in update_data.items():
#                 setattr(staff, field, value)
#             return staff
#         return None
    
#     def delete_staff(self, staff_id: str) -> bool:
#         staff = self.get_staff_by_id(staff_id)
#         if staff:
#             self.staff.remove(staff)
#             return True
#         return False
    
#     def get_staff_by_department(self, department: str) -> List[StaffMember]:
#         return [staff for staff in self.staff if staff.department.value == department]
    
#     def get_staff_by_role(self, role: str) -> List[StaffMember]:
#         return [staff for staff in self.staff if staff.role.value == role]
    
#     # Shift Operations
#     def get_all_shifts(self) -> List[Shift]:
#         return self.shifts.copy()
    
#     def get_shift_by_id(self, shift_id: str) -> Optional[Shift]:
#         return next((shift for shift in self.shifts if shift.id == shift_id), None)
    
#     def create_shift(self, shift_data: ShiftCreate) -> Shift:
#         shift_id = f"shift_{uuid.uuid4().hex[:8]}"
#         new_shift = Shift(id=shift_id, **shift_data.dict())
#         self.shifts.append(new_shift)
#         return new_shift
    
#     def update_shift(self, shift_id: str, shift_update: ShiftUpdate) -> Optional[Shift]:
#         shift = self.get_shift_by_id(shift_id)
#         if shift:
#             update_data = shift_update.dict(exclude_unset=True)
#             for field, value in update_data.items():
#                 setattr(shift, field, value)
#             return shift
#         return None
    
#     def delete_shift(self, shift_id: str) -> bool:
#         shift = self.get_shift_by_id(shift_id)
#         if shift:
#             self.shifts.remove(shift)
#             return True
#         return False
    
#     def get_shifts_by_date(self, date: str) -> List[Shift]:
#         return [shift for shift in self.shifts if shift.date == date]
    
#     def get_shifts_by_department(self, department: str) -> List[Shift]:
#         return [shift for shift in self.shifts if shift.department == department]
    
#     # Allocation Operations
#     def get_all_allocations(self) -> List[AllocationRecord]:
#         return self.allocations.copy()
    
#     def get_allocation_by_id(self, allocation_id: str) -> Optional[AllocationRecord]:
#         return next((alloc for alloc in self.allocations if alloc.id == allocation_id), None)
    
#     def create_allocation(self, allocation: AllocationRecord) -> AllocationRecord:
#         self.allocations.append(allocation)
#         return allocation
    
#     def get_allocations_by_staff(self, staff_id: str) -> List[AllocationRecord]:
#         return [alloc for alloc in self.allocations if alloc.staff_id == staff_id]
    
#     def get_allocations_by_shift(self, shift_id: str) -> List[AllocationRecord]:
#         return [alloc for alloc in self.allocations if alloc.shift_id == shift_id]
    
#     def get_allocations_by_date(self, date: str) -> List[AllocationRecord]:
#         shift_ids = [shift.id for shift in self.get_shifts_by_date(date)]
#         return [alloc for alloc in self.allocations if alloc.shift_id in shift_ids]
    
#     def update_allocation_status(self, allocation_id: str, status: str) -> Optional[AllocationRecord]:
#         allocation = self.get_allocation_by_id(allocation_id)
#         if allocation:
#             allocation.status = status
#             if status == "confirmed":
#                 allocation.assigned_at = datetime.now().isoformat()
#             return allocation
#         return None
    
#     def delete_allocation(self, allocation_id: str) -> bool:
#         allocation = self.get_allocation_by_id(allocation_id)
#         if allocation:
#             self.allocations.remove(allocation)
#             return True
#         return False
    
#     # Analytics and Summary Operations
#     def get_staff_utilization(self) -> Dict[str, Any]:
#         """Calculate staff utilization statistics"""
#         total_staff = len(self.staff)
#         allocated_staff = len(set(alloc.staff_id for alloc in self.allocations))
        
#         return {
#             "total_staff": total_staff,
#             "allocated_staff": allocated_staff,
#             "utilization_rate": allocated_staff / total_staff if total_staff > 0 else 0,
#             "unallocated_staff": total_staff - allocated_staff
#         }
    
#     def get_shift_coverage(self) -> Dict[str, Any]:
#         """Calculate shift coverage statistics"""
#         total_shifts = len(self.shifts)
#         covered_shifts = len(set(alloc.shift_id for alloc in self.allocations))
        
#         return {
#             "total_shifts": total_shifts,
#             "covered_shifts": covered_shifts,
#             "coverage_rate": covered_shifts / total_shifts if total_shifts > 0 else 0,
#             "uncovered_shifts": total_shifts - covered_shifts
#         }

# # Global database instance
# db = Database()


# backend/app/data/database.py

from typing import List, Optional, Dict, Any
from app.models.staff import StaffMember, StaffCreate, StaffUpdate
from app.models.shift import Shift, ShiftCreate, ShiftUpdate, ShiftStatus
from app.models.allocation import AllocationRecord, AllocationStatus
from app.models.staff_availability import StaffAvailability, StaffAvailabilityCreate, StaffAvailabilityUpdate, AvailabilityStatus, AvailabilityTimeline
from app.data.mock_data import MOCK_STAFF, MOCK_SHIFTS, MOCK_ALLOCATIONS
import uuid
from datetime import datetime, time

class Database:
    """In-memory database for development and testing"""
    
    def __init__(self):
        self.staff: List[StaffMember] = MOCK_STAFF.copy()
        self.shifts: List[Shift] = MOCK_SHIFTS.copy()
        self.allocations: List[AllocationRecord] = MOCK_ALLOCATIONS.copy()
        
        # NEW: Staff availability tracking
        self.staff_availability: List[StaffAvailability] = []
        self.availability_timeline: List[AvailabilityTimeline] = []
        
        # Initialize staff availability records
        self._initialize_staff_availability()
    
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
    
    # NEW METHODS FOR SHIFT LIFECYCLE MANAGEMENT
    
    def _initialize_staff_availability(self):
        """Initialize availability records for all staff"""
        current_time = datetime.now().isoformat()
        
        for staff_member in self.staff:
            availability = StaffAvailability(
                id=f"avail_{staff_member.id}",
                staff_id=staff_member.id,
                status=AvailabilityStatus.AVAILABLE,
                current_shift_id=None,
                available_from=current_time,
                last_updated=current_time,
                location=staff_member.department.value,
                notes="Initialized as available"
            )
            self.staff_availability.append(availability)
    
    def update_shift_status(self, shift_id: str, status: ShiftStatus, 
                           actual_start_time: str = None, actual_end_time: str = None,
                           completion_notes: str = None) -> Optional[Shift]:
        """Update shift status and related fields"""
        shift = self.get_shift_by_id(shift_id)
        if not shift:
            return None
        
        # Update shift status
        shift.status = status
        
        if actual_start_time:
            shift.actual_start_time = actual_start_time
        
        if actual_end_time:
            shift.actual_end_time = actual_end_time
        
        if completion_notes:
            shift.completion_notes = completion_notes
        
        # Check for overtime
        if actual_end_time and shift.end_time:
            # Simple check - in reality would parse times properly
            shift.is_extended = actual_end_time > shift.end_time
        
        # Update staff availability if shift completed
        if status == ShiftStatus.COMPLETED:
            self._release_staff_from_shift(shift_id)
        elif status == ShiftStatus.IN_PROGRESS:
            self._mark_staff_working(shift_id)
        
        return shift
    
    def get_shifts_by_status(self, status: ShiftStatus) -> List[Shift]:
        """Get shifts by status"""
        return [shift for shift in self.shifts if shift.status == status]
    
    def get_active_shifts(self) -> List[Shift]:
        """Get all currently active shifts"""
        return self.get_shifts_by_status(ShiftStatus.IN_PROGRESS)
    
    def get_ending_soon_shifts(self, hours_ahead: int = 2) -> List[Shift]:
        """Get shifts ending within specified hours"""
        # Simplified implementation - in reality would check actual times
        current_time = datetime.now()
        ending_soon = []
        
        for shift in self.get_shifts_by_status(ShiftStatus.IN_PROGRESS):
            # Simple logic - could be enhanced with proper time parsing
            ending_soon.append(shift)
        
        return ending_soon
    
    def bulk_complete_shifts(self, shift_ids: List[str]) -> Dict[str, bool]:
        """Bulk complete multiple shifts"""
        results = {}
        current_time = datetime.now().isoformat()
        
        for shift_id in shift_ids:
            try:
                updated_shift = self.update_shift_status(
                    shift_id, 
                    ShiftStatus.completed,
                    actual_end_time=current_time,
                    completion_notes="Bulk completion"
                )
                results[shift_id] = updated_shift is not None
            except Exception:
                results[shift_id] = False
        
        return results
    
    # STAFF AVAILABILITY MANAGEMENT
    
    def get_staff_availability(self, staff_id: str) -> Optional[StaffAvailability]:
        """Get current availability for a staff member"""
        return next((avail for avail in self.staff_availability if avail.staff_id == staff_id), None)
    
    def get_available_staff(self, include_on_break: bool = False) -> List[StaffAvailability]:
        """Get all currently available staff"""
        statuses = [AvailabilityStatus.AVAILABLE]
        if include_on_break:
            statuses.append(AvailabilityStatus.ON_BREAK)
        
        return [avail for avail in self.staff_availability if avail.status in statuses]
    
    def update_staff_availability(self, staff_id: str, status: AvailabilityStatus,
                                current_shift_id: str = None, available_from: str = None,
                                location: str = None, notes: str = None,
                                changed_by: str = "system") -> Optional[StaffAvailability]:
        """Update staff availability status"""
        availability = self.get_staff_availability(staff_id)
        if not availability:
            return None
        
        # Record timeline change
        timeline_entry = AvailabilityTimeline(
            id=f"timeline_{uuid.uuid4().hex[:8]}",
            staff_id=staff_id,
            status=status,
            changed_at=datetime.now().isoformat(),
            changed_by=changed_by,
            reason=f"Status changed from {availability.status} to {status}",
            shift_id=current_shift_id
        )
        self.availability_timeline.append(timeline_entry)
        
        # Update availability
        availability.status = status
        availability.last_updated = datetime.now().isoformat()
        
        if current_shift_id is not None:
            availability.current_shift_id = current_shift_id
        
        if available_from is not None:
            availability.available_from = available_from
        
        if location is not None:
            availability.location = location
        
        if notes is not None:
            availability.notes = notes
        
        return availability
    
    def _mark_staff_working(self, shift_id: str):
        """Mark all allocated staff as working for this shift"""
        shift_allocations = self.get_allocations_by_shift(shift_id)
        
        for allocation in shift_allocations:
            if allocation.status == AllocationStatus.CONFIRMED:
                self.update_staff_availability(
                    allocation.staff_id,
                    AvailabilityStatus.WORKING,
                    current_shift_id=shift_id,
                    notes=f"Working shift {shift_id}"
                )
    
    def _release_staff_from_shift(self, shift_id: str):
        """Release staff from shift and mark them as available"""
        shift_allocations = self.get_allocations_by_shift(shift_id)
        current_time = datetime.now().isoformat()
        
        for allocation in shift_allocations:
            if allocation.status == AllocationStatus.CONFIRMED:
                self.update_staff_availability(
                    allocation.staff_id,
                    AvailabilityStatus.AVAILABLE,
                    current_shift_id=None,
                    available_from=current_time,
                    notes=f"Released from completed shift {shift_id}"
                )
    
    def check_in_staff(self, staff_id: str, shift_id: str) -> Optional[AllocationRecord]:
        """Check in staff for their shift"""
        allocation = next(
            (alloc for alloc in self.allocations 
             if alloc.staff_id == staff_id and alloc.shift_id == shift_id), 
            None
        )
        
        if allocation:
            allocation.checked_in_at = datetime.now().isoformat()
            allocation.is_present = True
            
            # Update staff availability
            self.update_staff_availability(
                staff_id,
                AvailabilityStatus.WORKING,
                current_shift_id=shift_id,
                notes=f"Checked in for shift {shift_id}"
            )
            
            # Update shift status if this is the first check-in
            shift = self.get_shift_by_id(shift_id)
            if shift and shift.status == ShiftStatus.SCHEDULED:
                self.update_shift_status(shift_id, ShiftStatus.IN_PROGRESS, 
                                       actual_start_time=allocation.checked_in_at)
        
        return allocation
    
    def check_out_staff(self, staff_id: str, shift_id: str) -> Optional[AllocationRecord]:
        allocation = next(
            (alloc for alloc in self.allocations 
             if alloc.staff_id == staff_id and alloc.shift_id == shift_id),
            None
        )
        
        if allocation:
            allocation.checked_out_at = datetime.now().isoformat()
            allocation.is_present = False
            
            # Calculate overtime if any
            if allocation.hours_worked > 8:  # Assuming 8-hour standard shift
                allocation.overtime_hours = allocation.hours_worked - 8
            
            # Update staff availability
            self.update_staff_availability(
                staff_id,
                AvailabilityStatus.AVAILABLE,
                current_shift_id=None,
                available_from=allocation.checked_out_at,
                notes=f"Checked out from shift {shift_id}"
            )
        
        return allocation
    
    def get_availability_timeline(self, staff_id: str, limit: int = 50) -> List[AvailabilityTimeline]:
        """Get availability timeline for a staff member"""
        timeline = [entry for entry in self.availability_timeline if entry.staff_id == staff_id]
        return sorted(timeline, key=lambda x: x.changed_at, reverse=True)[:limit]
    
    def _release_completed_shifts(self):
        """Release staff from shifts that have ended"""
        current_time = datetime.now()
        
        for shift in self.shifts:
            if shift.status != ShiftStatus.IN_PROGRESS:
                continue
                
            try:
                # Parse shift end time
                shift_date = datetime.strptime(shift.date, "%Y-%m-%d").date()
                end_hour, end_minute = map(int, shift.end_time.split(':'))
                shift_end = datetime.combine(shift_date, time(end_hour, end_minute))
                
                # If current time is past shift end time
                if current_time > shift_end:
                    # Update shift status
                    self.update_shift_status(
                        shift.id,
                        ShiftStatus.COMPLETED,
                        actual_end_time=current_time.isoformat(),
                        completion_notes="Shift automatically completed"
                    )
                    
            except Exception as e:
                print(f"Error processing shift {shift.id}: {str(e)}")
                continue
    
    def get_working_staff(self) -> List[StaffMember]:
        """Get all currently working staff"""
        # First check for any shifts that need to be completed
        self._release_completed_shifts()
        
        # Then return staff with active shifts
        return [staff for staff in self.staff if hasattr(staff, 'current_shift_id') and staff.current_shift_id]
    
    def get_staff_current_shift(self, staff_id: str) -> Optional[Shift]:
        """Get the current shift a staff member is working"""
        availability = self.get_staff_availability(staff_id)
        
        if availability and availability.current_shift_id:
            return self.get_shift_by_id(availability.current_shift_id)
        
        return None

# Global database instance
db = Database()
# backend/app/routers/shifts.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.shift import Shift, ShiftCreate, ShiftUpdate
from app.data.database import db

router = APIRouter(prefix="/api/shifts", tags=["shifts"])

@router.get("/", response_model=List[Shift])
async def get_all_shifts():
    """Get all shifts"""
    return db.get_all_shifts()

@router.get("/{shift_id}", response_model=Shift)
async def get_shift_by_id(shift_id: str):
    """Get shift by ID"""
    shift = db.get_shift_by_id(shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift

@router.post("/", response_model=Shift)
async def create_shift(shift_data: ShiftCreate):
    """Create new shift"""
    return db.create_shift(shift_data)

@router.put("/{shift_id}", response_model=Shift)
async def update_shift(shift_id: str, shift_update: ShiftUpdate):
    """Update shift"""
    shift = db.update_shift(shift_id, shift_update)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift

@router.delete("/{shift_id}")
async def delete_shift(shift_id: str):
    """Delete shift"""
    success = db.delete_shift(shift_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shift not found")
    return {"message": "Shift deleted successfully"}

@router.get("/date/{date}", response_model=List[Shift])
async def get_shifts_by_date(date: str):
    """Get shifts by date (YYYY-MM-DD format)"""
    return db.get_shifts_by_date(date)

@router.get("/department/{department}", response_model=List[Shift])
async def get_shifts_by_department(department: str):
    """Get shifts by department"""
    return db.get_shifts_by_department(department)

@router.get("/search/", response_model=List[Shift])
async def search_shifts(
    date: Optional[str] = Query(None, description="Filter by date"),
    department: Optional[str] = Query(None, description="Filter by department"),
    shift_type: Optional[str] = Query(None, description="Filter by shift type"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """Search shifts with multiple filters"""
    shifts = db.get_all_shifts()
    
    # Apply filters
    if date:
        shifts = [s for s in shifts if s.date == date]
    
    if department:
        shifts = [s for s in shifts if s.department.lower() == department.lower()]
    
    if shift_type:
        shifts = [s for s in shifts if s.shift_type.value.lower() == shift_type.lower()]
    
    if priority:
        shifts = [s for s in shifts if s.priority.value.lower() == priority.lower()]
    
    return shifts

@router.get("/{shift_id}/requirements")
async def get_shift_requirements(shift_id: str):
    """Get detailed requirements for a shift"""
    shift = db.get_shift_by_id(shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    # Get current allocations for this shift
    allocations = db.get_allocations_by_shift(shift_id)
    
    # Calculate fulfilled requirements
    fulfilled_roles = {}
    for allocation in allocations:
        staff = db.get_staff_by_id(allocation.staff_id)
        if staff and allocation.status == "confirmed":
            role = staff.role.value
            fulfilled_roles[role] = fulfilled_roles.get(role, 0) + 1
    
    # Calculate remaining requirements
    remaining_requirements = {}
    for role, required_count in shift.required_staff.items():
        fulfilled_count = fulfilled_roles.get(role, 0)
        remaining_requirements[role] = max(0, required_count - fulfilled_count)
    
    return {
        "shift_id": shift_id,
        "shift_details": shift,
        "required_staff": shift.required_staff,
        "fulfilled_staff": fulfilled_roles,
        "remaining_requirements": remaining_requirements,
        "current_allocations": len(allocations),
        "capacity_remaining": shift.max_capacity - len(allocations),
        "is_fully_staffed": all(count == 0 for count in remaining_requirements.values())
    }

@router.get("/analytics/coverage")
async def get_shift_coverage_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get shift coverage analytics"""
    
    shifts = db.get_all_shifts()
    allocations = db.get_all_allocations()
    
    # Filter by date range if provided
    if start_date or end_date:
        filtered_shifts = []
        for shift in shifts:
            include_shift = True
            if start_date and shift.date < start_date:
                include_shift = False
            if end_date and shift.date > end_date:
                include_shift = False
            if include_shift:
                filtered_shifts.append(shift)
        shifts = filtered_shifts
    
    # Calculate coverage metrics
    total_shifts = len(shifts)
    shift_ids = {shift.id for shift in shifts}
    
    covered_shifts = 0
    partially_covered_shifts = 0
    fully_covered_shifts = 0
    
    coverage_by_department = {}
    coverage_by_priority = {}
    
    for shift in shifts:
        shift_allocations = [a for a in allocations if a.shift_id == shift.id]
        confirmed_allocations = [a for a in shift_allocations if a.status == "confirmed"]
        
        # Count staff by role
        allocated_roles = {}
        for allocation in confirmed_allocations:
            staff = db.get_staff_by_id(allocation.staff_id)
            if staff:
                role = staff.role.value
                allocated_roles[role] = allocated_roles.get(role, 0) + 1
        
        # Check if requirements are met
        requirements_met = 0
        total_requirements = len(shift.required_staff)
        
        for role, required_count in shift.required_staff.items():
            allocated_count = allocated_roles.get(role, 0)
            if allocated_count >= required_count:
                requirements_met += 1
        
        # Categorize coverage
        if confirmed_allocations:
            covered_shifts += 1
            
            if requirements_met == total_requirements:
                fully_covered_shifts += 1
            else:
                partially_covered_shifts += 1
        
        # Department coverage
        dept = shift.department
        if dept not in coverage_by_department:
            coverage_by_department[dept] = {"total": 0, "covered": 0, "fully_covered": 0}
        
        coverage_by_department[dept]["total"] += 1
        if confirmed_allocations:
            coverage_by_department[dept]["covered"] += 1
        if requirements_met == total_requirements:
            coverage_by_department[dept]["fully_covered"] += 1
        
        # Priority coverage
        priority = shift.priority.value
        if priority not in coverage_by_priority:
            coverage_by_priority[priority] = {"total": 0, "covered": 0, "fully_covered": 0}
        
        coverage_by_priority[priority]["total"] += 1
        if confirmed_allocations:
            coverage_by_priority[priority]["covered"] += 1
        if requirements_met == total_requirements:
            coverage_by_priority[priority]["fully_covered"] += 1
    
    return {
        "summary": {
            "total_shifts": total_shifts,
            "covered_shifts": covered_shifts,
            "uncovered_shifts": total_shifts - covered_shifts,
            "fully_covered_shifts": fully_covered_shifts,
            "partially_covered_shifts": partially_covered_shifts,
            "coverage_rate": covered_shifts / total_shifts if total_shifts > 0 else 0,
            "full_coverage_rate": fully_covered_shifts / total_shifts if total_shifts > 0 else 0
        },
        "coverage_by_department": coverage_by_department,
        "coverage_by_priority": coverage_by_priority,
        "date_range": {
            "start_date": start_date or "all",
            "end_date": end_date or "all"
        }
    }
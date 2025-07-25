# backend/app/routers/staff.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.staff import StaffMember, StaffCreate, StaffUpdate
from app.services.staff_service import staff_service

router = APIRouter(prefix="/api/staff", tags=["staff"])

@router.get("/", response_model=List[StaffMember])
async def get_all_staff():
    """Get all staff members"""
    return await staff_service.get_all_staff()

@router.get("/{staff_id}", response_model=StaffMember)
async def get_staff_by_id(staff_id: str):
    """Get staff member by ID"""
    staff = await staff_service.get_staff_by_id(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff

@router.post("/", response_model=StaffMember)
async def create_staff(staff_data: StaffCreate):
    """Create new staff member"""
    return await staff_service.create_staff(staff_data)

@router.put("/{staff_id}", response_model=StaffMember)
async def update_staff(staff_id: str, staff_update: StaffUpdate):
    """Update staff member"""
    staff = await staff_service.update_staff(staff_id, staff_update)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff

@router.delete("/{staff_id}")
async def delete_staff(staff_id: str):
    """Delete staff member"""
    success = await staff_service.delete_staff(staff_id)
    if not success:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return {"message": "Staff member deleted successfully"}

@router.get("/department/{department}", response_model=List[StaffMember])
async def get_staff_by_department(department: str):
    """Get staff by department"""
    return await staff_service.get_staff_by_department(department)

@router.get("/role/{role}", response_model=List[StaffMember])
async def get_staff_by_role(role: str):
    """Get staff by role"""
    return await staff_service.get_staff_by_role(role)

@router.get("/working", response_model=List[StaffMember])
async def get_working_staff():
    """Get all currently working staff members"""
    working_staff = await staff_service.get_working_staff()
    if not working_staff:
        raise HTTPException(status_code=404, detail="No working staff found")
    return working_staff

@router.get("/available/current", response_model=List[StaffMember])
async def get_currently_available_staff():
    """Get all currently available staff members"""
    available_staff = await staff_service.get_available_staff_endpoint()
    if not available_staff:
        raise HTTPException(status_code=404, detail="No available staff found")
    return available_staff

@router.get("/available/for-date/{date}", response_model=List[StaffMember])
async def get_available_staff_for_date(
    date: str,
    department: Optional[str] = Query(None, description="Filter by department")
):
    """Get staff available on a specific date"""
    return await staff_service.get_available_staff(date, department)

@router.get("/analysis/skills")
async def get_staff_skills_analysis(
    department: Optional[str] = Query(None, description="Filter by department")
):
    """Get staff skills analysis"""
    return await staff_service.analyze_staff_skills(department)

@router.get("/analysis/workload")
async def get_staff_workload_analysis(
    staff_id: Optional[str] = Query(None, description="Specific staff member"),
    date_range: Optional[str] = Query(None, description="Date range for analysis")
):
    """Get staff workload analysis"""
    return await staff_service.get_staff_workload_analysis(staff_id, date_range)

@router.get("/suggestions/shift/{shift_id}")
async def get_staff_suggestions_for_shift(shift_id: str):
    """Get staff suggestions for a specific shift"""
    suggestions = await staff_service.suggest_staff_for_shift(shift_id)
    if not suggestions:
        raise HTTPException(status_code=404, detail="No suitable staff found or shift not found")
    return suggestions
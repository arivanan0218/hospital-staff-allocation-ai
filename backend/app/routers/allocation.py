# backend/app/routers/allocation.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.allocation import AllocationRecord, AllocationRequest, AllocationResult, AllocationSummary, AllocationStatus
from app.services.allocation_service import allocation_service

router = APIRouter(prefix="/api/allocations", tags=["allocations"])

@router.get("/", response_model=List[AllocationRecord])
async def get_all_allocations():
    """Get all allocations"""
    return await allocation_service.get_all_allocations()

@router.get("/{allocation_id}", response_model=AllocationRecord)
async def get_allocation_by_id(allocation_id: str):
    """Get allocation by ID"""
    allocation = await allocation_service.get_allocation_by_id(allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation

@router.post("/create", response_model=AllocationRecord)
async def create_allocation(
    staff_id: str,
    shift_id: str,
    confidence_score: float = 0.5,
    reasoning: str = "Manual allocation"
):
    """Create a new allocation manually"""
    allocation = await allocation_service.create_allocation(
        staff_id, shift_id, confidence_score, reasoning
    )
    if not allocation:
        raise HTTPException(status_code=400, detail="Failed to create allocation. Check if staff and shift exist.")
    return allocation

@router.post("/auto-allocate", response_model=AllocationResult)
async def auto_allocate_shifts(allocation_request: AllocationRequest):
    """Automatically allocate staff to shifts using AI"""
    return await allocation_service.auto_allocate_shifts(allocation_request)

@router.get("/staff/{staff_id}", response_model=List[AllocationRecord])
async def get_allocations_by_staff(staff_id: str):
    """Get allocations for a specific staff member"""
    return await allocation_service.get_allocations_by_staff(staff_id)

@router.get("/shift/{shift_id}", response_model=List[AllocationRecord])
async def get_allocations_by_shift(shift_id: str):
    """Get allocations for a specific shift"""
    return await allocation_service.get_allocations_by_shift(shift_id)

@router.get("/date/{date}", response_model=List[AllocationRecord])
async def get_allocations_by_date(date: str):
    """Get allocations for a specific date (YYYY-MM-DD format)"""
    return await allocation_service.get_allocations_by_date(date)

@router.put("/{allocation_id}/status")
async def update_allocation_status(allocation_id: str, status: AllocationStatus):
    """Update allocation status"""
    allocation = await allocation_service.update_allocation_status(allocation_id, status)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation

@router.delete("/{allocation_id}")
async def delete_allocation(allocation_id: str):
    """Delete allocation"""
    success = await allocation_service.delete_allocation(allocation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return {"message": "Allocation deleted successfully"}

@router.get("/summary/{date_range}", response_model=AllocationSummary)
async def get_allocation_summary(date_range: str):
    """Get allocation summary for a date range (e.g., '2024-07-15' or '2024-07-15 to 2024-07-20')"""
    return await allocation_service.get_allocation_summary(date_range)

@router.get("/{allocation_id}/validate")
async def validate_allocation(allocation_id: str):
    """Validate a specific allocation against constraints"""
    result = await allocation_service.validate_allocation(allocation_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/alternatives/shift/{shift_id}")
async def get_alternative_allocations(
    shift_id: str,
    exclude_staff: Optional[str] = Query(None, description="Comma-separated staff IDs to exclude")
):
    """Get alternative staff suggestions for a shift"""
    excluded_staff_ids = exclude_staff.split(",") if exclude_staff else []
    alternatives = await allocation_service.suggest_alternative_allocations(shift_id, excluded_staff_ids)
    if not alternatives:
        raise HTTPException(status_code=404, detail="No alternatives found or shift not found")
    return alternatives

@router.post("/optimize")
async def optimize_allocations(
    date_range: str,
    strategy: str = Query("balance", description="Optimization strategy: cost, quality, balance, satisfaction"),
    constraints: Optional[dict] = None
):
    """Optimize existing allocations"""
    result = await allocation_service.optimize_existing_allocations(date_range, strategy)
    return result

@router.get("/conflicts/{date_range}")
async def get_conflict_analysis(date_range: str):
    """Analyze conflicts in allocations for a date range"""
    return await allocation_service.get_conflict_analysis(date_range)

@router.get("/analytics/utilization")
async def get_utilization_analytics():
    """Get staff utilization analytics"""
    from app.data.database import db
    
    staff_utilization = db.get_staff_utilization()
    shift_coverage = db.get_shift_coverage()
    
    # Calculate additional metrics
    all_staff = db.get_all_staff()
    all_shifts = db.get_all_shifts()
    all_allocations = db.get_all_allocations()
    
    # Department utilization
    dept_utilization = {}
    for staff in all_staff:
        dept = staff.department.value
        if dept not in dept_utilization:
            dept_utilization[dept] = {"total_staff": 0, "allocated_staff": 0}
        dept_utilization[dept]["total_staff"] += 1
    
    for allocation in all_allocations:
        staff = db.get_staff_by_id(allocation.staff_id)
        if staff:
            dept = staff.department.value
            if dept in dept_utilization:
                dept_utilization[dept]["allocated_staff"] += 1
    
    # Calculate utilization rates
    for dept_data in dept_utilization.values():
        if dept_data["total_staff"] > 0:
            dept_data["utilization_rate"] = dept_data["allocated_staff"] / dept_data["total_staff"]
        else:
            dept_data["utilization_rate"] = 0
    
    # Role utilization
    role_utilization = {}
    for staff in all_staff:
        role = staff.role.value
        if role not in role_utilization:
            role_utilization[role] = {"total_staff": 0, "allocated_staff": 0}
        role_utilization[role]["total_staff"] += 1
    
    allocated_staff_ids = set()
    for allocation in all_allocations:
        allocated_staff_ids.add(allocation.staff_id)
    
    for staff in all_staff:
        if staff.id in allocated_staff_ids:
            role = staff.role.value
            if role in role_utilization:
                role_utilization[role]["allocated_staff"] += 1
    
    # Calculate role utilization rates
    for role_data in role_utilization.values():
        if role_data["total_staff"] > 0:
            role_data["utilization_rate"] = role_data["allocated_staff"] / role_data["total_staff"]
        else:
            role_data["utilization_rate"] = 0
    
    return {
        "overall": {
            "staff_utilization": staff_utilization,
            "shift_coverage": shift_coverage
        },
        "by_department": dept_utilization,
        "by_role": role_utilization,
        "summary": {
            "total_staff": len(all_staff),
            "total_shifts": len(all_shifts),
            "total_allocations": len(all_allocations),
            "average_allocations_per_staff": len(all_allocations) / len(all_staff) if all_staff else 0
        }
    }

@router.post("/batch-create")
async def create_batch_allocations(allocations_data: List[dict]):
    """Create multiple allocations in batch"""
    results = []
    
    for allocation_data in allocations_data:
        try:
            allocation = await allocation_service.create_allocation(
                staff_id=allocation_data.get("staff_id"),
                shift_id=allocation_data.get("shift_id"),
                confidence_score=allocation_data.get("confidence_score", 0.5),
                reasoning=allocation_data.get("reasoning", "Batch allocation")
            )
            
            if allocation:
                results.append({
                    "success": True,
                    "allocation": allocation,
                    "message": "Allocation created successfully"
                })
            else:
                results.append({
                    "success": False,
                    "allocation": None,
                    "message": "Failed to create allocation",
                    "input": allocation_data
                })
                
        except Exception as e:
            results.append({
                "success": False,
                "allocation": None,
                "message": f"Error: {str(e)}",
                "input": allocation_data
            })
    
    successful_count = sum(1 for result in results if result["success"])
    
    return {
        "summary": {
            "total_requests": len(allocations_data),
            "successful": successful_count,
            "failed": len(allocations_data) - successful_count
        },
        "results": results
    }
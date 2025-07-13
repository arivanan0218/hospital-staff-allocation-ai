# backend/app/services/allocation_service.py

from typing import List, Optional, Dict, Any
from app.models.allocation import AllocationRecord, AllocationRequest, AllocationResult, AllocationSummary, AllocationStatus
from app.models.shift import Shift
from app.models.staff import StaffMember
from app.data.database import db
from app.agents.allocation_agent import allocation_agent
from app.agents.constraint_agent import constraint_agent
from app.agents.optimization_agent import optimization_agent
from app.services.llm_service import llm_service
import uuid
from datetime import datetime, timedelta
import json

class AllocationService:
    """Service layer for staff allocation operations"""
    
    async def create_allocation(self, staff_id: str, shift_id: str, 
                              confidence_score: float = 0.5, 
                              reasoning: str = "Manual allocation") -> Optional[AllocationRecord]:
        """Create a new allocation"""
        
        # Validate staff and shift exist
        staff = db.get_staff_by_id(staff_id)
        shift = db.get_shift_by_id(shift_id)
        
        if not staff or not shift:
            return None
        
        # Create allocation record
        allocation = AllocationRecord(
            id=f"allocation_{uuid.uuid4().hex[:8]}",
            staff_id=staff_id,
            shift_id=shift_id,
            status=AllocationStatus.PENDING,
            confidence_score=confidence_score,
            reasoning=reasoning,
            constraints_met=[],
            potential_issues=[]
        )
        
        # Validate allocation against constraints
        validation_result = await constraint_agent.validate_allocation(allocation)
        
        # Update allocation based on validation
        allocation.constraints_met = list(validation_result["constraint_details"].keys())
        allocation.potential_issues = validation_result["violations"] + validation_result["warnings"]
        
        # Auto-confirm if validation passes
        if validation_result["is_valid"]:
            allocation.status = AllocationStatus.CONFIRMED
            allocation.assigned_at = datetime.now().isoformat()
        
        # Store in database
        return db.create_allocation(allocation)
    
    async def auto_allocate_shifts(self, allocation_request: AllocationRequest) -> AllocationResult:
        """Automatically allocate staff to shifts using AI"""
        
        try:
            # Get shift details
            shifts = []
            for shift_id in allocation_request.shift_ids:
                shift = db.get_shift_by_id(shift_id)
                if shift:
                    shifts.append(shift)
            
            if not shifts:
                return AllocationResult(
                    success=False,
                    message="No valid shifts found",
                    allocations=[],
                    unallocated_shifts=allocation_request.shift_ids,
                    optimization_score=0.0
                )
            
            # Use allocation agent to create allocations
            allocations = await allocation_agent.allocate_staff_to_shifts(
                allocation_request.shift_ids,
                allocation_request.preferences
            )
            
            # Validate all allocations
            validation_results = await constraint_agent.validate_multiple_allocations(allocations)
            
            # Separate valid and invalid allocations
            valid_allocations = []
            invalid_allocations = []
            
            for allocation in allocations:
                allocation_validation = validation_results["individual_validations"].get(allocation.id, {})
                if allocation_validation.get("is_valid", False):
                    allocation.status = AllocationStatus.CONFIRMED
                    allocation.assigned_at = datetime.now().isoformat()
                    valid_allocations.append(allocation)
                else:
                    allocation.status = AllocationStatus.REJECTED
                    invalid_allocations.append(allocation)
            
            # Calculate metrics
            unallocated_shifts = []
            allocated_shift_ids = {alloc.shift_id for alloc in valid_allocations}
            
            for shift_id in allocation_request.shift_ids:
                if shift_id not in allocated_shift_ids:
                    unallocated_shifts.append(shift_id)
            
            optimization_score = len(valid_allocations) / len(allocation_request.shift_ids) if allocation_request.shift_ids else 0.0
            
            # Calculate total cost
            total_cost = await self._calculate_allocation_cost(valid_allocations)
            
            # Generate recommendations
            recommendations = await self._generate_allocation_recommendations(
                valid_allocations, invalid_allocations, unallocated_shifts
            )
            
            return AllocationResult(
                success=len(valid_allocations) > 0,
                message=f"Successfully allocated {len(valid_allocations)} out of {len(allocation_request.shift_ids)} shifts",
                allocations=valid_allocations,
                unallocated_shifts=unallocated_shifts,
                optimization_score=optimization_score,
                total_cost=total_cost,
                recommendations=recommendations
            )
            
        except Exception as e:
            return AllocationResult(
                success=False,
                message=f"Error during allocation: {str(e)}",
                allocations=[],
                unallocated_shifts=allocation_request.shift_ids,
                optimization_score=0.0,
                total_cost=0.0,
                recommendations=["Manual allocation required due to system error"]
            )
    
    async def optimize_existing_allocations(self, date_range: str, strategy: str = "balance") -> Dict[str, Any]:
        """Optimize existing allocations"""
        
        try:
            optimization_result = await optimization_agent.optimize_schedule(
                date_range, strategy
            )
            
            return optimization_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "recommendations": ["Manual optimization required"]
            }
    
    async def get_allocation_by_id(self, allocation_id: str) -> Optional[AllocationRecord]:
        """Get allocation by ID"""
        return db.get_allocation_by_id(allocation_id)
    
    async def get_all_allocations(self) -> List[AllocationRecord]:
        """Get all allocations"""
        return db.get_all_allocations()
    
    async def get_allocations_by_staff(self, staff_id: str) -> List[AllocationRecord]:
        """Get allocations for a specific staff member"""
        return db.get_allocations_by_staff(staff_id)
    
    async def get_allocations_by_shift(self, shift_id: str) -> List[AllocationRecord]:
        """Get allocations for a specific shift"""
        return db.get_allocations_by_shift(shift_id)
    
    async def get_allocations_by_date(self, date: str) -> List[AllocationRecord]:
        """Get allocations for a specific date"""
        return db.get_allocations_by_date(date)
    
    async def update_allocation_status(self, allocation_id: str, status: AllocationStatus) -> Optional[AllocationRecord]:
        """Update allocation status"""
        return db.update_allocation_status(allocation_id, status.value)
    
    async def delete_allocation(self, allocation_id: str) -> bool:
        """Delete allocation"""
        return db.delete_allocation(allocation_id)
    
    async def get_allocation_summary(self, date_range: str) -> AllocationSummary:
        """Get allocation summary for a date range"""
        
        # Parse date range
        if " to " in date_range:
            start_date, end_date = date_range.split(" to ")
            start_date, end_date = start_date.strip(), end_date.strip()
        else:
            start_date = end_date = date_range.strip()
        
        # Get relevant shifts and allocations
        all_shifts = db.get_all_shifts()
        relevant_shifts = [s for s in all_shifts if start_date <= s.date <= end_date]
        
        all_allocations = db.get_all_allocations()
        relevant_allocations = []
        
        for allocation in all_allocations:
            shift = db.get_shift_by_id(allocation.shift_id)
            if shift and start_date <= shift.date <= end_date:
                relevant_allocations.append(allocation)
        
        # Calculate metrics
        total_shifts = len(relevant_shifts)
        allocated_shifts = len(set(alloc.shift_id for alloc in relevant_allocations))
        unallocated_shifts = total_shifts - allocated_shifts
        
        # Calculate staff hours
        total_staff_hours = 0.0
        for allocation in relevant_allocations:
            # Assume 8-hour shifts for simplicity
            total_staff_hours += 8.0
        
        # Calculate utilization
        all_staff = db.get_all_staff()
        total_possible_hours = sum(staff.max_hours_per_week for staff in all_staff) * (
            (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1
        ) / 7  # Convert to daily average
        
        average_utilization = total_staff_hours / total_possible_hours if total_possible_hours > 0 else 0.0
        
        # Department breakdown
        departments = {}
        for allocation in relevant_allocations:
            shift = db.get_shift_by_id(allocation.shift_id)
            if shift:
                dept = shift.department
                departments[dept] = departments.get(dept, 0) + 1
        
        # Cost breakdown
        cost_breakdown = await self._calculate_cost_breakdown(relevant_allocations)
        
        return AllocationSummary(
            date_range=date_range,
            total_shifts=total_shifts,
            allocated_shifts=allocated_shifts,
            unallocated_shifts=unallocated_shifts,
            total_staff_hours=total_staff_hours,
            average_utilization=min(average_utilization, 1.0),
            departments=departments,
            cost_breakdown=cost_breakdown
        )
    
    async def validate_allocation(self, allocation_id: str) -> Dict[str, Any]:
        """Validate a specific allocation"""
        
        allocation = db.get_allocation_by_id(allocation_id)
        if not allocation:
            return {"error": "Allocation not found"}
        
        return await constraint_agent.validate_allocation(allocation)
    
    async def suggest_alternative_allocations(self, shift_id: str, excluded_staff_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Suggest alternative staff for a shift"""
        
        shift = db.get_shift_by_id(shift_id)
        if not shift:
            return []
        
        # Get available staff
        all_staff = db.get_all_staff()
        available_staff = [
            staff for staff in all_staff
            if (shift.date not in staff.unavailable_dates and
                staff.skill_level >= shift.minimum_skill_level and
                (not excluded_staff_ids or staff.id not in excluded_staff_ids))
        ]
        
        suggestions = []
        
        for staff in available_staff:
            # Calculate suitability score
            score = await self._calculate_suitability_score(staff, shift)
            
            # Check constraints
            temp_allocation = AllocationRecord(
                id="temp",
                staff_id=staff.id,
                shift_id=shift_id,
                status=AllocationStatus.PENDING,
                confidence_score=score,
                reasoning="Alternative suggestion",
                constraints_met=[],
                potential_issues=[]
            )
            
            validation = await constraint_agent.validate_allocation(temp_allocation)
            
            suggestion = {
                "staff_id": staff.id,
                "name": staff.name,
                "role": staff.role.value,
                "department": staff.department.value,
                "suitability_score": score,
                "hourly_rate": staff.hourly_rate,
                "skill_level": staff.skill_level,
                "is_valid": validation["is_valid"],
                "potential_issues": validation["violations"] + validation["warnings"],
                "recommendation": "high" if score > 0.8 and validation["is_valid"] else "medium" if score > 0.6 else "low"
            }
            
            suggestions.append(suggestion)
        
        # Sort by suitability score and validity
        suggestions.sort(key=lambda x: (x["is_valid"], x["suitability_score"]), reverse=True)
        
        return suggestions[:5]  # Return top 5 alternatives
    
    async def get_conflict_analysis(self, date_range: str) -> Dict[str, Any]:
        """Analyze conflicts in allocations"""
        
        # Get allocations in date range
        if " to " in date_range:
            start_date, end_date = date_range.split(" to ")
            start_date, end_date = start_date.strip(), end_date.strip()
        else:
            start_date = end_date = date_range.strip()
        
        relevant_allocations = []
        all_allocations = db.get_all_allocations()
        
        for allocation in all_allocations:
            shift = db.get_shift_by_id(allocation.shift_id)
            if shift and start_date <= shift.date <= end_date:
                relevant_allocations.append(allocation)
        
        # Validate all allocations for conflicts
        validation_results = await constraint_agent.validate_multiple_allocations(relevant_allocations)
        
        conflicts = {
            "global_conflicts": validation_results["global_conflicts"],
            "individual_violations": [],
            "summary": {
                "total_allocations": len(relevant_allocations),
                "conflicted_allocations": 0,
                "critical_violations": 0,
                "warnings": 0
            }
        }
        
        # Process individual violations
        for allocation_id, validation in validation_results["individual_validations"].items():
            if not validation["is_valid"] or validation["warnings"]:
                allocation = db.get_allocation_by_id(allocation_id)
                if allocation:
                    conflicts["individual_violations"].append({
                        "allocation_id": allocation_id,
                        "staff_id": allocation.staff_id,
                        "shift_id": allocation.shift_id,
                        "violations": validation["violations"],
                        "warnings": validation["warnings"],
                        "severity_score": validation["severity_score"]
                    })
                    
                    if not validation["is_valid"]:
                        conflicts["summary"]["conflicted_allocations"] += 1
                        conflicts["summary"]["critical_violations"] += len(validation["violations"])
                    
                    conflicts["summary"]["warnings"] += len(validation["warnings"])
        
        return conflicts
    
    async def _calculate_allocation_cost(self, allocations: List[AllocationRecord]) -> float:
        """Calculate total cost of allocations"""
        
        total_cost = 0.0
        
        for allocation in allocations:
            staff = db.get_staff_by_id(allocation.staff_id)
            if staff:
                # Assume 8-hour shifts
                total_cost += staff.hourly_rate * 8
        
        return total_cost
    
    async def _calculate_cost_breakdown(self, allocations: List[AllocationRecord]) -> Dict[str, float]:
        """Calculate cost breakdown by department/role"""
        
        cost_breakdown = {
            "by_department": {},
            "by_role": {},
            "total": 0.0
        }
        
        for allocation in allocations:
            staff = db.get_staff_by_id(allocation.staff_id)
            shift = db.get_shift_by_id(allocation.shift_id)
            
            if staff and shift:
                cost = staff.hourly_rate * 8  # 8-hour shift
                
                # By department
                dept = shift.department
                cost_breakdown["by_department"][dept] = cost_breakdown["by_department"].get(dept, 0.0) + cost
                
                # By role
                role = staff.role.value
                cost_breakdown["by_role"][role] = cost_breakdown["by_role"].get(role, 0.0) + cost
                
                cost_breakdown["total"] += cost
        
        return cost_breakdown
    
    async def _calculate_suitability_score(self, staff: StaffMember, shift: Shift) -> float:
        """Calculate how suitable a staff member is for a shift"""
        
        score = 0.0
        
        # Skill level (30%)
        if staff.skill_level >= shift.minimum_skill_level:
            skill_score = min(staff.skill_level / 10.0, 1.0)
            score += skill_score * 0.3
        
        # Department match (25%)
        if staff.department.value == shift.department:
            score += 0.25
        
        # Shift preference (20%)
        if shift.shift_type.value in staff.preferred_shifts:
            score += 0.20
        
        # Experience (15%)
        exp_score = min(staff.experience_years / 15.0, 1.0)
        score += exp_score * 0.15
        
        # Availability (10%)
        if shift.date not in staff.unavailable_dates:
            score += 0.10
        
        return min(score, 1.0)
    
    async def _generate_allocation_recommendations(self, 
                                                 valid_allocations: List[AllocationRecord],
                                                 invalid_allocations: List[AllocationRecord],
                                                 unallocated_shifts: List[str]) -> List[str]:
        """Generate recommendations based on allocation results"""
        
        recommendations = []
        
        if invalid_allocations:
            recommendations.append(f"Review {len(invalid_allocations)} invalid allocations for constraint violations")
        
        if unallocated_shifts:
            recommendations.append(f"Find staff for {len(unallocated_shifts)} unallocated shifts")
            recommendations.append("Consider adjusting shift requirements or hiring additional staff")
        
        if len(valid_allocations) > 0:
            # Calculate average confidence
            avg_confidence = sum(alloc.confidence_score for alloc in valid_allocations) / len(valid_allocations)
            if avg_confidence < 0.7:
                recommendations.append("Low confidence scores suggest reviewing allocation criteria")
        
        # Use LLM for additional insights
        try:
            allocation_data = {
                "valid_allocations": len(valid_allocations),
                "invalid_allocations": len(invalid_allocations),
                "unallocated_shifts": len(unallocated_shifts)
            }
            
            prompt = f"""
            Based on the following allocation results, provide 2-3 actionable recommendations:
            
            {json.dumps(allocation_data, indent=2)}
            
            Focus on practical improvements for hospital staff scheduling.
            """
            
            llm_response = await llm_service.generate_response(prompt)
            
            # Extract recommendations from LLM response
            llm_recommendations = [line.strip() for line in llm_response.split('\n') 
                                 if line.strip() and len(line.strip()) > 10][:3]
            
            recommendations.extend(llm_recommendations)
            
        except Exception:
            pass  # LLM recommendations are optional
        
        return recommendations[:5]  # Limit to 5 recommendations

# Global allocation service instance
allocation_service = AllocationService()
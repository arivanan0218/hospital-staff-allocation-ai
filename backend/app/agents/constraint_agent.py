# backend/app/agents/constraint_agent.py

from typing import Dict, List, Any, Optional, Tuple
from app.services.llm_service import llm_service
from app.data.database import db
from app.models.allocation import AllocationRecord
from app.models.staff import StaffMember
from app.models.shift import Shift
from datetime import datetime, timedelta
import json

class ConstraintAgent:
    """AI Agent responsible for validating constraints and rules"""
    
    def __init__(self):
        self.constraint_rules = self._define_constraint_rules()
    
    def _define_constraint_rules(self) -> Dict[str, Dict[str, Any]]:
        """Define hospital-specific constraint rules"""
        return {
            "max_weekly_hours": {
                "description": "Staff cannot exceed maximum weekly hours",
                "severity": "critical",
                "check_function": self._check_weekly_hours
            },
            "skill_level_requirement": {
                "description": "Staff must meet minimum skill level for shift",
                "severity": "critical",
                "check_function": self._check_skill_level
            },
            "department_match": {
                "description": "Staff should be assigned to their department",
                "severity": "medium",
                "check_function": self._check_department_match
            },
            "availability_check": {
                "description": "Staff must be available on shift date",
                "severity": "critical",
                "check_function": self._check_availability
            },
            "minimum_rest_period": {
                "description": "Staff must have minimum rest between shifts",
                "severity": "high",
                "check_function": self._check_rest_period
            },
            "certification_requirements": {
                "description": "Staff must have required certifications",
                "severity": "critical",
                "check_function": self._check_certifications
            },
            "shift_capacity": {
                "description": "Shift cannot exceed maximum capacity",
                "severity": "critical",
                "check_function": self._check_shift_capacity
            },
            "role_requirements": {
                "description": "Shift must have required roles filled",
                "severity": "high",
                "check_function": self._check_role_requirements
            }
        }
    
    async def validate_allocation(self, allocation: AllocationRecord) -> Dict[str, Any]:
        """Validate a single allocation against all constraints"""
        
        validation_result = {
            "is_valid": True,
            "violations": [],
            "warnings": [],
            "suggestions": [],
            "severity_score": 0.0,
            "constraint_details": {}
        }
        
        staff = db.get_staff_by_id(allocation.staff_id)
        shift = db.get_shift_by_id(allocation.shift_id)
        
        if not staff or not shift:
            validation_result["is_valid"] = False
            validation_result["violations"].append("Staff or shift not found")
            validation_result["severity_score"] = 1.0
            return validation_result
        
        # Check each constraint rule
        total_violations = 0
        critical_violations = 0
        
        for rule_name, rule_config in self.constraint_rules.items():
            try:
                violation_data = rule_config["check_function"](allocation, staff, shift)
                
                if violation_data["violated"]:
                    total_violations += 1
                    
                    if rule_config["severity"] == "critical":
                        critical_violations += 1
                        validation_result["violations"].append(violation_data["message"])
                    elif rule_config["severity"] == "high":
                        validation_result["warnings"].append(violation_data["message"])
                    else:
                        validation_result["suggestions"].append(violation_data["message"])
                
                validation_result["constraint_details"][rule_name] = {
                    "violated": violation_data["violated"],
                    "message": violation_data["message"],
                    "severity": rule_config["severity"],
                    "details": violation_data.get("details", {})
                }
                
            except Exception as e:
                validation_result["warnings"].append(f"Error checking {rule_name}: {str(e)}")
        
        # Determine overall validity
        validation_result["is_valid"] = critical_violations == 0
        validation_result["severity_score"] = critical_violations / len(self.constraint_rules)
        
        # Use LLM for additional analysis if there are violations
        if total_violations > 0:
            llm_analysis = await self._get_llm_constraint_analysis(allocation, staff, shift, validation_result)
            validation_result["llm_analysis"] = llm_analysis
            
            # Add LLM suggestions
            if "suggestions" in llm_analysis:
                validation_result["suggestions"].extend(llm_analysis["suggestions"])
        
        return validation_result
    
    async def validate_multiple_allocations(self, allocations: List[AllocationRecord]) -> Dict[str, Any]:
        """Validate multiple allocations and check for conflicts"""
        
        results = {
            "individual_validations": {},
            "global_conflicts": [],
            "overall_valid": True,
            "summary": {
                "total_allocations": len(allocations),
                "valid_allocations": 0,
                "critical_violations": 0,
                "warnings": 0
            }
        }
        
        # Validate each allocation individually
        for allocation in allocations:
            validation = await self.validate_allocation(allocation)
            results["individual_validations"][allocation.id] = validation
            
            if validation["is_valid"]:
                results["summary"]["valid_allocations"] += 1
            else:
                results["overall_valid"] = False
                results["summary"]["critical_violations"] += len(validation["violations"])
            
            results["summary"]["warnings"] += len(validation["warnings"])
        
        # Check for global conflicts (e.g., double-booking)
        global_conflicts = self._check_global_conflicts(allocations)
        results["global_conflicts"] = global_conflicts
        
        if global_conflicts:
            results["overall_valid"] = False
        
        return results
    
    def _check_weekly_hours(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check if allocation violates weekly hour limits"""
        
        # Get all allocations for this staff member in the same week
        shift_date = datetime.strptime(shift.date, "%Y-%m-%d")
        week_start = shift_date - timedelta(days=shift_date.weekday())
        week_end = week_start + timedelta(days=7)
        
        staff_allocations = db.get_allocations_by_staff(staff.id)
        weekly_hours = 0
        
        for alloc in staff_allocations:
            alloc_shift = db.get_shift_by_id(alloc.shift_id)
            if alloc_shift:
                alloc_date = datetime.strptime(alloc_shift.date, "%Y-%m-%d")
                if week_start <= alloc_date < week_end:
                    # Calculate shift hours (simplified as 8 hours)
                    weekly_hours += 8
        
        # Add current shift hours
        weekly_hours += 8  # Simplified
        
        violated = weekly_hours > staff.max_hours_per_week
        
        return {
            "violated": violated,
            "message": f"Weekly hours ({weekly_hours}) exceed maximum ({staff.max_hours_per_week})" if violated else "Weekly hours within limit",
            "details": {
                "current_weekly_hours": weekly_hours,
                "max_allowed": staff.max_hours_per_week,
                "additional_hours": 8
            }
        }
    
    def _check_skill_level(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check if staff meets skill level requirements"""
        
        violated = staff.skill_level < shift.minimum_skill_level
        
        return {
            "violated": violated,
            "message": f"Staff skill level ({staff.skill_level}) below required ({shift.minimum_skill_level})" if violated else "Skill level requirement met",
            "details": {
                "staff_skill_level": staff.skill_level,
                "required_skill_level": shift.minimum_skill_level
            }
        }
    
    def _check_department_match(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check if staff department matches shift department"""
        
        violated = staff.department.value != shift.department
        
        return {
            "violated": violated,
            "message": f"Department mismatch: staff ({staff.department.value}) vs shift ({shift.department})" if violated else "Department match",
            "details": {
                "staff_department": staff.department.value,
                "shift_department": shift.department
            }
        }
    
    def _check_availability(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check if staff is available on shift date"""
        
        violated = shift.date in staff.unavailable_dates
        
        return {
            "violated": violated,
            "message": f"Staff unavailable on {shift.date}" if violated else "Staff available",
            "details": {
                "shift_date": shift.date,
                "unavailable_dates": staff.unavailable_dates
            }
        }
    
    def _check_rest_period(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check minimum rest period between shifts"""
        
        # Get staff's other allocations
        staff_allocations = db.get_allocations_by_staff(staff.id)
        current_date = datetime.strptime(shift.date, "%Y-%m-%d")
        
        for alloc in staff_allocations:
            if alloc.id == allocation.id:
                continue
                
            other_shift = db.get_shift_by_id(alloc.shift_id)
            if other_shift:
                other_date = datetime.strptime(other_shift.date, "%Y-%m-%d")
                time_diff = abs((current_date - other_date).days)
                
                # Require at least 12 hours rest (simplified to same day check)
                if time_diff == 0:  # Same day - potential issue
                    return {
                        "violated": True,
                        "message": f"Insufficient rest period - multiple shifts on {shift.date}",
                        "details": {
                            "conflicting_shift": other_shift.id,
                            "same_day_shifts": True
                        }
                    }
        
        return {
            "violated": False,
            "message": "Adequate rest period",
            "details": {}
        }
    
    def _check_certifications(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check if staff has required certifications"""
        
        # Simplified certification check based on special requirements
        violated = False
        missing_certs = []
        
        for requirement in shift.special_requirements:
            # This is a simplified check - in reality, you'd have a proper certification system
            if "certified" in requirement.lower():
                cert_type = requirement.replace("_certified", "")
                if cert_type not in staff.certification_level.lower():
                    violated = True
                    missing_certs.append(requirement)
        
        return {
            "violated": violated,
            "message": f"Missing certifications: {', '.join(missing_certs)}" if violated else "Certification requirements met",
            "details": {
                "required_certifications": shift.special_requirements,
                "staff_certifications": staff.certification_level,
                "missing": missing_certs
            }
        }
    
    def _check_shift_capacity(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check if shift has capacity for additional staff"""
        
        # Count current allocations for this shift
        shift_allocations = db.get_allocations_by_shift(shift.id)
        current_capacity = len(shift_allocations)
        
        violated = current_capacity >= shift.max_capacity
        
        return {
            "violated": violated,
            "message": f"Shift at capacity ({current_capacity}/{shift.max_capacity})" if violated else "Capacity available",
            "details": {
                "current_allocations": current_capacity,
                "max_capacity": shift.max_capacity
            }
        }
    
    def _check_role_requirements(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Check if required roles are being filled"""
        
        # Count allocated staff by role for this shift
        shift_allocations = db.get_allocations_by_shift(shift.id)
        role_counts = {}
        
        for alloc in shift_allocations:
            alloc_staff = db.get_staff_by_id(alloc.staff_id)
            if alloc_staff:
                role = alloc_staff.role.value
                role_counts[role] = role_counts.get(role, 0) + 1
        
        # Add current allocation
        role_counts[staff.role.value] = role_counts.get(staff.role.value, 0) + 1
        
        # Check if requirements are met
        unmet_requirements = []
        for role, required_count in shift.required_staff.items():
            current_count = role_counts.get(role, 0)
            if current_count < required_count:
                unmet_requirements.append(f"{role}: {current_count}/{required_count}")
        
        violated = len(unmet_requirements) > 0
        
        return {
            "violated": violated,
            "message": f"Unmet role requirements: {', '.join(unmet_requirements)}" if violated else "Role requirements satisfied",
            "details": {
                "required_roles": shift.required_staff,
                "current_roles": role_counts,
                "unmet": unmet_requirements
            }
        }
    
    def _check_global_conflicts(self, allocations: List[AllocationRecord]) -> List[Dict[str, Any]]:
        """Check for conflicts across multiple allocations"""
        
        conflicts = []
        
        # Check for double-booking (same staff, overlapping shifts)
        staff_shifts = {}
        for allocation in allocations:
            staff_id = allocation.staff_id
            shift = db.get_shift_by_id(allocation.shift_id)
            
            if staff_id not in staff_shifts:
                staff_shifts[staff_id] = []
            
            if shift:
                staff_shifts[staff_id].append({
                    "allocation_id": allocation.id,
                    "shift_id": shift.id,
                    "date": shift.date,
                    "start_time": shift.start_time,
                    "end_time": shift.end_time
                })
        
        # Check for time conflicts
        for staff_id, shifts in staff_shifts.items():
            for i, shift1 in enumerate(shifts):
                for j, shift2 in enumerate(shifts[i+1:], i+1):
                    if shift1["date"] == shift2["date"]:
                        # Same date - check time overlap
                        conflicts.append({
                            "type": "double_booking",
                            "staff_id": staff_id,
                            "conflicting_allocations": [shift1["allocation_id"], shift2["allocation_id"]],
                            "message": f"Staff {staff_id} double-booked on {shift1['date']}"
                        })
        
        return conflicts
    
    async def _get_llm_constraint_analysis(self, allocation: AllocationRecord, staff: StaffMember, shift: Shift, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get LLM analysis of constraint violations"""
        
        constraint_data = {
            "staff": staff.dict(),
            "shift": shift.dict(),
            "allocation": allocation.dict(),
            "violations": validation_result["violations"],
            "warnings": validation_result["warnings"]
        }
        
        return await llm_service.evaluate_allocation_constraints(constraint_data)

# Global constraint agent instance
constraint_agent = ConstraintAgent()
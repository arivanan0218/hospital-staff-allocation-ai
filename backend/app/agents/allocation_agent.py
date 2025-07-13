# backend/app/agents/allocation_agent.py

from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferMemory
from app.services.llm_service import llm_service
from app.data.database import db
from app.models.allocation import AllocationRecord, AllocationStatus
from app.models.staff import StaffMember
from app.models.shift import Shift
import json
import uuid
from datetime import datetime

class AllocationAgent:
    """AI Agent responsible for staff allocation decisions"""
    
    def __init__(self):
        self.memory = ConversationBufferMemory()
        self.tools = self._create_tools()
        
    def _create_tools(self) -> List[Tool]:
        """Create tools that the agent can use"""
        
        def get_available_staff(date: str, department: str = None) -> str:
            """Get available staff for a specific date and optionally department"""
            try:
                staff_list = db.get_all_staff()
                available_staff = []
                
                for staff in staff_list:
                    # Check if staff is available on the given date
                    if date not in staff.unavailable_dates:
                        if department is None or staff.department.value == department:
                            available_staff.append({
                                "id": staff.id,
                                "name": staff.name,
                                "role": staff.role.value,
                                "department": staff.department.value,
                                "skill_level": staff.skill_level,
                                "hourly_rate": staff.hourly_rate,
                                "experience_years": staff.experience_years
                            })
                
                return json.dumps(available_staff)
            except Exception as e:
                return f"Error getting staff: {str(e)}"
        
        def get_shift_requirements(shift_id: str) -> str:
            """Get detailed requirements for a specific shift"""
            try:
                shift = db.get_shift_by_id(shift_id)
                if not shift:
                    return "Shift not found"
                
                shift_info = {
                    "id": shift.id,
                    "date": shift.date,
                    "shift_type": shift.shift_type.value,
                    "department": shift.department,
                    "start_time": shift.start_time,
                    "end_time": shift.end_time,
                    "required_staff": shift.required_staff,
                    "minimum_skill_level": shift.minimum_skill_level,
                    "priority": shift.priority.value,
                    "special_requirements": shift.special_requirements,
                    "max_capacity": shift.max_capacity
                }
                
                return json.dumps(shift_info)
            except Exception as e:
                return f"Error getting shift: {str(e)}"
        
        def check_staff_workload(staff_id: str, date_range: str) -> str:
            """Check current workload for a staff member"""
            try:
                allocations = db.get_allocations_by_staff(staff_id)
                workload_info = {
                    "staff_id": staff_id,
                    "current_allocations": len(allocations),
                    "confirmed_hours": 0,
                    "pending_hours": 0
                }
                
                for allocation in allocations:
                    shift = db.get_shift_by_id(allocation.shift_id)
                    if shift:
                        # Calculate hours (simplified - assumes 8-hour shifts)
                        hours = 8  # You could calculate actual hours from start/end time
                        if allocation.status == AllocationStatus.CONFIRMED:
                            workload_info["confirmed_hours"] += hours
                        elif allocation.status == AllocationStatus.PENDING:
                            workload_info["pending_hours"] += hours
                
                return json.dumps(workload_info)
            except Exception as e:
                return f"Error checking workload: {str(e)}"
        
        def calculate_allocation_score(staff_id: str, shift_id: str) -> str:
            """Calculate compatibility score between staff and shift"""
            try:
                staff = db.get_staff_by_id(staff_id)
                shift = db.get_shift_by_id(shift_id)
                
                if not staff or not shift:
                    return "0.0"
                
                score = 0.0
                factors = []
                
                # Skill level match (30% weight)
                if staff.skill_level >= shift.minimum_skill_level:
                    skill_score = min(staff.skill_level / 10.0, 1.0)
                    score += skill_score * 0.3
                    factors.append(f"Skill match: {skill_score:.2f}")
                
                # Department match (25% weight)
                if staff.department.value == shift.department:
                    score += 0.25
                    factors.append("Department match: 1.0")
                
                # Shift preference match (20% weight)
                if shift.shift_type.value in staff.preferred_shifts:
                    score += 0.20
                    factors.append("Shift preference match: 1.0")
                
                # Experience factor (15% weight)
                exp_score = min(staff.experience_years / 15.0, 1.0)
                score += exp_score * 0.15
                factors.append(f"Experience factor: {exp_score:.2f}")
                
                # Availability (10% weight)
                if shift.date not in staff.unavailable_dates:
                    score += 0.10
                    factors.append("Available: 1.0")
                
                result = {
                    "score": round(score, 2),
                    "factors": factors,
                    "recommendation": "high" if score > 0.8 else "medium" if score > 0.6 else "low"
                }
                
                return json.dumps(result)
            except Exception as e:
                return f"Error calculating score: {str(e)}"
        
        return [
            Tool(
                name="get_available_staff",
                description="Get list of available staff for a specific date and optionally department",
                func=get_available_staff
            ),
            Tool(
                name="get_shift_requirements",
                description="Get detailed requirements and information for a specific shift",
                func=get_shift_requirements
            ),
            Tool(
                name="check_staff_workload",
                description="Check current workload and allocation status for a staff member",
                func=check_staff_workload
            ),
            Tool(
                name="calculate_allocation_score",
                description="Calculate compatibility score between a staff member and shift",
                func=calculate_allocation_score
            )
        ]
    
    async def allocate_staff_to_shifts(self, shift_ids: List[str], preferences: Dict[str, Any] = None) -> List[AllocationRecord]:
        """Main method to allocate staff to shifts using AI reasoning"""
        
        allocations = []
        
        for shift_id in shift_ids:
            try:
                # Get shift details
                shift = db.get_shift_by_id(shift_id)
                if not shift:
                    continue
                
                # Get available staff for this shift's date and department
                available_staff = json.loads(self.tools[0].func(shift.date, shift.department))
                
                # Use LLM to analyze and recommend allocations
                analysis_data = {
                    "shift": {
                        "id": shift.id,
                        "date": shift.date,
                        "department": shift.department,
                        "required_staff": shift.required_staff,
                        "minimum_skill_level": shift.minimum_skill_level,
                        "priority": shift.priority.value
                    },
                    "available_staff": available_staff
                }
                
                # Get AI recommendation
                ai_analysis = await llm_service.analyze_staff_allocation([analysis_data], [shift.dict()])
                
                # Process AI recommendations and create allocations
                if "recommendations" in ai_analysis:
                    for recommendation in ai_analysis["recommendations"]:
                        if recommendation.get("shift_id") == shift_id:
                            for staff_allocation in recommendation.get("staff_allocations", []):
                                allocation = AllocationRecord(
                                    id=f"allocation_{uuid.uuid4().hex[:8]}",
                                    staff_id=staff_allocation["staff_id"],
                                    shift_id=shift_id,
                                    status=AllocationStatus.PENDING,
                                    confidence_score=staff_allocation.get("confidence", 0.5),
                                    reasoning=staff_allocation.get("reasoning", "AI recommendation"),
                                    constraints_met=["ai_analysis"],
                                    potential_issues=recommendation.get("potential_issues", [])
                                )
                                
                                # Store allocation in database
                                db.create_allocation(allocation)
                                allocations.append(allocation)
                
            except Exception as e:
                print(f"Error allocating staff to shift {shift_id}: {str(e)}")
                continue
        
        return allocations
    
    async def optimize_existing_allocations(self, date_range: str) -> Dict[str, Any]:
        """Optimize existing allocations for better efficiency"""
        
        try:
            # Get all shifts and allocations in the date range
            all_shifts = db.get_all_shifts()
            all_allocations = db.get_all_allocations()
            
            # Filter by date range (simplified - just use first date for now)
            target_date = date_range.split(" to ")[0] if " to " in date_range else date_range
            relevant_shifts = [s for s in all_shifts if s.date == target_date]
            
            current_schedule = {
                "shifts": [s.dict() for s in relevant_shifts],
                "allocations": [a.dict() for a in all_allocations]
            }
            
            # Use LLM to optimize
            optimization_goals = ["minimize_cost", "maximize_efficiency", "improve_satisfaction"]
            optimization_result = await llm_service.optimize_schedule(current_schedule, optimization_goals)
            
            return optimization_result
            
        except Exception as e:
            return {
                "error": f"Failed to optimize allocations: {str(e)}",
                "optimized_schedule": {"changes": []},
                "performance_metrics": {},
                "implementation_plan": []
            }

# Global allocation agent instance
allocation_agent = AllocationAgent()
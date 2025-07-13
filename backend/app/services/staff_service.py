# backend/app/services/staff_service.py

from typing import List, Optional, Dict, Any
from app.models.staff import StaffMember, StaffCreate, StaffUpdate
from app.data.database import db
from app.services.llm_service import llm_service
import json

class StaffService:
    """Service layer for staff-related operations"""
    
    async def get_all_staff(self) -> List[StaffMember]:
        """Get all staff members"""
        return db.get_all_staff()
    
    async def get_staff_by_id(self, staff_id: str) -> Optional[StaffMember]:
        """Get staff member by ID"""
        return db.get_staff_by_id(staff_id)
    
    async def create_staff(self, staff_data: StaffCreate) -> StaffMember:
        """Create new staff member"""
        return db.create_staff(staff_data)
    
    async def update_staff(self, staff_id: str, staff_update: StaffUpdate) -> Optional[StaffMember]:
        """Update staff member"""
        return db.update_staff(staff_id, staff_update)
    
    async def delete_staff(self, staff_id: str) -> bool:
        """Delete staff member"""
        return db.delete_staff(staff_id)
    
    async def get_staff_by_department(self, department: str) -> List[StaffMember]:
        """Get staff by department"""
        return db.get_staff_by_department(department)
    
    async def get_staff_by_role(self, role: str) -> List[StaffMember]:
        """Get staff by role"""
        return db.get_staff_by_role(role)
    
    async def get_available_staff(self, date: str, department: str = None) -> List[StaffMember]:
        """Get staff available on a specific date"""
        if department:
            staff_list = db.get_staff_by_department(department)
        else:
            staff_list = db.get_all_staff()
        
        # Filter by availability
        available_staff = [
            staff for staff in staff_list 
            if date not in staff.unavailable_dates
        ]
        
        return available_staff
    
    async def analyze_staff_skills(self, department: str = None) -> Dict[str, Any]:
        """Analyze staff skill distribution"""
        
        if department:
            staff_list = db.get_staff_by_department(department)
        else:
            staff_list = db.get_all_staff()
        
        if not staff_list:
            return {"error": "No staff found"}
        
        # Calculate skill statistics
        skill_levels = [staff.skill_level for staff in staff_list]
        experience_years = [staff.experience_years for staff in staff_list]
        
        # Role distribution
        role_distribution = {}
        for staff in staff_list:
            role = staff.role.value
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        # Department distribution (if not filtered by department)
        dept_distribution = {}
        if not department:
            for staff in staff_list:
                dept = staff.department.value
                dept_distribution[dept] = dept_distribution.get(dept, 0) + 1
        
        # Skill level distribution
        skill_distribution = {}
        for level in skill_levels:
            skill_distribution[str(level)] = skill_distribution.get(str(level), 0) + 1
        
        analysis = {
            "total_staff": len(staff_list),
            "average_skill_level": sum(skill_levels) / len(skill_levels),
            "average_experience": sum(experience_years) / len(experience_years),
            "skill_level_distribution": skill_distribution,
            "role_distribution": role_distribution,
            "department_distribution": dept_distribution if not department else {department: len(staff_list)},
            "skill_gaps": await self._identify_skill_gaps(staff_list),
            "recommendations": await self._generate_staffing_recommendations(staff_list)
        }
        
        return analysis
    
    async def get_staff_workload_analysis(self, staff_id: str = None, date_range: str = None) -> Dict[str, Any]:
        """Analyze staff workload"""
        
        if staff_id:
            staff_list = [db.get_staff_by_id(staff_id)] if db.get_staff_by_id(staff_id) else []
        else:
            staff_list = db.get_all_staff()
        
        workload_analysis = {
            "staff_workloads": [],
            "summary": {
                "total_staff": len(staff_list),
                "overloaded_staff": 0,
                "underutilized_staff": 0,
                "balanced_staff": 0
            }
        }
        
        for staff in staff_list:
            allocations = db.get_allocations_by_staff(staff.id)
            
            # Calculate hours (simplified)
            total_hours = len(allocations) * 8  # Assume 8-hour shifts
            utilization_rate = min(total_hours / staff.max_hours_per_week, 1.0)
            
            # Categorize workload
            if utilization_rate > 0.9:
                category = "overloaded"
                workload_analysis["summary"]["overloaded_staff"] += 1
            elif utilization_rate < 0.6:
                category = "underutilized"
                workload_analysis["summary"]["underutilized_staff"] += 1
            else:
                category = "balanced"
                workload_analysis["summary"]["balanced_staff"] += 1
            
            staff_workload = {
                "staff_id": staff.id,
                "name": staff.name,
                "role": staff.role.value,
                "department": staff.department.value,
                "max_hours_per_week": staff.max_hours_per_week,
                "allocated_hours": total_hours,
                "utilization_rate": round(utilization_rate, 2),
                "category": category,
                "number_of_shifts": len(allocations)
            }
            
            workload_analysis["staff_workloads"].append(staff_workload)
        
        return workload_analysis
    
    async def suggest_staff_for_shift(self, shift_id: str) -> List[Dict[str, Any]]:
        """Suggest best staff for a specific shift"""
        
        shift = db.get_shift_by_id(shift_id)
        if not shift:
            return []
        
        # Get available staff
        available_staff = await self.get_available_staff(shift.date, shift.department)
        
        suggestions = []
        
        for staff in available_staff:
            # Calculate suitability score
            score = 0.0
            reasons = []
            
            # Skill level check
            if staff.skill_level >= shift.minimum_skill_level:
                skill_score = min(staff.skill_level / 10.0, 1.0)
                score += skill_score * 0.3
                reasons.append(f"Skill level {staff.skill_level}/10")
            else:
                continue  # Skip if doesn't meet minimum requirements
            
            # Role match
            if staff.role.value in shift.required_staff:
                score += 0.25
                reasons.append(f"Role match ({staff.role.value})")
            
            # Department match
            if staff.department.value == shift.department:
                score += 0.2
                reasons.append("Department match")
            
            # Shift preference
            if shift.shift_type.value in staff.preferred_shifts:
                score += 0.15
                reasons.append("Shift preference match")
            
            # Experience
            exp_score = min(staff.experience_years / 15.0, 1.0)
            score += exp_score * 0.1
            reasons.append(f"{staff.experience_years} years experience")
            
            # Cost consideration (inverse - lower cost = slightly higher score)
            cost_score = max(0, (100 - staff.hourly_rate) / 100) * 0.05
            score += cost_score
            
            suggestion = {
                "staff_id": staff.id,
                "name": staff.name,
                "role": staff.role.value,
                "department": staff.department.value,
                "suitability_score": round(score, 2),
                "hourly_rate": staff.hourly_rate,
                "skill_level": staff.skill_level,
                "experience_years": staff.experience_years,
                "reasons": reasons,
                "recommendation": "high" if score > 0.8 else "medium" if score > 0.6 else "low"
            }
            
            suggestions.append(suggestion)
        
        # Sort by suitability score (descending)
        suggestions.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return suggestions[:10]  # Return top 10 suggestions
    
    async def _identify_skill_gaps(self, staff_list: List[StaffMember]) -> List[str]:
        """Identify skill gaps in the staff"""
        
        skill_gaps = []
        
        # Check for departments with low average skill levels
        dept_skills = {}
        for staff in staff_list:
            dept = staff.department.value
            if dept not in dept_skills:
                dept_skills[dept] = []
            dept_skills[dept].append(staff.skill_level)
        
        for dept, skills in dept_skills.items():
            avg_skill = sum(skills) / len(skills)
            if avg_skill < 7:
                skill_gaps.append(f"Low average skill level in {dept} department: {avg_skill:.1f}")
        
        # Check for role shortages
        role_counts = {}
        for staff in staff_list:
            role = staff.role.value
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Identify understaffed roles (this is simplified)
        if role_counts.get("doctor", 0) < 3:
            skill_gaps.append("Shortage of doctors")
        if role_counts.get("nurse", 0) < 6:
            skill_gaps.append("Shortage of nurses")
        
        return skill_gaps
    
    async def _generate_staffing_recommendations(self, staff_list: List[StaffMember]) -> List[str]:
        """Generate AI-powered staffing recommendations"""
        
        # Prepare data for LLM analysis
        staff_data = [
            {
                "role": staff.role.value,
                "department": staff.department.value,
                "skill_level": staff.skill_level,
                "experience_years": staff.experience_years,
                "max_hours_per_week": staff.max_hours_per_week
            }
            for staff in staff_list
        ]
        
        try:
            # Use LLM to analyze staffing patterns and provide recommendations
            prompt = f"""
            Analyze the following hospital staffing data and provide recommendations:
            
            STAFF DATA:
            {json.dumps(staff_data, indent=2)}
            
            Please provide:
            1. Staffing level assessment
            2. Skill gap analysis
            3. Recommendations for hiring priorities
            4. Training suggestions
            5. Schedule optimization opportunities
            
            Respond with a JSON array of recommendation strings.
            """
            
            system_message = """
            You are a hospital staffing consultant AI. Analyze the provided staffing data 
            and provide actionable recommendations for improving hospital operations.
            """
            
            response = await llm_service.generate_response(prompt, system_message)
            
            # Try to parse as JSON, fallback to simple list
            try:
                recommendations = json.loads(response)
                if isinstance(recommendations, list):
                    return recommendations
            except:
                pass
            
            # Fallback: extract recommendations from text
            lines = response.split('\n')
            recommendations = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            return recommendations[:5]  # Return top 5
            
        except Exception as e:
            # Fallback recommendations
            return [
                "Conduct skill assessment for all staff",
                "Consider cross-training to improve flexibility",
                "Review workload distribution across departments",
                "Evaluate hiring needs based on patient volume trends"
            ]

# Global staff service instance
staff_service = StaffService()
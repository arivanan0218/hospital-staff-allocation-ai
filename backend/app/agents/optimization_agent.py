# backend/app/agents/optimization_agent.py

from typing import Dict, List, Any, Optional, Tuple
from app.services.llm_service import llm_service
from app.data.database import db
from app.models.allocation import AllocationRecord, AllocationStatus
from app.models.staff import StaffMember
from app.models.shift import Shift
import json
from datetime import datetime, timedelta

class OptimizationAgent:
    """AI Agent responsible for optimizing staff schedules and resource allocation"""
    
    def __init__(self):
        self.optimization_strategies = {
            "cost": self._optimize_for_cost,
            "quality": self._optimize_for_quality,
            "balance": self._optimize_for_balance,
            "satisfaction": self._optimize_for_satisfaction
        }
    
    async def optimize_schedule(self, 
                              date_range: str, 
                              strategy: str = "balance",
                              constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main optimization method"""
        
        try:
            # Parse date range
            start_date, end_date = self._parse_date_range(date_range)
            
            # Get relevant data
            shifts = self._get_shifts_in_range(start_date, end_date)
            current_allocations = self._get_allocations_in_range(start_date, end_date)
            all_staff = db.get_all_staff()
            
            # Current state analysis
            current_state = self._analyze_current_state(shifts, current_allocations, all_staff)
            
            # Apply optimization strategy
            if strategy in self.optimization_strategies:
                optimization_result = await self.optimization_strategies[strategy](
                    shifts, current_allocations, all_staff, constraints or {}
                )
            else:
                optimization_result = await self._optimize_for_balance(
                    shifts, current_allocations, all_staff, constraints or {}
                )
            
            # Calculate improvement metrics
            improvement_metrics = self._calculate_improvements(current_state, optimization_result)
            
            # Generate implementation plan
            implementation_plan = await self._generate_implementation_plan(optimization_result)
            
            return {
                "success": True,
                "strategy_used": strategy,
                "current_state": current_state,
                "optimization_result": optimization_result,
                "improvement_metrics": improvement_metrics,
                "implementation_plan": implementation_plan,
                "recommendations": optimization_result.get("recommendations", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "recommendations": ["Manual optimization required due to error"]
            }
    
    async def suggest_improvements(self, allocation_ids: List[str]) -> Dict[str, Any]:
        """Suggest improvements for specific allocations"""
        
        suggestions = {
            "improvements": [],
            "cost_savings": 0.0,
            "efficiency_gains": [],
            "risk_reductions": []
        }
        
        for allocation_id in allocation_ids:
            allocation = db.get_allocation_by_id(allocation_id)
            if not allocation:
                continue
            
            staff = db.get_staff_by_id(allocation.staff_id)
            shift = db.get_shift_by_id(allocation.shift_id)
            
            if staff and shift:
                # Analyze current allocation
                analysis = await self._analyze_single_allocation(allocation, staff, shift)
                
                # Generate specific suggestions
                improvement_suggestions = await self._generate_allocation_suggestions(analysis)
                suggestions["improvements"].extend(improvement_suggestions)
        
        return suggestions
    
    async def _optimize_for_cost(self, shifts: List[Shift], allocations: List[AllocationRecord], 
                               staff: List[StaffMember], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize schedule to minimize costs"""
        
        # Calculate current cost
        current_cost = self._calculate_total_cost(allocations, staff)
        
        # Sort staff by hourly rate (ascending for cost optimization)
        staff_by_cost = sorted(staff, key=lambda s: s.hourly_rate)
        
        # Re-allocate using cost-optimal strategy
        optimized_allocations = []
        total_cost_savings = 0.0
        
        for shift in shifts:
            # Find the most cost-effective staff that meets requirements
            suitable_staff = self._find_suitable_staff_for_shift(shift, staff_by_cost)
            
            # Select based on cost and basic requirements
            selected_staff = []
            for role, count in shift.required_staff.items():
                role_staff = [s for s in suitable_staff if s.role.value == role][:count]
                selected_staff.extend(role_staff)
            
            # Create optimized allocations
            for selected in selected_staff:
                cost_saving = self._calculate_cost_saving(shift, selected, allocations)
                total_cost_savings += cost_saving
                
                optimized_allocations.append({
                    "shift_id": shift.id,
                    "staff_id": selected.id,
                    "cost_saving": cost_saving,
                    "reasoning": f"Cost-optimal selection: ${selected.hourly_rate}/hour"
                })
        
        return {
            "optimized_allocations": optimized_allocations,
            "cost_savings": total_cost_savings,
            "strategy": "cost_optimization",
            "recommendations": [
                f"Potential cost savings: ${total_cost_savings:.2f}",
                "Prioritize lower-cost staff while maintaining quality standards",
                "Consider cross-training to increase flexibility"
            ]
        }
    
    async def _optimize_for_quality(self, shifts: List[Shift], allocations: List[AllocationRecord], 
                                  staff: List[StaffMember], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize schedule to maximize quality of care"""
        
        # Sort staff by skill level and experience (descending for quality)
        staff_by_quality = sorted(staff, key=lambda s: (s.skill_level, s.experience_years), reverse=True)
        
        optimized_allocations = []
        quality_improvements = []
        
        for shift in shifts:
            # Prioritize high-priority shifts
            priority_weight = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
            weight = priority_weight.get(shift.priority.value, 0.5)
            
            # Find highest quality staff for this shift
            suitable_staff = self._find_suitable_staff_for_shift(shift, staff_by_quality)
            
            # Select highest quality staff
            selected_staff = []
            for role, count in shift.required_staff.items():
                role_staff = [s for s in suitable_staff if s.role.value == role][:count]
                selected_staff.extend(role_staff)
            
            # Calculate quality improvements
            for selected in selected_staff:
                quality_score = self._calculate_quality_score(shift, selected)
                quality_improvements.append(quality_score)
                
                optimized_allocations.append({
                    "shift_id": shift.id,
                    "staff_id": selected.id,
                    "quality_score": quality_score,
                    "reasoning": f"High-quality match: skill level {selected.skill_level}, {selected.experience_years} years experience"
                })
        
        avg_quality_improvement = sum(quality_improvements) / len(quality_improvements) if quality_improvements else 0
        
        return {
            "optimized_allocations": optimized_allocations,
            "quality_improvement": avg_quality_improvement,
            "strategy": "quality_optimization",
            "recommendations": [
                f"Average quality score improvement: {avg_quality_improvement:.2f}",
                "Assign most experienced staff to critical shifts",
                "Ensure skill level requirements are exceeded where possible"
            ]
        }
    
    async def _optimize_for_balance(self, shifts: List[Shift], allocations: List[AllocationRecord], 
                                  staff: List[StaffMember], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize for balanced approach (cost, quality, satisfaction)"""
        
        # Use LLM for complex multi-objective optimization
        optimization_data = {
            "shifts": [s.dict() for s in shifts],
            "current_allocations": [a.dict() for a in allocations],
            "staff": [s.dict() for s in staff],
            "constraints": constraints
        }
        
        llm_optimization = await llm_service.optimize_schedule(
            optimization_data, 
            ["minimize_cost", "maximize_quality", "improve_satisfaction", "ensure_fairness"]
        )
        
        # Process LLM recommendations
        optimized_allocations = []
        balance_scores = {
            "cost_efficiency": 0.0,
            "quality_score": 0.0,
            "satisfaction_score": 0.0,
            "fairness_score": 0.0
        }
        
        # Extract and process LLM suggestions
        if "optimized_schedule" in llm_optimization:
            changes = llm_optimization["optimized_schedule"].get("changes", [])
            
            for change in changes:
                if change["type"] == "reassignment":
                    # Process reassignment recommendations
                    allocation_suggestion = self._process_reassignment(change)
                    if allocation_suggestion:
                        optimized_allocations.append(allocation_suggestion)
        
        # Calculate balance scores
        balance_scores = self._calculate_balance_scores(optimized_allocations, shifts, staff)
        
        return {
            "optimized_allocations": optimized_allocations,
            "balance_scores": balance_scores,
            "strategy": "balanced_optimization",
            "llm_analysis": llm_optimization,
            "recommendations": llm_optimization.get("implementation_plan", [])
        }
    
    async def _optimize_for_satisfaction(self, shifts: List[Shift], allocations: List[AllocationRecord], 
                                       staff: List[StaffMember], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize for staff satisfaction"""
        
        optimized_allocations = []
        satisfaction_improvements = []
        
        for shift in shifts:
            # Find staff who prefer this shift type
            suitable_staff = self._find_suitable_staff_for_shift(shift, staff)
            
            # Sort by preference match
            staff_with_preferences = []
            for s in suitable_staff:
                preference_score = self._calculate_preference_score(s, shift)
                staff_with_preferences.append((s, preference_score))
            
            # Sort by preference score (descending)
            staff_with_preferences.sort(key=lambda x: x[1], reverse=True)
            
            # Select staff based on preferences
            selected_staff = []
            for role, count in shift.required_staff.items():
                role_staff = [(s, score) for s, score in staff_with_preferences if s.role.value == role][:count]
                selected_staff.extend(role_staff)
            
            # Create allocations with satisfaction scores
            for selected, preference_score in selected_staff:
                satisfaction_improvements.append(preference_score)
                
                optimized_allocations.append({
                    "shift_id": shift.id,
                    "staff_id": selected.id,
                    "satisfaction_score": preference_score,
                    "reasoning": f"High preference match: {preference_score:.2f}"
                })
        
        avg_satisfaction = sum(satisfaction_improvements) / len(satisfaction_improvements) if satisfaction_improvements else 0
        
        return {
            "optimized_allocations": optimized_allocations,
            "satisfaction_improvement": avg_satisfaction,
            "strategy": "satisfaction_optimization",
            "recommendations": [
                f"Average satisfaction improvement: {avg_satisfaction:.2f}",
                "Prioritize staff shift preferences where possible",
                "Consider workload distribution for fairness"
            ]
        }
    
    def _parse_date_range(self, date_range: str) -> Tuple[str, str]:
        """Parse date range string"""
        if " to " in date_range:
            start, end = date_range.split(" to ")
            return start.strip(), end.strip()
        else:
            # Single date
            return date_range.strip(), date_range.strip()
    
    def _get_shifts_in_range(self, start_date: str, end_date: str) -> List[Shift]:
        """Get shifts within date range"""
        all_shifts = db.get_all_shifts()
        return [s for s in all_shifts if start_date <= s.date <= end_date]
    
    def _get_allocations_in_range(self, start_date: str, end_date: str) -> List[AllocationRecord]:
        """Get allocations within date range"""
        all_allocations = db.get_all_allocations()
        relevant_allocations = []
        
        for allocation in all_allocations:
            shift = db.get_shift_by_id(allocation.shift_id)
            if shift and start_date <= shift.date <= end_date:
                relevant_allocations.append(allocation)
        
        return relevant_allocations
    
    def _analyze_current_state(self, shifts: List[Shift], allocations: List[AllocationRecord], 
                             staff: List[StaffMember]) -> Dict[str, Any]:
        """Analyze current schedule state"""
        
        total_cost = self._calculate_total_cost(allocations, staff)
        utilization = self._calculate_staff_utilization(allocations, staff)
        coverage = self._calculate_shift_coverage(shifts, allocations)
        
        return {
            "total_shifts": len(shifts),
            "total_allocations": len(allocations),
            "total_cost": total_cost,
            "staff_utilization": utilization,
            "shift_coverage": coverage,
            "average_quality_score": self._calculate_average_quality(allocations, staff, shifts)
        }
    
    def _calculate_total_cost(self, allocations: List[AllocationRecord], staff: List[StaffMember]) -> float:
        """Calculate total cost of allocations"""
        total_cost = 0.0
        
        for allocation in allocations:
            staff_member = next((s for s in staff if s.id == allocation.staff_id), None)
            if staff_member:
                # Assume 8-hour shifts for simplicity
                total_cost += staff_member.hourly_rate * 8
        
        return total_cost
    
    def _find_suitable_staff_for_shift(self, shift: Shift, staff_list: List[StaffMember]) -> List[StaffMember]:
        """Find staff suitable for a specific shift"""
        suitable = []
        
        for staff_member in staff_list:
            # Check basic suitability
            if (staff_member.skill_level >= shift.minimum_skill_level and
                shift.date not in staff_member.unavailable_dates):
                suitable.append(staff_member)
        
        return suitable
    
    def _calculate_preference_score(self, staff: StaffMember, shift: Shift) -> float:
        """Calculate how well a shift matches staff preferences"""
        score = 0.0
        
        # Shift type preference
        if shift.shift_type.value in staff.preferred_shifts:
            score += 0.4
        
        # Department match
        if staff.department.value == shift.department:
            score += 0.3
        
        # Skill level appropriateness (not too overqualified)
        skill_diff = staff.skill_level - shift.minimum_skill_level
        if 0 <= skill_diff <= 2:
            score += 0.3
        elif skill_diff > 2:
            score += 0.1  # Overqualified
        
        return min(score, 1.0)
    
    def _calculate_quality_score(self, shift: Shift, staff: StaffMember) -> float:
        """Calculate quality score for staff-shift pairing"""
        score = 0.0
        
        # Skill level
        score += min(staff.skill_level / 10.0, 1.0) * 0.4
        
        # Experience
        score += min(staff.experience_years / 15.0, 1.0) * 0.3
        
        # Department match
        if staff.department.value == shift.department:
            score += 0.2
        
        # Priority match (higher skill for higher priority)
        priority_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
        priority_score = priority_weights.get(shift.priority.value, 0.5)
        score += priority_score * 0.1
        
        return min(score, 1.0)
    
    async def _generate_implementation_plan(self, optimization_result: Dict[str, Any]) -> List[str]:
        """Generate step-by-step implementation plan"""
        
        plan = [
            "1. Review optimization recommendations with management",
            "2. Notify affected staff of proposed changes",
            "3. Check for any conflicts or objections",
            "4. Implement changes in scheduling system",
            "5. Monitor performance metrics post-implementation"
        ]
        
        # Add strategy-specific steps
        strategy = optimization_result.get("strategy", "")
        
        if "cost" in strategy:
            plan.insert(1, "1.5. Verify cost savings calculations")
        elif "quality" in strategy:
            plan.insert(1, "1.5. Ensure quality standards are maintained")
        elif "satisfaction" in strategy:
            plan.insert(1, "1.5. Gather staff feedback on proposed changes")
        
        return plan
    
    def _calculate_improvements(self, current_state: Dict[str, Any], 
                              optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate improvement metrics"""
        
        improvements = {
            "cost_change": 0.0,
            "quality_change": 0.0,
            "efficiency_change": 0.0,
            "satisfaction_change": 0.0
        }
        
        # Extract improvements based on optimization strategy
        strategy = optimization_result.get("strategy", "")
        
        if "cost" in strategy:
            improvements["cost_change"] = optimization_result.get("cost_savings", 0.0)
        elif "quality" in strategy:
            improvements["quality_change"] = optimization_result.get("quality_improvement", 0.0)
        elif "satisfaction" in strategy:
            improvements["satisfaction_change"] = optimization_result.get("satisfaction_improvement", 0.0)
        elif "balance" in strategy:
            balance_scores = optimization_result.get("balance_scores", {})
            improvements.update(balance_scores)
        
        return improvements
    
    def _calculate_balance_scores(self, allocations: List[Dict], shifts: List[Shift], 
                                staff: List[StaffMember]) -> Dict[str, float]:
        """Calculate balanced optimization scores"""
        
        return {
            "cost_efficiency": 0.75,  # Placeholder scores
            "quality_score": 0.82,
            "satisfaction_score": 0.68,
            "fairness_score": 0.71
        }
    
    async def _analyze_single_allocation(self, allocation: AllocationRecord, 
                                       staff: StaffMember, shift: Shift) -> Dict[str, Any]:
        """Analyze a single allocation for improvement opportunities"""
        
        return {
            "allocation_id": allocation.id,
            "current_quality_score": self._calculate_quality_score(shift, staff),
            "current_satisfaction_score": self._calculate_preference_score(staff, shift),
            "cost_per_hour": staff.hourly_rate,
            "improvement_potential": "medium"  # Simplified
        }
    
    async def _generate_allocation_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggestions for improving a specific allocation"""
        
        suggestions = []
        
        if analysis["current_quality_score"] < 0.7:
            suggestions.append({
                "type": "quality_improvement",
                "description": "Consider assigning higher-skilled staff",
                "impact": "medium"
            })
        
        if analysis["current_satisfaction_score"] < 0.5:
            suggestions.append({
                "type": "satisfaction_improvement", 
                "description": "Staff preferences not well matched",
                "impact": "low"
            })
        
        return suggestions
    
    def _calculate_staff_utilization(self, allocations: List[AllocationRecord], 
                                   staff: List[StaffMember]) -> float:
        """Calculate overall staff utilization rate"""
        if not staff:
            return 0.0
        
        allocated_staff = set(a.staff_id for a in allocations)
        return len(allocated_staff) / len(staff)
    
    def _calculate_shift_coverage(self, shifts: List[Shift], 
                                allocations: List[AllocationRecord]) -> float:
        """Calculate shift coverage rate"""
        if not shifts:
            return 0.0
        
        covered_shifts = set(a.shift_id for a in allocations)
        return len(covered_shifts) / len(shifts)
    
    def _calculate_average_quality(self, allocations: List[AllocationRecord], 
                                 staff: List[StaffMember], shifts: List[Shift]) -> float:
        """Calculate average quality score across all allocations"""
        if not allocations:
            return 0.0
        
        total_quality = 0.0
        count = 0
        
        for allocation in allocations:
            staff_member = next((s for s in staff if s.id == allocation.staff_id), None)
            shift = next((sh for sh in shifts if sh.id == allocation.shift_id), None)
            
            if staff_member and shift:
                total_quality += self._calculate_quality_score(shift, staff_member)
                count += 1
        
        return total_quality / count if count > 0 else 0.0
    
    def _calculate_cost_saving(self, shift: Shift, staff: StaffMember, 
                             current_allocations: List[AllocationRecord]) -> float:
        """Calculate potential cost saving for a staff assignment"""
        # Simplified calculation - compare with average rate
        current_allocation = next(
            (a for a in current_allocations if a.shift_id == shift.id), None
        )
        
        if current_allocation:
            current_staff = db.get_staff_by_id(current_allocation.staff_id)
            if current_staff:
                return (current_staff.hourly_rate - staff.hourly_rate) * 8  # 8-hour shift
        
        return 0.0
    
    def _process_reassignment(self, change: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a reassignment recommendation from LLM"""
        # Extract details from LLM suggestion and create allocation recommendation
        return {
            "type": "reassignment",
            "details": change.get("details", ""),
            "impact": change.get("impact", "medium"),
            "priority": change.get("priority", "medium")
        }

# Global optimization agent instance
optimization_agent = OptimizationAgent()
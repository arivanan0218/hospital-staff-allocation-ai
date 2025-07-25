# backend/app/data/mock_data.py

from typing import List, Dict
from app.models.staff import StaffMember, StaffRole, Department
from app.models.shift import Shift, ShiftType, Priority, ShiftStatus
from app.models.allocation import AllocationRecord, AllocationStatus
from datetime import datetime

# Mock Staff Data
MOCK_STAFF: List[StaffMember] = [
    StaffMember(
        id="staff_001",
        name="Dr. Sarah Johnson",
        role=StaffRole.DOCTOR,
        department=Department.EMERGENCY,
        skill_level=9,
        current_shift_id="shift_001",
        max_hours_per_week=50,
        preferred_shifts=["morning", "evening"],
        unavailable_dates=["2024-07-20"],
        certification_level="senior",
        experience_years=8,
        hourly_rate=85.0
    ),
    StaffMember(
        id="staff_002",
        name="Nurse Emily Davis",
        role=StaffRole.NURSE,
        department=Department.ICU,
        skill_level=8,
        current_shift_id="shift_002",
        max_hours_per_week=36,
        preferred_shifts=["morning", "afternoon"],
        unavailable_dates=["2024-07-21"],
        certification_level="advanced",
        experience_years=5,
        hourly_rate=35.0
    ),
    StaffMember(
        id="staff_003",
        name="Dr. Michael Chen",
        role=StaffRole.DOCTOR,
        department=Department.SURGERY,
        skill_level=10,
        max_hours_per_week=45,
        preferred_shifts=["morning"],
        unavailable_dates=["2024-07-18", "2024-07-19"],
        certification_level="expert",
        experience_years=12,
        hourly_rate=120.0
    ),
    StaffMember(
        id="staff_004",
        name="Technician Jake Wilson",
        role=StaffRole.TECHNICIAN,
        department=Department.EMERGENCY,
        skill_level=7,
        max_hours_per_week=40,
        preferred_shifts=["afternoon", "evening"],
        unavailable_dates=[],
        certification_level="intermediate",
        experience_years=4,
        hourly_rate=28.0
    ),
    StaffMember(
        id="staff_005",
        name="Nurse Lisa Martinez",
        role=StaffRole.NURSE,
        department=Department.PEDIATRICS,
        skill_level=8,
        max_hours_per_week=36,
        preferred_shifts=["morning", "afternoon"],
        unavailable_dates=["2024-07-21"],
        certification_level="advanced",
        experience_years=5,
        hourly_rate=32.0
    ),
    StaffMember(
        id="staff_006",
        name="Dr. Amanda Rodriguez",
        role=StaffRole.DOCTOR,
        department=Department.CARDIOLOGY,
        skill_level=9,
        max_hours_per_week=48,
        preferred_shifts=["morning"],
        unavailable_dates=[],
        certification_level="senior",
        experience_years=10,
        hourly_rate=95.0
    ),
    StaffMember(
        id="staff_007",
        name="Technician Sarah Johnson",
        role=StaffRole.TECHNICIAN,
        department=Department.EMERGENCY,
        skill_level=7,
        max_hours_per_week=40,
        preferred_shifts=["afternoon", "evening"],
        unavailable_dates=[],
        certification_level="intermediate",
        experience_years=4,
        hourly_rate=28.0
    ),
    StaffMember(
        id="staff_008",
        name="Nurse Emily Davis",
        role=StaffRole.NURSE,
        department=Department.ICU,
        skill_level=8,
        max_hours_per_week=36,
        preferred_shifts=["morning", "afternoon", "evening", "night"],
        unavailable_dates=[],
        certification_level="advanced",
        experience_years=5,
        hourly_rate=15.0
    ),
    StaffMember(
        id="staff_009",
        name="Dr. Michael Chen",
        role=StaffRole.DOCTOR,
        department=Department.SURGERY,
        skill_level=10,
        max_hours_per_week=45,
        preferred_shifts=["morning"],
        unavailable_dates=[],
        certification_level="expert",
        experience_years=12,
        hourly_rate=120.0
    ),
    StaffMember(
        id="staff_010",
        name="Technician Sarah Johnson",
        role=StaffRole.TECHNICIAN,
        department=Department.EMERGENCY,
        skill_level=7,
        max_hours_per_week=40,
        preferred_shifts=["morning","afternoon", "evening"],
        unavailable_dates=[],
        certification_level="intermediate",
        experience_years=4,
        hourly_rate=28.0
    ),
]

# Mock Shift Data
MOCK_SHIFTS: List[Shift] = [
    Shift(
        id="shift_001",
        date=datetime.now().strftime("%Y-%m-%d"),  # Today's date
        shift_type=ShiftType.MORNING,
        status=ShiftStatus.IN_PROGRESS,
        department="emergency",
        start_time="08:00",
        end_time="16:00",
        required_staff={"doctor": 1, "nurse": 0, "technician": 1},
        minimum_skill_level=5,  # Lowered from 6
        priority=Priority.HIGH,
        special_requirements=["trauma_certified"],
        max_capacity=8,
        actual_start_time=None,
        actual_end_time=None,
        is_extended=False,
        completion_notes=None
    ),
    Shift(
        id="shift_002",
        date=datetime.now().strftime("%Y-%m-%d"),  # Today's date
        shift_type=ShiftType.NIGHT,
        status=ShiftStatus.IN_PROGRESS,
        department="icu",
        start_time="20:00",
        end_time="08:00",
        required_staff={"doctor": 1, "nurse": 1},  # Reduced from 4 nurses
        minimum_skill_level=6,
        priority=Priority.CRITICAL,
        special_requirements=["icu_certified"],
        max_capacity=6,
        actual_start_time=None,
        actual_end_time=None,
        is_extended=False,
        completion_notes=None
    ),
    Shift(
        id="shift_003",
        date="2024-07-16",
        shift_type=ShiftType.MORNING,
        department="surgery",
        start_time="07:00",
        end_time="15:00",
        required_staff={"doctor": 1, "nurse": 1, "technician": 1},  # Reduced requirements
        minimum_skill_level=7,
        priority=Priority.HIGH,
        special_requirements=["surgery_certified"],
        max_capacity=7,
        status=ShiftStatus.SCHEDULED,
        actual_start_time=None,
        actual_end_time=None,
        is_extended=False,
        completion_notes=None
    ),
    Shift(
        id="shift_004",
        date="2024-07-16",
        shift_type=ShiftType.AFTERNOON,
        department="pediatrics",
        start_time="14:00",
        end_time="22:00",
        required_staff={"doctor": 1, "nurse": 1},
        minimum_skill_level=5,  # Lowered from 6
        priority=Priority.MEDIUM,
        special_requirements=["pediatric_certified"],
        max_capacity=4,
        status=ShiftStatus.SCHEDULED,
        actual_start_time=None,
        actual_end_time=None,
        is_extended=False,
        completion_notes=None
    ),
    Shift(
        id="shift_005",
        date="2024-07-17",
        shift_type=ShiftType.MORNING,
        department="cardiology",
        start_time="08:00",
        end_time="16:00",
        required_staff={"doctor": 1, "nurse": 1, "technician": 1},
        minimum_skill_level=6,
        priority=Priority.MEDIUM,
        special_requirements=["cardiology_certified"],
        max_capacity=5,
        status=ShiftStatus.SCHEDULED,
        actual_start_time=None,
        actual_end_time=None,
        is_extended=False,
        completion_notes=None
    ),
    # Add more shifts for today's date to make testing easier
    Shift(
        id="shift_006",
        date="2024-07-18",
        shift_type=ShiftType.MORNING,
        department="general",
        start_time="08:00",
        end_time="16:00",
        required_staff={"doctor": 1, "nurse": 1},
        minimum_skill_level=5,
        priority=Priority.MEDIUM,
        special_requirements=[],
        max_capacity=4,
        status=ShiftStatus.SCHEDULED,
        actual_start_time=None,
        actual_end_time=None,
        is_extended=False,
        completion_notes=None
    )
]

# Mock Allocation Data
MOCK_ALLOCATIONS: List[AllocationRecord] = [
    AllocationRecord(
        id="allocation_001",
        staff_id="staff_001",
        shift_id="shift_001",
        status=AllocationStatus.CONFIRMED,
        assigned_at="2024-07-13T10:30:00",
        confidence_score=0.92,
        reasoning="Dr. Johnson is highly skilled in emergency care and available during this time slot",
        constraints_met=["skill_level", "availability", "department_match"],
        potential_issues=[],
        checked_in_at=None,
        checked_out_at=None,
        is_present=False,
        overtime_hours=0.0
    ),
    AllocationRecord(
        id="allocation_002",
        staff_id="staff_002",
        shift_id="shift_002",
        status=AllocationStatus.CONFIRMED,
        assigned_at="2024-07-13T10:35:00",
        confidence_score=0.88,
        reasoning="Nurse Davis specializes in ICU care and prefers night shifts",
        constraints_met=["skill_level", "availability", "department_match", "shift_preference"],
        potential_issues=[],
        checked_in_at=None,
        checked_out_at=None,
        is_present=False,
        overtime_hours=0.0
    )
]
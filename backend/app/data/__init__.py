# # backend/app/data/__init__.py
# """
# Data layer including database operations and mock data
# """

# from .database import db
# from .mock_data import MOCK_STAFF, MOCK_SHIFTS, MOCK_ALLOCATIONS

# __all__ = ["db", "MOCK_STAFF", "MOCK_SHIFTS", "MOCK_ALLOCATIONS"]

# backend/app/data/__init__.py
"""
Data layer including database operations and mock data
"""

from .database import db
from .mock_data import MOCK_STAFF, MOCK_SHIFTS, MOCK_ALLOCATIONS

__all__ = ["db", "MOCK_STAFF", "MOCK_SHIFTS", "MOCK_ALLOCATIONS"]
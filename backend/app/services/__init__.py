# # backend/app/services/__init__.py
# """
# Service layer for business logic and external integrations
# """

# from .staff_service import staff_service
# from .allocation_service import allocation_service
# from .llm_service import llm_service

# __all__ = ["staff_service", "allocation_service", "llm_service"]

# backend/app/services/__init__.py
"""
Service layer for business logic and external integrations
"""

from .staff_service import staff_service
from .allocation_service import allocation_service
from .llm_service import llm_service

__all__ = ["staff_service", "allocation_service", "llm_service"]
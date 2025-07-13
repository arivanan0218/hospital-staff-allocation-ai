# backend/app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import uvicorn

# Load environment variables
load_dotenv()

# Import routers
from app.routers import staff, shifts, allocation

# Import services for health checks
from app.data.database import db
from app.services.llm_service import llm_service

# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Hospital Staff Allocation AI"),
    description="AI-powered hospital staff allocation system using LangChain, LangGraph, and GROQ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(staff.router)
app.include_router(shifts.router)
app.include_router(allocation.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Hospital Staff Allocation AI API",
        "version": "1.0.0",
        "description": "AI-powered staff allocation system for hospitals",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "Staff management",
            "Shift scheduling",
            "AI-powered allocation",
            "Constraint validation",
            "Schedule optimization",
            "Analytics and reporting"
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connectivity
        staff_count = len(db.get_all_staff())
        shift_count = len(db.get_all_shifts())
        allocation_count = len(db.get_all_allocations())
        
        # Check LLM service (simple test)
        llm_status = "healthy"
        try:
            # Simple test prompt
            test_response = await llm_service.generate_response("Hello", "You are a helpful assistant.")
            if not test_response or "error" in test_response.lower():
                llm_status = "degraded"
        except Exception:
            llm_status = "unhealthy"
        
        return {
            "status": "healthy",
            "timestamp": db.__class__.__name__,  # Current time would be better
            "services": {
                "database": {
                    "status": "healthy",
                    "stats": {
                        "staff_count": staff_count,
                        "shift_count": shift_count,
                        "allocation_count": allocation_count
                    }
                },
                "llm_service": {
                    "status": llm_status,
                    "provider": "GROQ"
                }
            },
            "environment": {
                "debug": os.getenv("DEBUG", "False"),
                "host": os.getenv("HOST", "localhost"),
                "port": os.getenv("PORT", "8000")
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# API information endpoint
@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "api_version": "1.0.0",
        "ai_features": {
            "allocation_agent": {
                "description": "Intelligent staff allocation using LangChain agents",
                "endpoints": ["/api/allocations/auto-allocate", "/api/allocations/optimize"]
            },
            "constraint_validation": {
                "description": "AI-powered constraint checking and validation",
                "endpoints": ["/api/allocations/{id}/validate", "/api/allocations/conflicts/{date_range}"]
            },
            "llm_integration": {
                "description": "GROQ LLM for natural language processing and recommendations",
                "provider": "GROQ",
                "model": "llama3-8b-8192"
            }
        },
        "endpoints": {
            "staff_management": {
                "base_url": "/api/staff",
                "operations": ["create", "read", "update", "delete", "analytics"]
            },
            "shift_management": {
                "base_url": "/api/shifts",
                "operations": ["create", "read", "update", "delete", "search", "analytics"]
            },
            "allocation_management": {
                "base_url": "/api/allocations",
                "operations": ["create", "auto-allocate", "optimize", "validate", "analytics"]
            }
        },
        "features": [
            "Real-time staff allocation",
            "Constraint-based validation",
            "Multi-objective optimization",
            "Analytics and reporting",
            "Alternative suggestions",
            "Conflict detection"
        ]
    }

# Statistics endpoint
@app.get("/api/stats")
async def get_system_statistics():
    """Get system-wide statistics"""
    try:
        # Get basic counts
        staff_count = len(db.get_all_staff())
        shift_count = len(db.get_all_shifts())
        allocation_count = len(db.get_all_allocations())
        
        # Calculate utilization
        staff_utilization = db.get_staff_utilization()
        shift_coverage = db.get_shift_coverage()
        
        # Department statistics
        all_staff = db.get_all_staff()
        dept_stats = {}
        for staff in all_staff:
            dept = staff.department.value
            if dept not in dept_stats:
                dept_stats[dept] = {"count": 0, "avg_skill": 0, "total_skill": 0}
            dept_stats[dept]["count"] += 1
            dept_stats[dept]["total_skill"] += staff.skill_level
        
        # Calculate averages
        for dept_data in dept_stats.values():
            if dept_data["count"] > 0:
                dept_data["avg_skill"] = round(dept_data["total_skill"] / dept_data["count"], 2)
        
        # Role statistics
        role_stats = {}
        for staff in all_staff:
            role = staff.role.value
            if role not in role_stats:
                role_stats[role] = {"count": 0, "avg_experience": 0, "total_experience": 0}
            role_stats[role]["count"] += 1
            role_stats[role]["total_experience"] += staff.experience_years
        
        # Calculate averages
        for role_data in role_stats.values():
            if role_data["count"] > 0:
                role_data["avg_experience"] = round(role_data["total_experience"] / role_data["count"], 2)
        
        return {
            "overview": {
                "total_staff": staff_count,
                "total_shifts": shift_count,
                "total_allocations": allocation_count,
                "staff_utilization_rate": staff_utilization["utilization_rate"],
                "shift_coverage_rate": shift_coverage["coverage_rate"]
            },
            "staff_by_department": dept_stats,
            "staff_by_role": role_stats,
            "utilization": staff_utilization,
            "coverage": shift_coverage,
            "system_health": {
                "database_status": "operational",
                "ai_agents_status": "operational",
                "llm_service_status": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

# Demo data reset endpoint (for development)
@app.post("/api/demo/reset")
async def reset_demo_data():
    """Reset to demo data (development only)"""
    try:
        from app.data.mock_data import MOCK_STAFF, MOCK_SHIFTS, MOCK_ALLOCATIONS
        
        # Reset database with mock data
        db.staff = MOCK_STAFF.copy()
        db.shifts = MOCK_SHIFTS.copy()
        db.allocations = MOCK_ALLOCATIONS.copy()
        
        return {
            "message": "Demo data reset successfully",
            "data": {
                "staff_count": len(db.staff),
                "shift_count": len(db.shifts),
                "allocation_count": len(db.allocations)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting demo data: {str(e)}")

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "False").lower() == "true" else "An unexpected error occurred"
        }
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "localhost"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
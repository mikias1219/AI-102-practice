"""
FastAPI Backend for Job Matching System
Integrates with Azure Cosmos DB and Azure Functions
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
import os
import uuid
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============ LOGGING SETUP ============

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ FASTAPI APP SETUP ============

app = FastAPI(
    title="Job Matching API",
    description="Backend API for job matching system with Azure Cosmos DB",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ PYDANTIC MODELS ============

class JobModel(BaseModel):
    """Job posting model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    title: str
    description: str
    skills: List[str]
    experience_required: int
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: str = "Full-time"  # Full-time, Part-time, Contract
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UserModel(BaseModel):
    """User model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    email: str
    skills: List[str]
    experience: int
    location: str
    bio: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ApplicationModel(BaseModel):
    """Job application model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    job_id: str
    status: str = "submitted"
    match_score: Optional[float] = None
    cover_letter: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    interview_date: Optional[str] = None

class RecommendationModel(BaseModel):
    """Job recommendation model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    job_id: str
    score: float
    reasons: List[str]
    generated_at: Optional[str] = None

class AnalyticsModel(BaseModel):
    """Analytics model"""
    total_jobs: int
    total_applications: int
    average_match_score: float
    applications_by_status: dict
    top_skills: List[str]

# ============ COSMOS DB SETUP ============

class CosmosDBClient:
    """Azure Cosmos DB client wrapper"""
    
    def __init__(self):
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.key = os.getenv("COSMOS_KEY")
        self.db_name = os.getenv("COSMOS_DB_NAME", "job-db")
        
        if not self.endpoint or not self.key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY are required")
        
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.db_name)
        
        # Initialize containers
        self.jobs_container = self.database.get_container_client("jobs")
        self.users_container = self.database.get_container_client("users")
        self.applications_container = self.database.get_container_client("applications")
        self.recommendations_container = self.database.get_container_client("recommendations")
        
        logger.info(f"✅ Connected to Cosmos DB: {self.endpoint}")

# Initialize Cosmos DB
try:
    cosmos_db = CosmosDBClient()
except Exception as e:
    logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
    cosmos_db = None

# ============ HEALTH CHECK ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cosmos_db": "connected" if cosmos_db else "disconnected"
    }

# ============ JOBS ENDPOINTS ============

@app.get("/api/jobs", response_model=dict)
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    location: Optional[str] = None,
    min_experience: Optional[int] = None
):
    """
    Get jobs with optional filters
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **location**: Filter by location
    - **min_experience**: Filter by minimum experience required
    """
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        query = "SELECT * FROM c WHERE c.status = 'active'"
        parameters = []
        
        if location:
            query += " AND c.location = @location"
            parameters.append({"name": "@location", "value": location})
        
        if min_experience is not None:
            query += " AND c.experience_required <= @min_exp"
            parameters.append({"name": "@min_exp", "value": min_experience})
        
        query += " ORDER BY c.created_at DESC OFFSET @skip LIMIT @limit"
        parameters.extend([
            {"name": "@skip", "value": skip},
            {"name": "@limit", "value": limit}
        ])
        
        items = list(cosmos_db.jobs_container.query_items(
            query=query,
            parameters=parameters
        ))
        
        return {
            "status": "success",
            "data": items,
            "count": len(items),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}", response_model=dict)
async def get_job(job_id: str):
    """Get specific job by ID"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        query = "SELECT * FROM c WHERE c.id = @id"
        items = list(cosmos_db.jobs_container.query_items(
            query=query,
            parameters=[{"name": "@id", "value": job_id}]
        ))
        
        if not items:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"status": "success", "data": items[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs", response_model=dict)
async def create_job(job: JobModel):
    """Create new job posting"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        job.created_at = datetime.utcnow().isoformat()
        job.updated_at = datetime.utcnow().isoformat()
        
        result = cosmos_db.jobs_container.create_item(body=job.dict())
        logger.info(f"✅ Job created: {job.id}")
        
        return {
            "status": "success",
            "data": result,
            "message": "Job created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/jobs/{job_id}", response_model=dict)
async def update_job(job_id: str, job_update: dict):
    """Update existing job"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        query = "SELECT * FROM c WHERE c.id = @id"
        items = list(cosmos_db.jobs_container.query_items(
            query=query,
            parameters=[{"name": "@id", "value": job_id}]
        ))
        
        if not items:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = items[0]
        job.update(job_update)
        job["updated_at"] = datetime.utcnow().isoformat()
        
        result = cosmos_db.jobs_container.replace_item(
            item=job_id,
            body=job
        )
        logger.info(f"✅ Job updated: {job_id}")
        
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ APPLICATIONS ENDPOINTS ============

@app.post("/api/applications", response_model=dict)
async def submit_application(application: ApplicationModel):
    """Submit job application"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        application.created_at = datetime.utcnow().isoformat()
        application.updated_at = datetime.utcnow().isoformat()
        
        result = cosmos_db.applications_container.create_item(
            body=application.dict()
        )
        logger.info(f"✅ Application submitted: {application.id}")
        
        return {
            "status": "success",
            "data": result,
            "message": "Application submitted successfully"
        }
    except Exception as e:
        logger.error(f"Error submitting application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/applications/{user_id}", response_model=dict)
async def get_user_applications(
    user_id: str,
    status: Optional[str] = None
):
    """Get user's applications"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        parameters = [{"name": "@user_id", "value": user_id}]
        
        if status:
            query += " AND c.status = @status"
            parameters.append({"name": "@status", "value": status})
        
        query += " ORDER BY c.created_at DESC"
        
        items = list(cosmos_db.applications_container.query_items(
            query=query,
            parameters=parameters
        ))
        
        return {
            "status": "success",
            "data": items,
            "count": len(items)
        }
    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/applications/{app_id}", response_model=dict)
async def update_application(app_id: str, update_data: dict):
    """Update application status"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        query = "SELECT * FROM c WHERE c.id = @id"
        items = list(cosmos_db.applications_container.query_items(
            query=query,
            parameters=[{"name": "@id", "value": app_id}]
        ))
        
        if not items:
            raise HTTPException(status_code=404, detail="Application not found")
        
        app = items[0]
        app.update(update_data)
        app["updated_at"] = datetime.utcnow().isoformat()
        
        result = cosmos_db.applications_container.replace_item(
            item=app_id,
            body=app
        )
        logger.info(f"✅ Application updated: {app_id}")
        
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ RECOMMENDATIONS ENDPOINTS ============

@app.get("/api/recommendations/{user_id}", response_model=dict)
async def get_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=100)
):
    """Get job recommendations for user"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        query = f"""
            SELECT * FROM c 
            WHERE c.user_id = @user_id 
            ORDER BY c.score DESC 
            OFFSET 0 LIMIT {limit}
        """
        
        items = list(cosmos_db.recommendations_container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}]
        ))
        
        return {
            "status": "success",
            "data": items,
            "count": len(items)
        }
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations", response_model=dict)
async def create_recommendation(recommendation: RecommendationModel):
    """Create job recommendation"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        recommendation.generated_at = datetime.utcnow().isoformat()
        
        result = cosmos_db.recommendations_container.create_item(
            body=recommendation.dict()
        )
        logger.info(f"✅ Recommendation created: {recommendation.id}")
        
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error creating recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ ANALYTICS ENDPOINTS ============

@app.get("/api/analytics", response_model=dict)
async def get_analytics():
    """Get system analytics"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        # Total jobs
        jobs_query = "SELECT VALUE COUNT(1) FROM c WHERE c.status = 'active'"
        job_count = list(cosmos_db.jobs_container.query_items(jobs_query))
        total_jobs = job_count[0] if job_count else 0
        
        # Total applications
        apps_query = "SELECT VALUE COUNT(1) FROM c"
        app_count = list(cosmos_db.applications_container.query_items(apps_query))
        total_applications = app_count[0] if app_count else 0
        
        # Average match score
        score_query = "SELECT VALUE AVG(c.match_score) FROM c WHERE c.match_score != null"
        avg_score_result = list(cosmos_db.applications_container.query_items(score_query))
        average_match_score = round(avg_score_result[0], 2) if avg_score_result and avg_score_result[0] else 0
        
        # Applications by status
        status_query = """
            SELECT c.status, COUNT(1) as count 
            FROM c 
            GROUP BY c.status
        """
        status_results = list(cosmos_db.applications_container.query_items(status_query))
        applications_by_status = {item["status"]: item["count"] for item in status_results}
        
        return {
            "status": "success",
            "data": {
                "total_jobs": total_jobs,
                "total_applications": total_applications,
                "average_match_score": average_match_score,
                "applications_by_status": applications_by_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ USERS ENDPOINTS ============

@app.post("/api/users", response_model=dict)
async def create_user(user: UserModel):
    """Create user profile"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        user.created_at = datetime.utcnow().isoformat()
        user.updated_at = datetime.utcnow().isoformat()
        
        result = cosmos_db.users_container.create_item(body=user.dict())
        logger.info(f"✅ User created: {user.id}")
        
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}", response_model=dict)
async def get_user(user_id: str):
    """Get user profile"""
    try:
        if not cosmos_db:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        items = list(cosmos_db.users_container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}]
        ))
        
        if not items:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"status": "success", "data": items[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ ROOT ENDPOINT ============

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 Job Matching API - Powered by FastAPI & Cosmos DB",
        "version": "2.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

# ============ ERROR HANDLERS ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "detail": exc.detail,
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


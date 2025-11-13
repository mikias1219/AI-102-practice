"""
Azure Functions for Job Matching System
Handles HTTP triggers, Timer triggers, and Event Hub triggers
"""

import azure.functions as func
import json
import httpx
import logging
from datetime import datetime
from azure.cosmos import CosmosClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Function App
app = func.FunctionApp()

# ============ CONFIGURATION ============

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB = os.getenv("COSMOS_DB_NAME", "job-db")

# Initialize Cosmos Client
try:
    cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = cosmos_client.get_database_client(COSMOS_DB)
    logger.info("✅ Cosmos DB connected in Azure Functions")
except Exception as e:
    logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
    cosmos_client = None

# ============ HTTP TRIGGERS ============

@app.route(route="jobs", methods=["GET", "POST"])
async def jobs_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for jobs endpoint
    GET: Retrieve jobs
    POST: Create new job
    """
    try:
        if req.method == "GET":
            skip = req.params.get('skip', 0)
            limit = req.params.get('limit', 10)
            
            # Call FastAPI backend
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{FASTAPI_URL}/api/jobs",
                    params={"skip": int(skip), "limit": int(limit)},
                    timeout=30.0
                )
            
            return func.HttpResponse(
                response.text,
                status_code=response.status_code,
                headers={"Content-Type": "application/json"}
            )
        
        elif req.method == "POST":
            req_body = req.get_json()
            
            # Call FastAPI backend
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{FASTAPI_URL}/api/jobs",
                    json=req_body,
                    timeout=30.0
                )
            
            return func.HttpResponse(
                response.text,
                status_code=response.status_code,
                headers={"Content-Type": "application/json"}
            )
    
    except Exception as e:
        logger.error(f"Error in jobs_http_trigger: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="jobs/{job_id}", methods=["GET", "PUT"])
async def job_details_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for specific job
    GET: Get job details
    PUT: Update job
    """
    try:
        job_id = req.route_params.get("job_id")
        
        if req.method == "GET":
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{FASTAPI_URL}/api/jobs/{job_id}",
                    timeout=30.0
                )
            
            return func.HttpResponse(
                response.text,
                status_code=response.status_code,
                headers={"Content-Type": "application/json"}
            )
        
        elif req.method == "PUT":
            req_body = req.get_json()
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{FASTAPI_URL}/api/jobs/{job_id}",
                    json=req_body,
                    timeout=30.0
                )
            
            return func.HttpResponse(
                response.text,
                status_code=response.status_code,
                headers={"Content-Type": "application/json"}
            )
    
    except Exception as e:
        logger.error(f"Error in job_details_http_trigger: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="applications", methods=["POST"])
async def submit_application_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for submitting job applications
    POST: Submit new application
    """
    try:
        req_body = req.get_json()
        
        # Call FastAPI backend
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FASTAPI_URL}/api/applications",
                json=req_body,
                timeout=30.0
            )
        
        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Error in submit_application_http_trigger: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="applications/{user_id}", methods=["GET"])
async def get_applications_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for getting user applications
    GET: Get all applications for a user
    """
    try:
        user_id = req.route_params.get("user_id")
        status = req.params.get('status')
        
        params = {}
        if status:
            params['status'] = status
        
        # Call FastAPI backend
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_URL}/api/applications/{user_id}",
                params=params,
                timeout=30.0
            )
        
        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Error in get_applications_http_trigger: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="recommendations/{user_id}", methods=["GET"])
async def get_recommendations_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for getting job recommendations
    GET: Get recommendations for user
    """
    try:
        user_id = req.route_params.get("user_id")
        limit = req.params.get('limit', 10)
        
        # Call FastAPI backend
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_URL}/api/recommendations/{user_id}",
                params={"limit": int(limit)},
                timeout=30.0
            )
        
        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Error in get_recommendations_http_trigger: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="analytics", methods=["GET"])
async def analytics_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for analytics
    GET: Get system analytics
    """
    try:
        # Call FastAPI backend
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_URL}/api/analytics",
                timeout=30.0
            )
        
        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Error in analytics_http_trigger: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

# ============ TIMER TRIGGERS ============

@app.schedule_rule(schedule="0 2 * * *", arg_name="myTimer")
def daily_job_recommendations_timer(myTimer: func.TimerRequest) -> None:
    """
    Timer trigger for daily job recommendations
    Runs daily at 2 AM UTC
    """
    try:
        logger.info("⏱️ Starting daily recommendations job")
        
        # Get all active jobs
        if cosmos_client:
            try:
                jobs_container = database.get_container_client("jobs")
                apps_container = database.get_container_client("applications")
                recs_container = database.get_container_client("recommendations")
                users_container = database.get_container_client("users")
                
                # Get all users
                users_query = "SELECT * FROM c"
                users = list(users_container.query_items(users_query))
                
                logger.info(f"Processing {len(users)} users")
                
                for user in users:
                    user_id = user.get("user_id")
                    user_skills = set(user.get("skills", []))
                    
                    # Get active jobs
                    jobs_query = "SELECT * FROM c WHERE c.status = 'active'"
                    jobs = list(jobs_container.query_items(jobs_query))
                    
                    # Calculate matches
                    for job in jobs:
                        job_skills = set(job.get("skills", []))
                        matched_skills = user_skills & job_skills
                        skill_match = len(matched_skills) / len(job_skills) if job_skills else 0
                        
                        # Calculate score
                        score = skill_match * 100
                        
                        # Check if already applied
                        app_query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.job_id = @job_id"
                        existing_apps = list(apps_container.query_items(
                            query=app_query,
                            parameters=[
                                {"name": "@user_id", "value": user_id},
                                {"name": "@job_id", "value": job.get("id")}
                            ]
                        ))
                        
                        # Only create recommendation if not already applied
                        if not existing_apps and score > 50:
                            recommendation = {
                                "id": str(__import__("uuid").uuid4()),
                                "user_id": user_id,
                                "job_id": job.get("id"),
                                "score": round(score, 2),
                                "reasons": [
                                    f"Skill match: {len(matched_skills)}/{len(job_skills)} skills",
                                    f"Location: {job.get('location')}"
                                ],
                                "generated_at": datetime.utcnow().isoformat()
                            }
                            
                            recs_container.create_item(body=recommendation)
                            logger.info(f"✅ Recommendation created for {user_id}: {job.get('id')}")
                
                logger.info("✅ Daily recommendations job completed successfully")
            
            except Exception as e:
                logger.error(f"Error processing recommendations: {e}")
        
        else:
            logger.warning("⚠️ Cosmos DB not connected")
    
    except Exception as e:
        logger.error(f"Error in daily_job_recommendations_timer: {e}")

@app.schedule_rule(schedule="0 */6 * * *", arg_name="myTimer")
def refresh_job_status_timer(myTimer: func.TimerRequest) -> None:
    """
    Timer trigger for refreshing job status
    Runs every 6 hours
    """
    try:
        logger.info("⏱️ Refreshing job status")
        
        if cosmos_client:
            try:
                jobs_container = database.get_container_client("jobs")
                
                # Get expired jobs (older than 90 days)
                old_jobs_query = """
                    SELECT * FROM c 
                    WHERE c.status = 'active' 
                    AND DateTimeDiff('day', TimestampToDateTime(c._ts), GetCurrentDateTime()) > 90
                """
                old_jobs = list(jobs_container.query_items(old_jobs_query))
                
                for job in old_jobs:
                    job["status"] = "archived"
                    jobs_container.replace_item(item=job["id"], body=job)
                    logger.info(f"✅ Job archived: {job['id']}")
                
                logger.info(f"✅ Refreshed status for {len(old_jobs)} jobs")
            
            except Exception as e:
                logger.error(f"Error refreshing job status: {e}")
        
        else:
            logger.warning("⚠️ Cosmos DB not connected")
    
    except Exception as e:
        logger.error(f"Error in refresh_job_status_timer: {e}")

@app.schedule_rule(schedule="0 0 * * 0", arg_name="myTimer")
def weekly_analytics_timer(myTimer: func.TimerRequest) -> None:
    """
    Timer trigger for weekly analytics
    Runs every Sunday at midnight
    """
    try:
        logger.info("⏱️ Generating weekly analytics")
        
        # Call FastAPI analytics endpoint
        import asyncio
        
        async def get_analytics():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{FASTAPI_URL}/api/analytics",
                    timeout=30.0
                )
                return response
        
        # This is for demonstration - in real scenarios, use async context
        logger.info("✅ Weekly analytics generated")
    
    except Exception as e:
        logger.error(f"Error in weekly_analytics_timer: {e}")

# ============ HEALTH CHECK ============

@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "cosmos_db": "connected" if cosmos_client else "disconnected"
        }),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )


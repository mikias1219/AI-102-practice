# 🏗️ Azure Cosmos DB + Azure Functions + FastAPI Architecture Guide

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT APPLICATIONS                       │
│              (Web, Mobile, Desktop, Third-party)                │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE FUNCTIONS (Serverless)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  HTTP Trigger│  │ Timer Trigger│  │ Event Trigger│          │
│  │   GET/POST   │  │  Scheduling  │  │ Processing  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                  │                  │
│         └─────────────────┼──────────────────┘                  │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Python Application)               │
│  ┌────────────────────────────────────────────────────────────┐│
│  │           Core Business Logic & API Endpoints              ││
│  │  • Data Processing                                         ││
│  │  • Validation & Authorization                             ││
│  │  • Aggregation & Analytics                                ││
│  └────────────────────────────────────────────────────────────┘│
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              AZURE COSMOS DB (NoSQL Database)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Container 1 │  │  Container 2 │  │  Container 3 │         │
│  │    Users     │  │      Jobs    │  │ Applications │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  • Global Distribution   • Multi-region Replication            │
│  • Automatic Indexing    • Real-time Analytics                 │
│  • NoSQL Flexibility     • 99.99% SLA                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Data Flow

### 1️⃣ **User Request Flow**

```
User/Client
    ↓
HTTP Request (GET /jobs)
    ↓
Azure Function (HTTP Trigger)
    ↓
FastAPI Backend (Process Request)
    ↓
Query Cosmos DB
    ↓
Format Response
    ↓
Return JSON Response
    ↓
User receives data (jobs list)
```

### 2️⃣ **Job Application Submission**

```
User submits Job Application Form
    ↓
POST /applications
    ↓
Azure Function receives request
    ↓
FastAPI validates data
    ↓
Cosmos DB stores application
    ↓
Triggers Azure Function Timer
    ↓
Send confirmation email
    ↓
Update application status
```

### 3️⃣ **Background Processing (Scheduled)**

```
Timer Trigger (Daily at 2 AM)
    ↓
Azure Function processes
    ↓
FastAPI analytics endpoint
    ↓
Query all applications from Cosmos DB
    ↓
Calculate matches
    ↓
Update job recommendations
    ↓
Store results back in Cosmos DB
```

---

## 🏢 Components Explained

### 1. **Azure Cosmos DB**
```
├── Database: job-matching-db
│   ├── Container: users
│   │   ├── Partition Key: /user_id
│   │   └── TTL: 2592000 (30 days)
│   │
│   ├── Container: jobs
│   │   ├── Partition Key: /company_id
│   │   └── Indexes: [title, skills, location]
│   │
│   ├── Container: applications
│   │   ├── Partition Key: /user_id
│   │   └── Indexes: [job_id, status, created_date]
│   │
│   └── Container: recommendations
│       ├── Partition Key: /user_id
│       └── Composite indexes for analytics
```

### 2. **Azure Functions**
```
├── Function App: job-matcher-functions
│   ├── HTTP Trigger: api/jobs, api/applications
│   ├── Timer Trigger: daily-matching@0 2 * * *
│   ├── Event Hub Trigger: process-events
│   └── Queue Trigger: background-jobs
```

### 3. **FastAPI Backend**
```
├── Routes:
│   ├── GET  /api/jobs              → Fetch all jobs
│   ├── POST /api/jobs              → Create job
│   ├── GET  /api/jobs/{id}         → Get job details
│   ├── POST /api/applications      → Submit application
│   ├── GET  /api/recommendations   → Get recommendations
│   └── GET  /api/analytics         → Analytics dashboard
│
├── Database Layer:
│   ├── CosmosDB Client
│   ├── Query Builder
│   └── Connection Pool
│
└── Services:
    ├── JobService
    ├── ApplicationService
    ├── RecommendationService
    └── AnalyticsService
```

---

## 💾 Data Models (Cosmos DB Documents)

### **User Document**
```json
{
  "id": "user123",
  "user_id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "skills": ["Python", "Azure", "Docker"],
  "experience": 5,
  "location": "San Francisco",
  "created_at": "2024-11-13T10:00:00Z",
  "updated_at": "2024-11-13T10:00:00Z"
}
```

### **Job Document**
```json
{
  "id": "job456",
  "company_id": "company789",
  "title": "Senior Python Developer",
  "description": "We are looking for...",
  "skills": ["Python", "FastAPI", "Docker", "Azure"],
  "experience_required": 5,
  "location": "San Francisco",
  "salary": "$150K - $200K",
  "created_at": "2024-11-13T10:00:00Z",
  "status": "active"
}
```

### **Application Document**
```json
{
  "id": "app789",
  "user_id": "user123",
  "job_id": "job456",
  "status": "submitted",
  "match_score": 85.5,
  "created_at": "2024-11-13T10:00:00Z",
  "updated_at": "2024-11-13T10:00:00Z",
  "interview_date": null
}
```

### **Recommendation Document**
```json
{
  "id": "rec012",
  "user_id": "user123",
  "job_id": "job456",
  "score": 85.5,
  "reasons": [
    "Skill match: 90%",
    "Experience match: 85%",
    "Location compatible: Yes"
  ],
  "generated_at": "2024-11-13T02:00:00Z"
}
```

---

## 🚀 Implementation Steps

### **STEP 1: Set up Azure Cosmos DB**

```bash
# Create Resource Group
az group create --name myResourceGroup --location eastus

# Create Cosmos DB Account
az cosmosdb create \
  --name job-matching-db \
  --resource-group myResourceGroup \
  --locations regionName=eastus failoverPriority=0

# Create Database
az cosmosdb sql database create \
  --account-name job-matching-db \
  --resource-group myResourceGroup \
  --name job-db

# Create Containers
# Jobs Container
az cosmosdb sql container create \
  --account-name job-matching-db \
  --database-name job-db \
  --name jobs \
  --resource-group myResourceGroup \
  --partition-key-path "/company_id"

# Users Container
az cosmosdb sql container create \
  --account-name job-matching-db \
  --database-name job-db \
  --name users \
  --resource-group myResourceGroup \
  --partition-key-path "/user_id"

# Applications Container
az cosmosdb sql container create \
  --account-name job-matching-db \
  --database-name job-db \
  --name applications \
  --resource-group myResourceGroup \
  --partition-key-path "/user_id"
```

### **STEP 2: Set up Azure Functions**

```bash
# Create Function App
az functionapp create \
  --resource-group myResourceGroup \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name job-matcher-functions

# Deploy Function
func azure functionapp publish job-matcher-functions
```

### **STEP 3: Deploy FastAPI Backend**

```bash
# Create App Service Plan
az appservice plan create \
  --name job-api-plan \
  --resource-group myResourceGroup \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group myResourceGroup \
  --plan job-api-plan \
  --name job-api-backend \
  --runtime "PYTHON|3.11"
```

---

## 📝 Code Examples

### **FastAPI Backend (main.py)**

```python
from fastapi import FastAPI, HTTPException
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
import os

# Initialize FastAPI
app = FastAPI(title="Job Matching API")

# Initialize Cosmos DB
cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
cosmos_key = os.getenv("COSMOS_KEY")
cosmos_db_name = "job-db"

client = CosmosClient(cosmos_endpoint, cosmos_key)
database = client.get_database_client(cosmos_db_name)
jobs_container = database.get_container_client("jobs")
users_container = database.get_container_client("users")
applications_container = database.get_container_client("applications")

# ============ JOBS ENDPOINTS ============

@app.get("/api/jobs")
async def get_jobs(skip: int = 0, limit: int = 10):
    """Get all jobs"""
    try:
        query = "SELECT * FROM c ORDER BY c.created_at DESC OFFSET @skip LIMIT @limit"
        items = list(jobs_container.query_items(
            query=query,
            parameters=[
                {"name": "@skip", "value": skip},
                {"name": "@limit", "value": limit}
            ]
        ))
        return {"status": "success", "data": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get specific job"""
    try:
        query = "SELECT * FROM c WHERE c.id = @id"
        items = list(jobs_container.query_items(
            query=query,
            parameters=[{"name": "@id", "value": job_id}]
        ))
        if not items:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"status": "success", "data": items[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs")
async def create_job(job: dict):
    """Create new job posting"""
    try:
        job["id"] = job.get("id", job.get("job_id", str(uuid.uuid4())))
        job["created_at"] = datetime.utcnow().isoformat()
        job["status"] = "active"
        
        result = jobs_container.create_item(body=job)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ APPLICATIONS ENDPOINTS ============

@app.post("/api/applications")
async def submit_application(application: dict):
    """Submit job application"""
    try:
        application["id"] = str(uuid.uuid4())
        application["created_at"] = datetime.utcnow().isoformat()
        application["status"] = "submitted"
        
        result = applications_container.create_item(body=application)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/applications/{user_id}")
async def get_user_applications(user_id: str):
    """Get user's applications"""
    try:
        query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC"
        items = list(applications_container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}]
        ))
        return {"status": "success", "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ RECOMMENDATIONS ENDPOINTS ============

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get job recommendations"""
    try:
        query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.score DESC"
        items = list(recommendations_container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}]
        ))
        return {"status": "success", "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ ANALYTICS ENDPOINTS ============

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics"""
    try:
        # Total jobs
        jobs_query = "SELECT VALUE COUNT(1) FROM c"
        job_count = list(jobs_container.query_items(jobs_query))[0]
        
        # Total applications
        apps_query = "SELECT VALUE COUNT(1) FROM c"
        app_count = list(applications_container.query_items(apps_query))[0]
        
        # Average match score
        score_query = "SELECT VALUE AVG(c.match_score) FROM c WHERE c.match_score != null"
        avg_score = list(applications_container.query_items(score_query))[0] or 0
        
        return {
            "status": "success",
            "total_jobs": job_count,
            "total_applications": app_count,
            "average_match_score": round(avg_score, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **Azure Function (function_app.py)**

```python
import azure.functions as func
import json
import httpx
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient

# Initialize Function App
app = func.FunctionApp()

# FastAPI backend URL
FASTAPI_URL = "https://job-api-backend.azurewebsites.net"

# Cosmos DB
cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
cosmos_key = os.getenv("COSMOS_KEY")
cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)

# ============ HTTP TRIGGER ============

@app.route(route="jobs", methods=["GET"])
async def get_jobs_http(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger for getting jobs"""
    try:
        skip = req.params.get('skip', 0)
        limit = req.params.get('limit', 10)
        
        # Call FastAPI backend
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_URL}/api/jobs",
                params={"skip": skip, "limit": limit}
            )
        
        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.route(route="applications", methods=["POST"])
async def submit_application(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP trigger for submitting applications"""
    try:
        req_body = req.get_json()
        
        # Call FastAPI backend
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FASTAPI_URL}/api/applications",
                json=req_body
            )
        
        return func.HttpResponse(
            response.text,
            status_code=response.status_code,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

# ============ TIMER TRIGGER ============

@app.schedule_rule(
    schedule="0 2 * * *",  # Daily at 2 AM
    arg_name="myTimer"
)
async def daily_recommendations(myTimer: func.TimerRequest) -> None:
    """Timer trigger for daily job recommendations"""
    try:
        # Call FastAPI analytics endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_URL}/api/analytics"
            )
        
        if response.status_code == 200:
            data = response.json()
            # Process and store recommendations
            # Update Cosmos DB with new recommendations
            print(f"Daily recommendations job completed: {data}")
        else:
            print(f"Error calling FastAPI: {response.status_code}")
            
    except Exception as e:
        print(f"Error in daily recommendations: {str(e)}")
```

---

## 🔧 Configuration (.env)

```env
# Cosmos DB
COSMOS_ENDPOINT=https://job-matching-db.documents.azure.com:443/
COSMOS_KEY=your-cosmos-db-key
COSMOS_CONNECTION_STRING=your-connection-string

# FastAPI
FASTAPI_URL=https://job-api-backend.azurewebsites.net
API_KEY=your-api-key

# Azure Function
FUNCTION_APP_URL=https://job-matcher-functions.azurewebsites.net

# Azure Services
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=myResourceGroup
AZURE_STORAGE_ACCOUNT=your-storage-account

# Application
DEBUG=False
LOG_LEVEL=INFO
```

---

## 📊 Benefits of This Architecture

### **Scalability**
- ✅ Cosmos DB handles millions of documents
- ✅ Azure Functions auto-scale
- ✅ FastAPI handles concurrent requests

### **Performance**
- ✅ Global distribution with Cosmos DB
- ✅ Automatic indexing
- ✅ Multi-region replication
- ✅ 99.99% SLA

### **Cost Efficiency**
- ✅ Pay-per-request pricing for Functions
- ✅ Serverless (no VM management)
- ✅ On-demand Cosmos DB throughput

### **Reliability**
- ✅ Built-in redundancy
- ✅ Automatic failover
- ✅ Global replication
- ✅ Point-in-time restore

### **Flexibility**
- ✅ NoSQL (schema-less)
- ✅ Multiple APIs (SQL, MongoDB, Cassandra)
- ✅ Serverless + Managed services

---

## 🚀 Deployment Checklist

- [ ] Create Cosmos DB account
- [ ] Create containers with partition keys
- [ ] Deploy Azure Functions
- [ ] Deploy FastAPI backend
- [ ] Configure connection strings
- [ ] Set up monitoring & logging
- [ ] Configure auto-scaling policies
- [ ] Set up backups
- [ ] Test endpoints
- [ ] Deploy to production

---

## 📚 Learning Resources

- [Cosmos DB Documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/)
- [Azure Functions Guide](https://learn.microsoft.com/en-us/azure/azure-functions/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [Python SDK for Cosmos DB](https://github.com/Azure/azure-sdk-for-python)

---

## ❓ FAQ

**Q: Why use Cosmos DB instead of SQL Database?**
A: Cosmos DB is better for unstructured data, global distribution, and flexible schemas.

**Q: Can I run FastAPI without Azure Functions?**
A: Yes! You can deploy FastAPI directly to App Service or Container Instances.

**Q: How do I handle real-time updates?**
A: Use Azure SignalR Service with Functions and WebSockets.

**Q: What about authentication?**
A: Use Azure AD, API Keys, or OAuth 2.0 with FastAPI middleware.

**Q: How to monitor costs?**
A: Use Azure Cost Management + Billing in Azure Portal.

---

**Ready to build?** Start with Step 1! 🚀


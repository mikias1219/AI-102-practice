# 🎯 Azure Cosmos DB + Functions + FastAPI - Quick Reference

## 📊 Architecture At a Glance

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────────────────────┐
│   Azure Functions            │
│  (HTTP + Timer Triggers)     │
└──────┬───────────────────────┘
       │ HTTP calls
       ▼
┌──────────────────────────────┐
│   FastAPI Backend            │
│  (Business Logic)            │
└──────┬───────────────────────┘
       │ Query/Insert
       ▼
┌──────────────────────────────┐
│   Azure Cosmos DB            │
│  (NoSQL Database)            │
└──────────────────────────────┘
```

---

## 🔄 Data Flow Examples

### Example 1: User Uploads CV and Gets Job Matches

```
1. User submits CV via web form
   ├─> Sent to Azure Function (HTTP Trigger)
   ├─> Function validates input
   ├─> Calls FastAPI /api/recommendations endpoint
   ├─> FastAPI queries Cosmos DB for matching jobs
   ├─> FastAPI calculates match scores
   ├─> Stores recommendations in Cosmos DB
   ├─> Returns results to Function
   └─> Function returns JSON to User

Timeline: ~2-3 seconds total
```

### Example 2: Daily Scheduled Job Recommendations

```
1. Timer Trigger fires (Daily at 2 AM)
   ├─> Azure Function Timer runs
   ├─> Function queries all users from Cosmos DB
   ├─> For each user:
   │   ├─> Get user skills and experience
   │   ├─> Get all active jobs
   │   ├─> Calculate match scores
   │   └─> Store recommendations
   └─> Job completes

Timeline: Runs automatically, ~5-10 minutes
```

### Example 3: Submit Job Application

```
1. User clicks "Apply" button
   ├─> Sent to Azure Function (HTTP Trigger)
   ├─> Function receives application data
   ├─> Calls FastAPI POST /api/applications
   ├─> FastAPI validates application
   ├─> Cosmos DB stores application
   ├─> FastAPI returns confirmation
   ├─> Function sends confirmation email
   └─> User sees "Application Submitted"

Timeline: ~1-2 seconds
```

---

## 💾 Database Structure

### Jobs Collection
```json
{
  "id": "job-uuid",
  "company_id": "company-1",
  "title": "Senior Developer",
  "skills": ["Python", "FastAPI", "Docker"],
  "experience_required": 5,
  "location": "San Francisco",
  "status": "active"
}
```

### Applications Collection
```json
{
  "id": "app-uuid",
  "user_id": "user-123",
  "job_id": "job-uuid",
  "status": "submitted",
  "match_score": 85.5,
  "created_at": "2024-11-13T10:00:00Z"
}
```

### Recommendations Collection
```json
{
  "id": "rec-uuid",
  "user_id": "user-123",
  "job_id": "job-uuid",
  "score": 85.5,
  "reasons": ["Skill match: 80%", "Experience: Match"]
}
```

---

## 🚀 Quick Commands

### 1. Deploy Everything

```bash
# Set variables
export RESOURCE_GROUP="job-matcher-rg"
export REGION="eastus"
export COSMOS_ACCOUNT="job-cosmos-db"
export FUNCTION_APP="job-functions"
export WEB_APP="job-api"

# Create everything
az group create --name $RESOURCE_GROUP --location $REGION

# Cosmos DB
az cosmosdb create --name $COSMOS_ACCOUNT --resource-group $RESOURCE_GROUP

# Functions
az functionapp create \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --runtime python \
  --runtime-version 3.11

# App Service
az appservice plan create --name job-plan --resource-group $RESOURCE_GROUP --sku B2 --is-linux
az webapp create --name $WEB_APP --resource-group $RESOURCE_GROUP --plan job-plan --runtime "PYTHON|3.11"
```

### 2. Insert Sample Data

```bash
python << 'EOF'
from azure.cosmos import CosmosClient
import os, uuid
from datetime import datetime

ENDPOINT = os.getenv("COSMOS_ENDPOINT")
KEY = os.getenv("COSMOS_KEY")

client = CosmosClient(ENDPOINT, KEY)
db = client.get_database_client("job-db")
jobs = db.get_container_client("jobs")

job = {
    "id": str(uuid.uuid4()),
    "company_id": "company-1",
    "title": "Python Developer",
    "description": "Build APIs with FastAPI",
    "skills": ["Python", "FastAPI", "Docker"],
    "experience_required": 3,
    "location": "Remote",
    "status": "active",
    "created_at": datetime.utcnow().isoformat()
}

jobs.create_item(body=job)
print(f"✅ Job created: {job['id']}")
EOF
```

### 3. Test API

```bash
# Get jobs
curl "https://$WEB_APP.azurewebsites.net/api/jobs"

# Create job
curl -X POST "https://$WEB_APP.azurewebsites.net/api/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "comp-1",
    "title": "Backend Engineer",
    "skills": ["Python", "FastAPI"],
    "experience_required": 3,
    "location": "Remote"
  }'

# Get analytics
curl "https://$WEB_APP.azurewebsites.net/api/analytics"
```

### 4. Test Functions

```bash
# Via Function URL
curl "https://$FUNCTION_APP.azurewebsites.net/api/jobs"

# Via Function Core Tools locally
func start
# Then in another terminal:
curl http://localhost:7071/api/jobs
```

---

## 📈 Performance Tips

### 1. Partition Keys Matter
```
Jobs:        /company_id    (many jobs per company)
Users:       /user_id       (one profile per user)
Applications: /user_id      (many apps per user)
```

### 2. Indexing Strategy
```
- Index frequently queried fields
- Don't index unused fields
- Use composite indexes for common filters
```

### 3. Query Optimization
```sql
-- ❌ Bad: Scans all documents
SELECT * FROM c

-- ✅ Good: Uses partition key
SELECT * FROM c WHERE c.user_id = "user-123"

-- ✅ Best: Uses index
SELECT * FROM c WHERE c.status = "active" AND c.created_at > "2024-11-01"
```

### 4. Caching with Azure Functions
```python
import json

# Cache in-memory
_job_cache = {}
_cache_expiry = 0

@app.route(route="jobs-cached")
def get_jobs_cached(req):
    global _cache_expiry
    import time
    
    if time.time() < _cache_expiry and _job_cache:
        return func.HttpResponse(json.dumps(_job_cache))
    
    # Fresh query
    # ... query cosmos db ...
    
    _cache_expiry = time.time() + 300  # 5 min cache
    return func.HttpResponse(json.dumps(result))
```

---

## 🔒 Security Considerations

### 1. Use Managed Identities
```bash
# Instead of connection strings, use managed identities
az functionapp identity assign --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

### 2. Key Vault Integration
```bash
# Store secrets in Key Vault
az keyvault create --name job-kv --resource-group $RESOURCE_GROUP

# Reference in Functions
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings "CosmosConnection=@Microsoft.KeyVault(SecretUri=https://job-kv.vault.azure.net/secrets/cosmos-conn/)"
```

### 3. API Authentication
```python
# Add API Key middleware to FastAPI
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/api/jobs")
async def get_jobs(api_key: str = Depends(verify_api_key)):
    # Protected endpoint
    pass
```

---

## 📊 Monitoring Queries

### Check RU Consumption
```bash
# Via Azure CLI
az monitor metrics list \
  --resource /subscriptions/{subId}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DocumentDB/databaseAccounts/$COSMOS_ACCOUNT \
  --metric ConsumedRU \
  --start-time 2024-11-13T00:00:00Z
```

### Function Performance
```bash
# Check function logs
func azure functionapp publish $FUNCTION_APP --build remote
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

---

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Cosmos DB connection failed" | Invalid endpoint/key | Check `.env`, verify in Azure Portal |
| "Function timeout" | Query taking too long | Add indexes, optimize partition key |
| "High RU consumption" | Inefficient queries | Review query plan, add filters |
| "Cold start delays" | First function execution | Use Premium plan, keep functions warm |
| "API returns 403" | Partition key mismatch | Ensure partition key matches document |

---

## 📚 Key Concepts

### Partition Key
- **What**: Document field used to distribute data
- **Why**: Enables horizontal scaling
- **Example**: `user_id` for applications (all user data together)

### RU (Request Unit)
- **What**: Measure of throughput cost
- **Cost**: 1 RU ≈ 1 read of 1KB document
- **Pricing**: Pay per RU/second provisioned

### TTL (Time To Live)
- **What**: Auto-delete documents after time
- **Use**: Temporary data, recommendations
- **Example**: Recommendations expire after 30 days

### Trigger Types
- **HTTP**: RESTful endpoints
- **Timer**: Scheduled jobs (cron)
- **Event Hub**: Stream processing
- **Queue**: Async processing

---

## 🎯 Next Steps

1. **Create Resource Group** → `az group create`
2. **Setup Cosmos DB** → Follow DEPLOYMENT_GUIDE.md
3. **Deploy FastAPI** → `az webapp create` + `git push`
4. **Deploy Functions** → `func azure functionapp publish`
5. **Insert Data** → Use sample job insert script
6. **Test Endpoints** → Use curl commands above
7. **Monitor & Scale** → Setup Application Insights
8. **Go Live** → Configure custom domain + SSL

---

## 💡 Tips & Tricks

```bash
# Quick test if everything is connected
curl https://FUNCTION_APP.azurewebsites.net/health

# View real-time logs
func azure functionapp publish $FUNCTION_APP --build remote
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP --follow

# Check Cosmos DB stats
az cosmosdb sql database throughput show \
  --account-name $COSMOS_ACCOUNT \
  --database-name job-db \
  --resource-group $RESOURCE_GROUP

# Export data from Cosmos DB
az cosmosdb sql restore --help
```

---

**Need help? Check ARCHITECTURE_GUIDE.md and DEPLOYMENT_GUIDE.md!** 🚀


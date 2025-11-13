# 🚀 Complete Deployment Guide: Cosmos DB + Azure Functions + FastAPI

## 📋 Prerequisites

- Azure Subscription (with credits or payment method)
- Azure CLI installed (`az --version`)
- Python 3.11+
- Git installed
- Docker (for containerization)

---

## 🔧 PHASE 1: Azure Cosmos DB Setup

### Step 1.1: Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="job-matcher-rg"
REGION="eastus"
COSMOS_ACCOUNT="job-matching-cosmos"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $REGION

echo "✅ Resource group created"
```

### Step 1.2: Create Cosmos DB Account

```bash
# Create Cosmos DB account (takes 5-10 minutes)
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --locations regionName=$REGION failoverPriority=0 \
  --capabilities EnableServerless \
  --default-consistency-level Session

echo "✅ Cosmos DB account created"
```

### Step 1.3: Create Database and Containers

```bash
# Create database
az cosmosdb sql database create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --name job-db

# Create Jobs Container
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name job-db \
  --name jobs \
  --resource-group $RESOURCE_GROUP \
  --partition-key-path "/company_id" \
  --throughput 400

# Create Users Container
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name job-db \
  --name users \
  --resource-group $RESOURCE_GROUP \
  --partition-key-path "/user_id" \
  --throughput 400

# Create Applications Container
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name job-db \
  --name applications \
  --resource-group $RESOURCE_GROUP \
  --partition-key-path "/user_id" \
  --throughput 400

# Create Recommendations Container
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --database-name job-db \
  --name recommendations \
  --resource-group $RESOURCE_GROUP \
  --partition-key-path "/user_id" \
  --throughput 400

echo "✅ All containers created"
```

### Step 1.4: Get Cosmos DB Connection String

```bash
# Get endpoint and key
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query documentEndpoint \
  --output tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query primaryMasterKey \
  --output tsv)

COSMOS_CONNECTION=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query primaryConnectionString \
  --output tsv)

echo "COSMOS_ENDPOINT=$COSMOS_ENDPOINT"
echo "COSMOS_KEY=$COSMOS_KEY"
```

---

## 📦 PHASE 2: FastAPI Backend Setup

### Step 2.1: Create App Service Plan

```bash
APP_SERVICE_PLAN="job-api-plan"
WEB_APP_NAME="job-api-backend-$RANDOM"

# Create App Service Plan (Linux)
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B2 \
  --is-linux

echo "✅ App Service Plan created"
```

### Step 2.2: Deploy FastAPI to App Service

```bash
# Create Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $WEB_APP_NAME \
  --runtime "PYTHON|3.11"

# Configure environment variables
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_KEY="$COSMOS_KEY" \
    COSMOS_DB_NAME="job-db" \
    WEBSITES_PORT=8000

echo "✅ Web App created"
```

### Step 2.3: Deploy Code to App Service

```bash
# Configure deployment from local Git
az webapp deployment user set \
  --user-name azuredeployuser \
  --password P@ssw0rd1234!

# Setup local Git deployment
az webapp deployment source config-local-git \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP

# Add Azure remote to git
DEPLOYMENT_URL=$(az webapp deployment source config-local-git \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query url \
  --output tsv)

# Deploy via Git
git remote add azure $DEPLOYMENT_URL
git push azure main

# Or deploy via ZIP
cd /path/to/project
zip -r app.zip . -x ".*" "*.git*" "__pycache__/*"
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --src-path app.zip

echo "✅ FastAPI deployed to App Service"
```

### Step 2.4: Verify FastAPI Deployment

```bash
# Get the URL
API_URL="https://$WEB_APP_NAME.azurewebsites.net"

# Test the API
curl "$API_URL/health"

echo "✅ API URL: $API_URL"
```

---

## 🔧 PHASE 3: Azure Functions Setup

### Step 3.1: Create Function App

```bash
FUNCTION_APP="job-matcher-functions"
STORAGE_ACCOUNT="jobmatcherstorage$RANDOM"

# Create Storage Account (required for Functions)
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $REGION \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $REGION \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT

echo "✅ Function App created"
```

### Step 3.2: Configure Function App Settings

```bash
# Set environment variables
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    FASTAPI_URL="$API_URL" \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_KEY="$COSMOS_KEY" \
    COSMOS_DB_NAME="job-db"

echo "✅ Function App configured"
```

### Step 3.3: Deploy Functions

```bash
# Install Azure Functions Core Tools
# macOS: brew tap azure/azure && brew install azure-functions-core-tools@4
# Linux: curl https://aka.ms/func-cli-install | bash
# Windows: Invoke-WebRequest -Uri https://aka.ms/func-cli-install -OutFile func-cli-installer.exe

# Create functions.json if not exists
# Then deploy
cd azure-agent-demo
func azure functionapp publish $FUNCTION_APP

echo "✅ Functions deployed"
```

---

## 📊 PHASE 4: Data Setup & Testing

### Step 4.1: Insert Sample Data

```python
# Create test_data_insert.py
from azure.cosmos import CosmosClient
import os
from datetime import datetime
import uuid

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client("job-db")
jobs_container = database.get_container_client("jobs")

# Sample jobs
sample_jobs = [
    {
        "id": str(uuid.uuid4()),
        "company_id": "company1",
        "title": "Senior Python Developer",
        "description": "Looking for senior Python developer with Azure experience",
        "skills": ["Python", "FastAPI", "Docker", "Azure"],
        "experience_required": 5,
        "location": "San Francisco, CA",
        "salary_min": 150000,
        "salary_max": 200000,
        "job_type": "Full-time",
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "company_id": "company2",
        "title": "Cloud Solutions Architect",
        "description": "Architect cloud solutions on Azure platform",
        "skills": ["Azure", "Cloud Architecture", "Python", "Terraform"],
        "experience_required": 8,
        "location": "New York, NY",
        "salary_min": 180000,
        "salary_max": 250000,
        "job_type": "Full-time",
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    }
]

# Insert jobs
for job in sample_jobs:
    jobs_container.create_item(body=job)
    print(f"✅ Inserted job: {job['title']}")

print("✅ Sample data inserted successfully")
```

### Step 4.2: Test API Endpoints

```bash
# Get all jobs
curl "$API_URL/api/jobs?skip=0&limit=10"

# Create job
curl -X POST "$API_URL/api/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "company3",
    "title": "Backend Engineer",
    "description": "Build scalable APIs",
    "skills": ["Python", "FastAPI"],
    "experience_required": 3,
    "location": "Remote",
    "job_type": "Full-time"
  }'

# Get analytics
curl "$API_URL/api/analytics"

echo "✅ API tests completed"
```

### Step 4.3: Test Azure Functions

```bash
# Get jobs via Function
curl "https://$FUNCTION_APP.azurewebsites.net/api/jobs?skip=0&limit=10"

# Submit application via Function
curl -X POST "https://$FUNCTION_APP.azurewebsites.net/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "job_id": "job123",
    "status": "submitted"
  }'

echo "✅ Functions tests completed"
```

---

## 📈 PHASE 5: Monitoring & Logging

### Step 5.1: Create Application Insights

```bash
AI_NAME="job-matcher-insights"

az monitor app-insights component create \
  --app $AI_NAME \
  --location $REGION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Get instrumentation key
AI_KEY=$(az monitor app-insights component show \
  --app $AI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

# Link to App Service
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$AI_KEY

# Link to Function App
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$AI_KEY

echo "✅ Application Insights configured"
```

### Step 5.2: Set up Alerts

```bash
# Create alert for high function failures
az monitor metrics alert create \
  --name "HighFunctionFailures" \
  --resource-group $RESOURCE_GROUP \
  --scopes "/subscriptions/{subscriptionId}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$FUNCTION_APP" \
  --condition "avg FailedFunctionRuns > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email azureadmin@company.com

echo "✅ Alerts configured"
```

---

## 💰 PHASE 6: Cost Optimization

### Monitor Costs

```bash
# View current costs
az consumption budget list --resource-group $RESOURCE_GROUP

# Set budget alert
az consumption budget create \
  --name JobMatcherBudget \
  --category Cost \
  --limit 100 \
  --time-period Monthly \
  --resource-group $RESOURCE_GROUP
```

### Optimize Throughput

```bash
# Switch to autoscale (Cosmos DB)
az cosmosdb sql container update \
  --account-name $COSMOS_ACCOUNT \
  --database-name job-db \
  --name jobs \
  --resource-group $RESOURCE_GROUP \
  --max-throughput 4000

echo "✅ Autoscale enabled"
```

---

## 🔄 PHASE 7: CI/CD Pipeline (GitHub Actions)

### Create .github/workflows/deploy.yml

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

env:
  RESOURCE_GROUP: job-matcher-rg
  WEB_APP_NAME: job-api-backend
  FUNCTION_APP: job-matcher-functions

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/
      
      - name: Deploy to App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.WEB_APP_NAME }}
          package: .
      
      - name: Deploy Functions
        run: |
          func azure functionapp publish ${{ env.FUNCTION_APP }}
```

---

## 📝 Environment Variables Summary

Create `.env` file:

```env
# Azure
SUBSCRIPTION_ID=your-subscription-id
RESOURCE_GROUP=job-matcher-rg
REGION=eastus

# Cosmos DB
COSMOS_ENDPOINT=https://job-matching-cosmos.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DB_NAME=job-db

# FastAPI
FASTAPI_URL=https://job-api-backend.azurewebsites.net
API_KEY=your-api-key

# Azure Functions
FUNCTION_APP_URL=https://job-matcher-functions.azurewebsites.net

# Application
DEBUG=False
LOG_LEVEL=INFO
```

---

## ✅ Verification Checklist

- [ ] Resource group created
- [ ] Cosmos DB account created
- [ ] Database and containers created
- [ ] FastAPI deployed to App Service
- [ ] Functions deployed
- [ ] Environment variables configured
- [ ] Sample data inserted
- [ ] API endpoints tested
- [ ] Monitoring configured
- [ ] Backups enabled

---

## 🆘 Troubleshooting

### Cosmos DB Connection Issues
```bash
# Test connection
python -c "
from azure.cosmos import CosmosClient
import os
client = CosmosClient(os.getenv('COSMOS_ENDPOINT'), os.getenv('COSMOS_KEY'))
print('✅ Connected')
"
```

### Function App Not Working
```bash
# Check logs
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

### FastAPI Not Responding
```bash
# Check App Service logs
az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
```

---

**🎉 You're all set! Your cloud infrastructure is ready!**


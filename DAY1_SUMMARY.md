# Day 1 Summary: Microsoft Foundry Services Foundation
## AI-102 Certification Practice - Completed Tasks

**Date**: December 30, 2025  
**Focus Area**: Plan and manage Azure AI solutions (20-25% of exam)  
**Status**: ✅ All 5 labs completed

---

## 📋 Overview

Day 1 focused on establishing the foundation for working with Microsoft Foundry Services (formerly Azure AI Foundry). All labs were successfully completed with working implementations, proper environment setup, and security best practices.

---

## ✅ Lab 1: Use Azure AI Services

### Objectives Completed
- ✅ Selected appropriate Microsoft Foundry Services
- ✅ Created Azure AI resource (Cognitive Services)
- ✅ Determined default endpoint for service
- ✅ Installed and utilized SDKs and APIs

### Implementation Details

**Resources Created:**
- **Azure AI Services Resource**: `ai-102-practice-111`
- **Location**: East US
- **Endpoint**: `https://ai-102-practice-111.cognitiveservices.azure.com/`
- **Key**: Configured and stored securely

**Code Implemented:**
1. **REST API Client** (`rest-client/rest-client.py`)
   - Language detection using REST API
   - Direct HTTP requests to Azure AI Services
   - Demonstrates API authentication with subscription keys

2. **SDK Client** (`sdk-client/sdk-client.py`)
   - Language detection using Azure SDK
   - Uses `azure-ai-textanalytics` package
   - Demonstrates SDK-based authentication

**Environment Setup:**
- ✅ Shared Python virtual environment created
- ✅ Shared `.env` file for credentials
- ✅ `python-dotenv` for environment variable management
- ✅ All dependencies installed (`azure-ai-textanalytics`, `python-dotenv`)

**Key Learnings:**
- REST API vs SDK: When to use each approach
- Endpoint format: `https://<resource-name>.cognitiveservices.azure.com/`
- Authentication: Subscription key in headers (`Ocp-Apim-Subscription-Key`)
- API versioning: Important for compatibility

---

## ✅ Lab 2: AI Services Security

### Objectives Completed
- ✅ Managed and protected account keys
- ✅ Managed authentication for Microsoft Foundry Service resources
- ✅ Planned for Responsible AI principles

### Implementation Details

**Resources Created:**
- **Azure Key Vault**: `ai-102-keyvault-7526`
- **Service Principal**: Created with app ID and password
- **Role Assignment**: Cognitive Services User role assigned

**Code Implemented:**
- **Key Vault Client** (`keyvault_client/keyvault-client.py`)
  - Retrieves AI Service key from Azure Key Vault
  - Uses Service Principal authentication
  - Demonstrates secure credential management

**Security Configuration:**
- ✅ Keys stored in Azure Key Vault (not in code)
- ✅ Service Principal authentication (not user credentials)
- ✅ Client Secret Credential for authentication
- ✅ Key Vault access policies configured

**Environment Variables:**
```env
KEY_VAULT=ai-102-keyvault-7526
TENANT_ID=<tenant-id>
APP_ID=<app-id>
APP_PASSWORD=<app-password>
```

**Key Learnings:**
- Never hardcode secrets in code
- Use Azure Key Vault for secret management
- Service Principals for application authentication
- Managed Identity vs Service Principal: When to use each

---

## ✅ Lab 3: Monitor AI Services

### Objectives Completed
- ✅ Monitored Azure AI resource
- ✅ Managed costs for Microsoft Foundry Services

### Implementation Details

**Monitoring Setup:**
- ✅ Metrics configured in Azure Portal
- ✅ Alerts configured for API calls
- ✅ Cost tracking enabled

**Test Script Created:**
- **test-api.sh**: Generates API calls for monitoring
  - Loads credentials from shared `.env`
  - Makes Language Detection API calls
  - Demonstrates metric generation

**Monitoring Features:**
- API call tracking
- Response time monitoring
- Error rate tracking
- Cost per API call
- Usage analytics

**Key Learnings:**
- Metrics appear in Azure Portal within 2-5 minutes
- Monitor for cost optimization
- Set up alerts for unusual activity
- Track usage patterns for capacity planning

---

## ✅ Lab 4: Use a Container

### Objectives Completed
- ✅ Planned and implemented container deployment
- ✅ Deployed AI models using appropriate deployment options

### Implementation Details

**Container Deployment:**
- ✅ Azure Container Instance (ACI) deployed
- ✅ Text Analytics container image pulled
- ✅ Container accessible via public IP
- ✅ REST API calls tested against container

**Scripts Created:**
1. **deploy-container.sh**: Deploys container to ACI
2. **check-status.sh**: Checks container status
3. **test-container.sh**: Tests container API endpoints

**Container Configuration:**
- **Image**: `mcr.microsoft.com/azure-cognitive-services/textanalytics/language`
- **Region**: East US
- **Resource Group**: AI-102
- **Public IP**: Configured for external access

**Key Learnings:**
- Containers enable offline/edge deployment
- Container instances for quick testing
- Container Registry for production images
- Network security considerations for containers
- When to use containers vs cloud endpoints

---

## ✅ Lab 5: Implement Content Safety

### Objectives Completed
- ✅ Implemented content moderation solutions
- ✅ Configured responsible AI insights
- ✅ Implemented responsible AI features
- ✅ Prevented harmful behavior

### Implementation Details

**Resources Created:**
- **Azure AI Content Safety**: `ai-102-content-safety`
- **Location**: East US
- **Pricing Tier**: F0 (Free)
- **Endpoint**: `https://eastus.api.cognitive.microsoft.com/`

**Code Implemented:**
- **Content Safety Client** (`prompt-shield.py`)
  - Text content moderation
  - Analyzes for: Hate, Self-harm, Sexual, Violence
  - Returns severity levels (0-4)
  - Blocklist matching support

**Content Safety Features:**
- Text moderation API
- Image moderation (available via Azure AI Foundry)
- Prompt Shields (jailbreak detection - via Azure AI Foundry)
- Protected material detection

**Environment Configuration:**
```env
CONTENT_SAFETY_ENDPOINT=https://eastus.api.cognitive.microsoft.com/
CONTENT_SAFETY_KEY=<key>
```

**Key Learnings:**
- Content Safety is a separate service from AI Services
- Different endpoint format for Content Safety
- Severity levels: 0 (Safe) to 4 (Very High)
- Prompt Shields require Azure AI Foundry access
- Responsible AI is a critical component

---

## 🛠️ Infrastructure Setup

### Shared Environment Configuration

**Location**: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/`

**Files:**
- **`.env`**: Shared environment variables for all labs
  ```env
  # Azure AI Services (Lab 1)
  AI_SERVICE_ENDPOINT=https://ai-102-practice-111.cognitiveservices.azure.com/
  AI_SERVICE_KEY=<key>
  
  # Azure Key Vault (Lab 2)
  KEY_VAULT=ai-102-keyvault-7526
  TENANT_ID=<tenant-id>
  APP_ID=<app-id>
  APP_PASSWORD=<app-password>
  
  # Azure AI Content Safety (Lab 5)
  CONTENT_SAFETY_ENDPOINT=https://eastus.api.cognitive.microsoft.com/
  CONTENT_SAFETY_KEY=<key>
  ```

- **`venv/`**: Shared Python virtual environment
  - `python-dotenv`: Environment variable loading
  - `azure-ai-textanalytics`: Text Analytics SDK
  - `azure-identity`: Authentication
  - `azure-keyvault-secrets`: Key Vault access
  - `requests`: HTTP requests

### Security Best Practices Implemented

1. ✅ **Credentials in `.env` file** (not in code)
2. ✅ **`.env` in `.gitignore`** (not committed to Git)
3. ✅ **Azure Key Vault** for production secrets
4. ✅ **Service Principal** for application authentication
5. ✅ **No hardcoded secrets** in any code files

---

## 📊 Resources Created

| Resource Name | Type | Purpose | Status |
|--------------|------|---------|--------|
| `ai-102-practice-111` | Cognitive Services | AI Services endpoint | ✅ Active |
| `ai-102-keyvault-7526` | Key Vault | Secret management | ✅ Active |
| `ai-102-content-safety` | Content Safety | Content moderation | ✅ Active |
| Container Instance | ACI | Container deployment | ✅ Deployed |

---

## 🎯 Key Concepts Mastered

### 1. Microsoft Foundry Services
- Understanding the new platform architecture
- Service selection criteria
- Endpoint formats and authentication

### 2. Authentication Methods
- **Subscription Keys**: Simple, for development
- **Service Principals**: For applications
- **Managed Identity**: For Azure-hosted apps
- **Key Vault**: For secure secret storage

### 3. Deployment Options
- **Cloud Endpoints**: Standard Azure AI Services
- **Containers**: For offline/edge scenarios
- **SDK vs REST**: When to use each

### 4. Monitoring & Cost Management
- Metrics and analytics
- Alert configuration
- Cost tracking and optimization

### 5. Responsible AI
- Content Safety implementation
- Content moderation
- Prompt Shields (jailbreak detection)
- Ethical AI practices

---

## 📝 Exam Focus Areas Covered

Based on AI-102 exam objectives (20-25% weight):

✅ **Plan and manage an Azure AI solution**
- Select appropriate services
- Provision resources
- Manage authentication
- Monitor services
- Manage costs

✅ **Implement responsible AI**
- Content Safety
- Content moderation
- Prompt Shields
- Harm detection

---

## 🚀 Next Steps: Day 2

**Focus**: Generative AI Solutions (15-20% of exam)

1. **Azure OpenAI Provisioning**
   - Create Azure OpenAI resource
   - Deploy models
   - Configure parameters

2. **Prompt Engineering**
   - Submit prompts
   - Improve responses
   - Apply techniques

3. **RAG Patterns**
   - Ground models in data
   - Deploy Foundry projects
   - Implement retrieval-augmented generation

4. **Image Generation**
   - DALL-E models
   - Multimodal models

---

## 📚 Important Files Reference

### Setup Guides
- `LAB2_SETUP.md`: Key Vault and Service Principal setup
- `LAB3_SETUP.md`: Monitoring configuration
- `LAB4_SETUP.md`: Container deployment guide
- `LAB5_SETUP.md`: Content Safety setup

### Code Files
- `01-use-azure-ai-services/Python/rest-client/rest-client.py`
- `01-use-azure-ai-services/Python/sdk-client/sdk-client.py`
- `02-ai-services-security/Python/keyvault_client/keyvault-client.py`
- `03-monitor-ai-services/test-api.sh`
- `04-use-a-container/deploy-container.sh`
- `04-use-a-container/test-container.sh`
- `05-implement-content-safety/Python/prompt-shield.py`

### Configuration
- `01-use-azure-ai-services/Python/.env`: Shared credentials
- `01-use-azure-ai-services/Python/venv/`: Shared virtual environment
- `.gitignore`: Security configuration

---

## ✅ Completion Checklist

- [x] Lab 1: Azure AI Services (REST & SDK)
- [x] Lab 2: Security (Key Vault)
- [x] Lab 3: Monitoring
- [x] Lab 4: Container Deployment
- [x] Lab 5: Content Safety
- [x] Environment setup (shared .env & venv)
- [x] Security configuration (.gitignore)
- [x] All scripts tested and working
- [x] Documentation created

---

## 🎓 Study Notes

### Critical Exam Topics
1. **Service Selection**: Know when to use which service
2. **Authentication**: Understand all methods and when to use each
3. **Deployment**: Cloud vs Container trade-offs
4. **Security**: Key Vault, Service Principals, Managed Identity
5. **Monitoring**: Metrics, alerts, cost management
6. **Responsible AI**: Content Safety, moderation, Prompt Shields

### Common Pitfalls to Avoid
- ❌ Hardcoding secrets in code
- ❌ Using user credentials for applications
- ❌ Not monitoring costs
- ❌ Ignoring Responsible AI principles
- ❌ Not understanding endpoint formats

### Best Practices
- ✅ Always use Key Vault for production
- ✅ Use Service Principals for apps
- ✅ Monitor costs and usage
- ✅ Implement Content Safety
- ✅ Use shared environments for efficiency

---

**Status**: Day 1 Complete ✅  
**Ready for**: Day 2 - Generative AI Solutions

---

*Last Updated: December 30, 2025*


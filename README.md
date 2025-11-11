# 🤖 Azure AI Agent Suite - Job Matching & AI Chat

A comprehensive Python + Streamlit application for intelligent job matching using Azure AI services with semantic embeddings and multi-turn agent conversations.

## ✨ Features

### 🤖 **Agent Chat**
- Multi-turn conversations with Azure AI Agent
- PDF context support for document-based Q&A
- Real-time responses with latency metrics

### 💼 **Job Matcher (Embedding-Based)**
- Upload CV (PDF) - Azure Document Intelligence extracts full text
- Semantic job matching using Azure OpenAI embeddings
- 60+ technical skill recognition
- Experience level detection
- Ranked results with detailed analysis
- Matched/missing skills breakdown

### 📋 **View Jobs**
- Browse all posted job opportunities
- See complete job details (description, skills, location, salary)
- Real-time data from Azure Blob Storage

### 👨‍💼 **Admin Panel**
- Post new job listings
- View/manage job postings
- Secure authentication

### ⚙️ **Settings**
- System status & configuration
- Feature availability
- API configuration overview

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Azure Subscription with:
  - Azure AI Projects (Agent)
  - Azure OpenAI (Embeddings)
  - Azure Document Intelligence (CV extraction)
  - Azure Blob Storage (Job storage)
  - Azure Credentials (Service Principal or User)

### Installation

```bash
# Clone repository
git clone https://github.com/mikias1219/AI-102-practice.git
cd azure-agent-demo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file with your Azure credentials:

```env
# Azure Subscription & Resources
SUBSCRIPTION_ID=your-subscription-id
RESOURCE_GROUP=your-resource-group
ACCOUNT_NAME=your-ai-resource-name
PROJECT_NAME=your-project-name

# Azure AI Agent
AGENT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AGENT_ID=asst_your_agent_id

# Azure OpenAI (for embeddings)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure Blob Storage (for job persistence)
AZURE_STORAGE_ACCOUNT_NAME=your-storage-account
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
BLOB_CONTAINER_CVS=cvs
BLOB_CONTAINER_JOBS=jobs

# Document Intelligence (for CV extraction)
DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-region.api.cognitive.microsoft.com/
DOCUMENT_INTELLIGENCE_API_KEY=your-doc-intel-key

# Admin Credentials
ADMIN_PASSWORD=your-secure-password
ADMIN_EMAIL=admin@company.com

# Optional: OpenAI API (fallback embeddings)
OPENAI_API_KEY=your-openai-api-key
```

### Run Application

```bash
streamlit run main_with_embeddings.py
```

Visit: `http://localhost:8501`

## 📊 How It Works

### Job Matching Flow

```
1. User uploads CV (PDF)
   ↓
2. Azure Document Intelligence extracts text
   ↓
3. Skills extracted (60+ keyword database)
4. Experience years detected from text
   ↓
5. CV converted to embedding (Azure OpenAI)
   ↓
6. Compared with job embeddings
   ↓
7. Scores calculated:
   - Embedding similarity (semantic)
   - Keyword matching (skills)
   - Experience matching
   - Education matching
   ↓
8. Results ranked by overall score
   ↓
9. Display with analysis & recommendations
```

### AI Agent Integration

```
1. User sends message
   ↓
2. Optional PDF context attached
   ↓
3. Message sent to Azure AI Agent
   ↓
4. Agent processes in thread
   ↓
5. Response retrieved and displayed
   ↓
6. Metrics shown (latency, token usage)
```

## 📁 Project Structure

```
azure-agent-demo/
├── main_with_embeddings.py        # Main Streamlit app (ACTIVE)
├── embedding_matcher.py            # Job matching engine
├── admin_panel.py                  # Admin interface
├── advanced_agents.py              # Advanced agent framework
├── agent_testing.py                # Testing utilities
├── job_matching.py                 # Document Intelligence CV parsing
├── main.py                         # Basic agent chat app
├── main_enhanced.py                # Enhanced UI version
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── SYSTEM_INFO.txt                 # Configuration guide
└── README.md                       # This file
```

## 🔑 Key Technologies

- **Streamlit**: Web UI framework
- **Azure AI Projects SDK**: Agent integration
- **Azure OpenAI**: Embeddings & LLM
- **Azure Document Intelligence**: PDF text extraction
- **Azure Blob Storage**: Data persistence
- **Azure Identity**: Authentication
- **PyPDF2**: PDF processing fallback
- **NumPy**: Vector operations

## 📊 Sample Jobs Included

The system comes with 3 sample jobs:

1. **Senior Python Developer** @ TechCorp (San Francisco, CA)
2. **Cloud Solutions Architect** @ CloudSystems Inc (New York, NY)
3. **AI/ML Engineer** @ IntelliAI (Remote)

## 🎯 Skills Recognition (60+)

**Languages:** Python, Java, JavaScript, C#, Go, Rust, TypeScript...
**Cloud:** Azure, AWS, GCP...
**DevOps:** Docker, Kubernetes, Terraform, CI/CD...
**Databases:** PostgreSQL, MongoDB, Redis, Elasticsearch...
**AI/ML:** TensorFlow, PyTorch, Machine Learning, NLP...
**Frameworks:** FastAPI, Django, React, Spring...

## 🔐 Admin Credentials

Default admin login (update in `.env`):
- **Email:** admin@company.com
- **Password:** SuperSecurePassword123!

## 🐛 Troubleshooting

### "Azure OpenAI client not available"
- Check `AZURE_OPENAI_ENDPOINT` format (should be `.cognitiveservices.azure.com/`)
- Verify `AZURE_OPENAI_API_KEY` is valid
- Ensure API version is `2024-12-01-preview`

### "Jobs not showing in View Jobs"
- Check Blob Storage credentials
- Verify `BLOB_CONTAINER_JOBS` exists
- Ensure jobs were posted via Admin Panel

### "Document Intelligence extraction failing"
- Verify `DOCUMENT_INTELLIGENCE_ENDPOINT` is reachable
- Check API key validity
- App will fallback to PyPDF2

### "Admin login fails"
- Verify `ADMIN_PASSWORD` in `.env` matches input
- Check `ADMIN_EMAIL` format

## 📈 Performance

- CV extraction: ~2-3 seconds (Document Intelligence)
- Embedding generation: ~100ms (Azure OpenAI)
- Job matching: ~1-2 seconds (3 jobs)
- Agent response: ~2-5 seconds (depends on complexity)

## 🚀 Production Deployment

For production, consider:

1. **Authentication:** Use Azure AD instead of hardcoded credentials
2. **Scaling:** Deploy to Azure Container Instances or App Service
3. **Monitoring:** Enable Application Insights
4. **Security:** Store secrets in Azure Key Vault
5. **Caching:** Use Redis for session management
6. **Load Balancing:** Use Azure Traffic Manager

## 📝 API Integration Example

```python
from embedding_matcher import SemanticJobMatcher

# Initialize matcher
matcher = SemanticJobMatcher()

# Get all jobs
jobs = matcher.get_all_jobs()

# Match CV
cv_text = "Senior Python Developer with 8 years Azure experience..."
skills = ["Python", "Azure", "Docker"]
experience = 8

matches = matcher.match_cv_to_jobs(cv_text, skills, experience)

# Print results
for match in matches:
    print(f"{match.job_title}: {match.overall_score:.1%}")
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Built with Azure AI services for intelligent job matching and AI-powered conversations.

## 🔗 Resources

- [Azure AI Projects](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## ⭐ Support

If you found this helpful, please star the repository!

---

**Status:** ✅ Production Ready  
**Last Updated:** November 2025  
**Version:** 2.0 (Enhanced with Document Intelligence & Dual Embeddings)


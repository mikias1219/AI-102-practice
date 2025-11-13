"""
Setup Azure Cosmos DB Database & Containers
Auto-creates database and all required containers for the job matching system
"""

from azure.cosmos import CosmosClient, PartitionKey, exceptions
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Disable verbose Azure SDK logging
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.core').setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

# ============================================================
# COSMOS DB CONFIGURATION
# ============================================================

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "https://job-matching-cosmos.documents.azure.com:443/")
COSMOS_KEY = os.getenv("COSMOS_KEY", "")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME", "job-db")

# Container configurations
# Note: No throughput for serverless accounts (pay-per-request)
CONTAINERS = {
    "jobs": {
        "partition_key": "/company_id",
        "throughput": None,  # Serverless account
        "description": "Job postings from companies"
    },
    "users": {
        "partition_key": "/user_id",
        "throughput": None,  # Serverless account
        "description": "User profiles"
    },
    "applications": {
        "partition_key": "/user_id",
        "throughput": None,  # Serverless account
        "description": "Job applications"
    },
    "recommendations": {
        "partition_key": "/user_id",
        "throughput": None,  # Serverless account
        "description": "Job recommendations"
    }
}

def setup_cosmos_db():
    """
    Create Cosmos DB database and all containers
    """
    try:
        # ============================================================
        # 1. CONNECT TO COSMOS DB
        # ============================================================
        logger.info("🔗 Connecting to Azure Cosmos DB...")
        
        if not COSMOS_ENDPOINT or not COSMOS_KEY:
            logger.error("❌ COSMOS_ENDPOINT and COSMOS_KEY are required in .env")
            return False
        
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        logger.info(f"✅ Connected to: {COSMOS_ENDPOINT}")
        
        # ============================================================
        # 2. CREATE DATABASE
        # ============================================================
        logger.info(f"\n📦 Creating database: {COSMOS_DB_NAME}...")
        
        try:
            database = client.create_database(COSMOS_DB_NAME)
            logger.info(f"✅ Database created: {COSMOS_DB_NAME}")
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(COSMOS_DB_NAME)
            logger.info(f"✅ Database already exists: {COSMOS_DB_NAME}")
        
        # ============================================================
        # 3. CREATE CONTAINERS
        # ============================================================
        logger.info("\n📋 Creating containers...\n")
        
        for container_name, config in CONTAINERS.items():
            try:
                logger.info(f"   Creating container: {container_name}")
                logger.info(f"   ├─ Partition Key: {config['partition_key']}")
                logger.info(f"   ├─ Mode: Serverless (pay-per-request)")
                logger.info(f"   └─ Purpose: {config['description']}")
                
                # Create container without throughput for serverless
                container = database.create_container(
                    id=container_name,
                    partition_key=PartitionKey(path=config['partition_key'])
                )
                logger.info(f"   ✅ Container created\n")
                
            except exceptions.CosmosResourceExistsError:
                logger.info(f"   ✅ Container already exists\n")
        
        # ============================================================
        # 4. VERIFY SETUP
        # ============================================================
        logger.info("✅ Verifying setup...\n")
        
        database_client = client.get_database_client(COSMOS_DB_NAME)
        containers = list(database_client.list_containers())
        
        logger.info(f"📊 Database Summary:")
        logger.info(f"   Database Name: {COSMOS_DB_NAME}")
        logger.info(f"   Total Containers: {len(containers)}\n")
        
        for i, container in enumerate(containers, 1):
            logger.info(f"   {i}. {container['id']}")
        
        # ============================================================
        # 5. INSERT SAMPLE DATA
        # ============================================================
        logger.info("\n📝 Inserting sample data...\n")
        
        # Sample jobs
        jobs_container = database_client.get_container_client("jobs")
        sample_jobs = [
            {
                "id": "job-001",
                "company_id": "company1",
                "title": "Senior Python Developer",
                "description": "Looking for senior Python developer with Azure experience",
                "skills": ["Python", "FastAPI", "Docker", "Azure"],
                "experience_required": 5,
                "location": "San Francisco, CA",
                "salary_min": 150000,
                "salary_max": 200000,
                "job_type": "Full-time",
                "status": "active"
            },
            {
                "id": "job-002",
                "company_id": "company2",
                "title": "Cloud Solutions Architect",
                "description": "Architect cloud solutions on Azure platform",
                "skills": ["Azure", "Cloud Architecture", "Python", "Terraform"],
                "experience_required": 8,
                "location": "New York, NY",
                "salary_min": 180000,
                "salary_max": 250000,
                "job_type": "Full-time",
                "status": "active"
            },
            {
                "id": "job-003",
                "company_id": "company3",
                "title": "AI/ML Engineer",
                "description": "Build machine learning models and AI solutions",
                "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning"],
                "experience_required": 3,
                "location": "Remote",
                "salary_min": 130000,
                "salary_max": 180000,
                "job_type": "Full-time",
                "status": "active"
            }
        ]
        
        for job in sample_jobs:
            try:
                jobs_container.create_item(body=job)
                logger.info(f"   ✅ Job inserted: {job['title']}")
            except exceptions.CosmosResourceExistsError:
                logger.info(f"   ℹ️  Job already exists: {job['title']}")
        
        # Sample users
        users_container = database_client.get_container_client("users")
        sample_users = [
            {
                "id": "user-001",
                "user_id": "user001",
                "name": "John Smith",
                "email": "john@example.com",
                "skills": ["Python", "Azure", "Docker", "FastAPI"],
                "experience": 5,
                "location": "San Francisco, CA",
                "bio": "Experienced Python developer passionate about cloud"
            },
            {
                "id": "user-002",
                "user_id": "user002",
                "name": "Sarah Johnson",
                "email": "sarah@example.com",
                "skills": ["Cloud Architecture", "Azure", "Terraform", "Python"],
                "experience": 8,
                "location": "New York, NY",
                "bio": "Cloud architect with 8 years experience"
            }
        ]
        
        logger.info("")
        for user in sample_users:
            try:
                users_container.create_item(body=user)
                logger.info(f"   ✅ User inserted: {user['name']}")
            except exceptions.CosmosResourceExistsError:
                logger.info(f"   ℹ️  User already exists: {user['name']}")
        
        # ============================================================
        # 6. SUCCESS SUMMARY
        # ============================================================
        logger.info("\n" + ("="*70))
        logger.info("✅ COSMOS DB SETUP COMPLETE!")
        logger.info(("="*70))
        logger.info(f"\n📊 Database Details:")
        logger.info(f"   Endpoint: {COSMOS_ENDPOINT}")
        logger.info(f"   Database: {COSMOS_DB_NAME}")
        logger.info(f"   Containers: {len(containers)}")
        logger.info(f"   Sample Jobs: {len(sample_jobs)}")
        logger.info(f"   Sample Users: {len(sample_users)}")
        
        logger.info(f"\n🔗 Next Steps:")
        logger.info(f"   1. Copy env.template to .env (if not done)")
        logger.info(f"   2. pip install -r requirements.txt")
        logger.info(f"   3. uvicorn backend_fastapi:app --reload")
        logger.info(f"   4. streamlit run main_with_embeddings.py")
        
        logger.info(f"\n🌐 Azure Portal:")
        logger.info(f"   https://portal.azure.com/")
        logger.info(f"   Resource: {COSMOS_DB_NAME}")
        logger.info(("="*70) + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        logger.error(f"\n🔍 Troubleshooting:")
        logger.error(f"   1. Verify COSMOS_ENDPOINT in .env")
        logger.error(f"   2. Verify COSMOS_KEY in .env")
        logger.error(f"   3. Check if Cosmos DB account exists in Azure")
        logger.error(f"   4. Verify firewall rules allow your IP")
        return False

if __name__ == "__main__":
    success = setup_cosmos_db()
    exit(0 if success else 1)


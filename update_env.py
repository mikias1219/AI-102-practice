"""
Update .env file with values from env.template
"""

import os
from dotenv import load_dotenv, set_key

# Read from env.template
env_template_path = "env.template"
env_path = ".env"

print("\n" + "="*70)
print("📝 UPDATING .env FILE FROM TEMPLATE")
print("="*70)

# Map of required env vars with their descriptions
required_vars = {
    "COSMOS_ENDPOINT": "Azure Cosmos DB endpoint",
    "COSMOS_KEY": "Azure Cosmos DB key",
    "COSMOS_DB_NAME": "Database name (job-db)",
    "COSMOS_CONNECTION_STRING": "Cosmos connection string (optional)",
    "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint",
    "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
    "AZURE_OPENAI_API_VERSION": "Azure OpenAI API version",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "Embedding model deployment",
    "DOCUMENT_INTELLIGENCE_ENDPOINT": "Document Intelligence endpoint",
    "DOCUMENT_INTELLIGENCE_API_KEY": "Document Intelligence API key",
    "OPENAI_API_KEY": "OpenAI API key (optional, for fallback)",
    "ADMIN_PASSWORD": "Admin panel password",
    "API_BASE_URL": "API backend URL",
}

# Read values from template
print("\n1️⃣  Reading from env.template...")
load_dotenv(env_template_path)

# Get values
values = {}
for key in required_vars:
    value = os.getenv(key, "")
    values[key] = value
    status = "✅" if value else "⚠️ "
    print(f"   {status} {key}")

# Update .env file
print(f"\n2️⃣  Updating {env_path}...")

try:
    # Create .env if it doesn't exist
    if not os.path.exists(env_path):
        print(f"   Creating new {env_path}")
        open(env_path, 'a').close()
    
    # Update each variable
    for key, value in values.items():
        set_key(env_path, key, value)
        print(f"   ✅ {key}")
    
    print(f"\n✅ .env file updated successfully!")
    
    # Verify
    print("\n3️⃣  Verifying...")
    load_dotenv(env_path, override=True)
    
    verified = 0
    missing = 0
    
    for key in required_vars:
        value = os.getenv(key, "")
        if value:
            print(f"   ✅ {key}: {value[:30]}..." if len(value) > 30 else f"   ✅ {key}: {value}")
            verified += 1
        else:
            print(f"   ⚠️  {key}: NOT SET")
            missing += 1
    
    print(f"\n📊 Summary: {verified} variables set, {missing} missing")
    
    if missing == 0:
        print("✅ All required variables are set!")
    else:
        print(f"⚠️  {missing} variables still need values. Update them in .env manually.")
    
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("="*70 + "\n")


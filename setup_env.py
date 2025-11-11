#!/usr/bin/env python3
"""
Setup script to create/update .env file with Azure Agent configuration
"""

import os

env_content = """# Azure Subscription & Resource Configuration
SUBSCRIPTION_ID=29f1cd2f-d0e2-413e-b913-1976b6924fa6
RESOURCE_GROUP=AI-Dev-Team
ACCOUNT_NAME=selamnewagent
PROJECT_NAME=selamnewagent

# ============================================================
# Azure Agent Configuration (Required for agent responses)
# ============================================================
# Your agent's project endpoint
AGENT_ENDPOINT=https://selamnewagent-resource.services.ai.azure.com/api/projects/selamnewagent

# Your agent's ID
AGENT_ID=asst_zPY06qUQiLjZPvbzn7MxVNPJ
"""

env_file = ".env"

# Write or overwrite the .env file
with open(env_file, 'w') as f:
    f.write(env_content)

print(f"✅ Successfully created/updated {env_file}")
print(f"\n📋 Configuration added:")
print(f"   • SUBSCRIPTION_ID: 29f1cd2f-d0e2-413e-b913-1976b6924fa6")
print(f"   • RESOURCE_GROUP: AI-Dev-Team")
print(f"   • ACCOUNT_NAME: selamnewagent")
print(f"   • PROJECT_NAME: selamnewagent")
print(f"   • AGENT_ENDPOINT: https://selamnewagent-resource.services.ai.azure.com/api/projects/selamnewagent")
print(f"   • AGENT_ID: asst_zPY06qUQiLjZPvbzn7MxVNPJ")
print(f"\n🚀 Now run: streamlit run main.py")





import os
from dotenv import load_dotenv
from openai import AzureOpenAI

## Flag to show citations
showCitations = True

# Load environment variables from shared .env file
# Use absolute path to find the shared .env file
import pathlib
# Path: .../mslearn-openai/Labfiles/02-use-own-data/Python/ownData.py
# Need to go up 4 levels to workspace root
workspace_root = pathlib.Path(__file__).absolute().parent.parent.parent.parent.parent
shared_env = workspace_root / 'mslearn-ai-services' / 'Labfiles' / '01-use-azure-ai-services' / 'Python' / '.env'

if shared_env.exists():
    load_dotenv(dotenv_path=shared_env)
    print(f"✅ Loaded .env from: {shared_env}")
else:
    # Fallback to current directory
    load_dotenv()
    print(f"⚠️  Using local .env (shared .env not found at: {shared_env})")

endpoint = os.environ.get("AZURE_OAI_ENDPOINT")
api_key = os.environ.get("AZURE_OAI_KEY")
deployment = os.environ.get("AZURE_OAI_DEPLOYMENT")

if not endpoint or not api_key or not deployment:
    print("❌ Error: Missing required environment variables!")
    print(f"   AZURE_OAI_ENDPOINT: {'✅' if endpoint else '❌'}")
    print(f"   AZURE_OAI_KEY: {'✅' if api_key else '❌'}")
    print(f"   AZURE_OAI_DEPLOYMENT: {'✅' if deployment else '❌'}")
    exit(1)

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-15-preview",
)

# Configure your data source
text = input('\nEnter a question:\n')

completion = client.chat.completions.create(
    model=deployment,
    messages=[
        {
            "role": "user",
            "content": text,
        },
    ],
    extra_body={
        "data_sources":[
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": os.environ["AZURE_SEARCH_ENDPOINT"],
                    "index_name": os.environ["AZURE_SEARCH_INDEX"],
                    "authentication": {
                        "type": "api_key",
                        "key": os.environ["AZURE_SEARCH_KEY"],
                    },
                    "query_type": "simple",
                    "top_n_documents": 5,
                    "in_scope": True,
                    "strictness": 3,
                    "role_information": "You are an AI assistant that helps people find information about travel destinations."
                }
            }
        ],
    }
)

print("\n" + "="*60)
print("RESPONSE:")
print("="*60)
print(completion.choices[0].message.content)
print("="*60)

if showCitations:
    print(f"\nCitations:\n{completion.choices[0].message.context}")

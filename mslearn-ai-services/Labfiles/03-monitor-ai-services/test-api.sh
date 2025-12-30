#!/bin/bash
# Test script to generate API calls for monitoring metrics

# Load environment variables from shared .env file
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Try multiple possible paths
SHARED_ENV1="$SCRIPT_DIR/../../../01-use-azure-ai-services/Python/.env"
SHARED_ENV2="$SCRIPT_DIR/../../01-use-azure-ai-services/Python/.env"
SHARED_ENV3="$(cd "$SCRIPT_DIR/../../.." && pwd)/mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env"

if [ -f "$SHARED_ENV1" ]; then
    SHARED_ENV="$SHARED_ENV1"
elif [ -f "$SHARED_ENV2" ]; then
    SHARED_ENV="$SHARED_ENV2"
elif [ -f "$SHARED_ENV3" ]; then
    SHARED_ENV="$SHARED_ENV3"
else
    echo "Error: .env file not found"
    echo "Tried: $SHARED_ENV1"
    echo "Tried: $SHARED_ENV2"
    echo "Tried: $SHARED_ENV3"
    echo "Please ensure Lab 1 is set up with the shared .env file"
    exit 1
fi

# Source the .env file
export $(grep -v '^#' "$SHARED_ENV" | grep -v '^$' | xargs)

# Check if required variables are set
if [ -z "$AI_SERVICE_ENDPOINT" ] || [ -z "$AI_SERVICE_KEY" ]; then
    echo "Error: AI_SERVICE_ENDPOINT or AI_SERVICE_KEY not found in .env file"
    exit 1
fi

ENDPOINT="${AI_SERVICE_ENDPOINT%/}"  # Remove trailing slash if present
KEY="$AI_SERVICE_KEY"

echo "Testing Azure AI Services API..."
echo "Endpoint: $ENDPOINT"
echo ""

# Make API call
RESPONSE=$(curl -s -X POST "$ENDPOINT/language/:analyze-text?api-version=2023-04-01" \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  --data-ascii "{'analysisInput':{'documents':[{'id':1,'text':'hello'}]}, 'kind': 'LanguageDetection'}")

# Check if request was successful
if echo "$RESPONSE" | grep -q "detectedLanguage"; then
    echo "✅ API call successful!"
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "This call will be reflected in your metrics within 2-5 minutes."
else
    echo "❌ API call failed!"
    echo "Response: $RESPONSE"
    exit 1
fi


#!/bin/bash
# Deploy Azure AI Services Sentiment Analysis Container to Azure Container Instances

# Load environment variables from shared .env file
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
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

ENDPOINT="${AI_SERVICE_ENDPOINT%/}"  # Remove trailing slash
KEY="$AI_SERVICE_KEY"
RG="AI-102"
TIMESTAMP=$(date +%s | tail -c 5)
CONTAINER_NAME="ai-102-sentiment-$TIMESTAMP"
DNS_LABEL="ai102sentiment$TIMESTAMP"

echo "🚀 Deploying Azure AI Services Container..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Container Name: $CONTAINER_NAME"
echo "Resource Group: $RG"
echo "DNS Label: $DNS_LABEL"
echo "Image: mcr.microsoft.com/azure-cognitive-services/textanalytics/sentiment:latest"
echo ""
echo "This will take 5-10 minutes..."
echo ""

# Deploy the container
az container create \
  --resource-group "$RG" \
  --name "$CONTAINER_NAME" \
  --image mcr.microsoft.com/azure-cognitive-services/textanalytics/sentiment:latest \
  --ports 5000 \
  --dns-name-label "$DNS_LABEL" \
  --environment-variables Eula=accept \
  --secure-environment-variables ApiKey="$KEY" Billing="$ENDPOINT" \
  --cpu 1 --memory 8 \
  --os-type Linux \
  --query "{Status:instanceView.state, IP:ipAddress.ip, FQDN:ipAddress.fqdn}" \
  -o json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Container deployment initiated!"
    echo ""
    echo "📋 Next Steps:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. Wait 5-10 minutes for the container to be ready"
    echo "2. Check status with:"
    echo "   az container show --resource-group $RG --name $CONTAINER_NAME --query instanceView.state -o tsv"
    echo ""
    echo "3. Get IP/FQDN with:"
    echo "   az container show --resource-group $RG --name $CONTAINER_NAME --query '{IP:ipAddress.ip, FQDN:ipAddress.fqdn}' -o json"
    echo ""
    echo "4. Test the container:"
    echo "   ./test-container.sh <IP_OR_FQDN>"
    echo ""
    echo "Container Name: $CONTAINER_NAME"
else
    echo "❌ Container deployment failed!"
    exit 1
fi


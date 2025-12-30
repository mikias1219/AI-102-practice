#!/bin/bash
# Test script for containerized sentiment analysis

if [ -z "$1" ]; then
    echo "Usage: $0 <CONTAINER_IP_OR_FQDN>"
    echo ""
    echo "Example:"
    echo "  $0 20.123.45.67"
    echo "  $0 ai102sentiment12345.eastus.azurecontainer.io"
    echo ""
    echo "To get your container IP/FQDN:"
    echo "  az container show --resource-group AI-102 --name <container-name> --query '{IP:ipAddress.ip, FQDN:ipAddress.fqdn}' -o json"
    exit 1
fi

CONTAINER_ENDPOINT="$1"
PORT="5000"

echo "🧪 Testing Containerized Sentiment Analysis..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Container: http://$CONTAINER_ENDPOINT:$PORT"
echo ""

# Test with v3.1 endpoint
echo "Testing v3.1 endpoint..."
RESPONSE=$(curl -s -X POST "http://$CONTAINER_ENDPOINT:$PORT/text/analytics/v3.1/sentiment" \
  -H "Content-Type: application/json" \
  --data-ascii "{'documents':[{'id':1,'text':'The performance was amazing! The sound could have been clearer.'},{'id':2,'text':'The food and service were unacceptable. While the host was nice, the waiter was rude and food was cold.'}]}")

if echo "$RESPONSE" | grep -q "sentiment"; then
    echo "✅ v3.1 endpoint working!"
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo "⚠️  v3.1 endpoint failed, trying v3.0..."
    echo "Error: $RESPONSE"
    echo ""
    
    # Try v3.0 endpoint
    echo "Testing v3.0 endpoint..."
    RESPONSE=$(curl -s -X POST "http://$CONTAINER_ENDPOINT:$PORT/text/analytics/v3.0/sentiment?model-version=latest" \
      -H "Content-Type: application/json" \
      -d '{
        "documents": [
          {
            "id": "1-en",
            "language": "en",
            "text": "The performance was amazing! The sound could have been clearer."
          },
          {
            "id": "2-en",
            "language": "en",
            "text": "The food and service were unacceptable. While the host was nice, the waiter was rude and food was cold."
          }
        ]
      }')
    
    if echo "$RESPONSE" | grep -q "sentiment"; then
        echo "✅ v3.0 endpoint working!"
        echo "Response:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    else
        echo "❌ Both endpoints failed!"
        echo "Response: $RESPONSE"
        echo ""
        echo "Troubleshooting:"
        echo "1. Check container status:"
        echo "   az container show --resource-group AI-102 --name <container-name> --query instanceView.state -o tsv"
        echo ""
        echo "2. Check container logs:"
        echo "   az container logs --resource-group AI-102 --name <container-name>"
        echo ""
        echo "3. Check /status endpoint:"
        echo "   curl http://$CONTAINER_ENDPOINT:$PORT/status"
        exit 1
    fi
fi

echo ""
echo "✅ Container test successful!"


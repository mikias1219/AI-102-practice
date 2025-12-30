#!/bin/bash
# Check container status and get connection details

if [ -z "$1" ]; then
    echo "Usage: $0 <container-name>"
    echo ""
    echo "To list all containers:"
    echo "  az container list --resource-group AI-102 --query '[].{Name:name, Status:instanceView.state}' -o table"
    exit 1
fi

CONTAINER_NAME="$1"
RG="AI-102"

echo "📊 Container Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

az container show \
  --resource-group "$RG" \
  --name "$CONTAINER_NAME" \
  --query "{Status:instanceView.state, IP:ipAddress.ip, FQDN:ipAddress.fqdn, Ports:containers[0].ports}" \
  -o json

echo ""
echo "📋 Connection Details:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

IP=$(az container show --resource-group "$RG" --name "$CONTAINER_NAME" --query ipAddress.ip -o tsv)
FQDN=$(az container show --resource-group "$RG" --name "$CONTAINER_NAME" --query ipAddress.fqdn -o tsv)

if [ -n "$IP" ]; then
    echo "IP Address: $IP"
    echo "FQDN: $FQDN"
    echo ""
    echo "Test with:"
    echo "  ./test-container.sh $IP"
    echo "  or"
    echo "  ./test-container.sh $FQDN"
else
    echo "⚠️  Container IP not available yet. Wait a few minutes and try again."
fi

echo ""
echo "📜 View Logs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  az container logs --resource-group $RG --name $CONTAINER_NAME --follow"


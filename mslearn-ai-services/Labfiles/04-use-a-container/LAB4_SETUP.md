# Lab 4: Use Containers - Setup Guide

## 🎯 Lab Objectives
- Deploy Azure AI Services in containers
- Use Azure Container Instances (ACI)
- Understand containerized AI services
- Test containerized sentiment analysis

---

## 📋 Prerequisites

1. ✅ Completed Lab 1 (Azure AI Services resource created)
2. ✅ Azure subscription with permissions to create Container Instances
3. ✅ Azure CLI installed and configured

---

## 🐳 Step 1: Deploy Container Using Azure CLI

### Quick Deployment Command

```bash
# Get your credentials from .env or Azure
ENDPOINT="https://ai-102-practice-111.cognitiveservices.azure.com/"
KEY="<your-key>"
RG="AI-102"
CONTAINER_NAME="ai-102-sentiment-$(date +%s | tail -c 5)"

# Deploy the container
az container create \
  --resource-group $RG \
  --name $CONTAINER_NAME \
  --image mcr.microsoft.com/azure-cognitive-services/textanalytics/sentiment:latest \
  --ports 5000 \
  --dns-name-label ai102sentiment$(date +%s | tail -c 5) \
  --environment-variables Eula=accept \
  --secure-environment-variables ApiKey=$KEY Billing=$ENDPOINT \
  --cpu 1 --memory 8 \
  --os-type Linux
```

### Or Use the Automated Script

```bash
cd mslearn-ai-services/Labfiles/04-use-a-container
./deploy-container.sh
```

---

## 🔧 Step 2: Deploy Container Using Azure Portal

### In Azure Portal:

1. **Create Container Instance**
   - Go to Azure Portal → Create a resource
   - Search for "Container Instances"
   - Click **Create**

2. **Configure Basics**
   - **Subscription**: Your subscription
   - **Resource group**: AI-102 (same as your AI Services resource)
   - **Container name**: `ai-102-sentiment-<unique-id>`
   - **Region**: Choose any available region
   - **Image source**: Other Registry
   - **Image type**: Public
   - **Image**: `mcr.microsoft.com/azure-cognitive-services/textanalytics/sentiment:latest`
   - **OS type**: Linux
   - **Size**: 1 vcpu, 8 GB memory

3. **Configure Networking**
   - **Networking type**: Public
   - **DNS name label**: `ai102sentiment-<unique-id>` (must be globally unique)
   - **Ports**: Change TCP port from 80 to **5000**

4. **Configure Advanced Settings**
   - **Restart policy**: On failure
   - **Environment variables**:
     - `ApiKey`: Your Azure AI Services Key 1 (mark as secure)
     - `Billing`: Your Azure AI Services endpoint (mark as secure)
     - `Eula`: `accept` (not secure)
   - **Key management**: Microsoft-managed keys (MMK)

5. **Create**
   - Click **Review + create** → **Create**
   - Wait 5-10 minutes for deployment

---

## ⏱️ Step 3: Wait for Container to be Ready

After deployment, check the container status:

```bash
# Check container status
az container show \
  --resource-group AI-102 \
  --name <your-container-name> \
  --query "{Status:instanceView.state, IP:ipAddress.ip, FQDN:ipAddress.fqdn}" \
  -o json
```

**Important**: Wait until Status is "Running" before testing.

---

## 🧪 Step 4: Test the Container

### Get Container IP or FQDN

```bash
# Get container details
az container show \
  --resource-group AI-102 \
  --name <your-container-name> \
  --query "{IP:ipAddress.ip, FQDN:ipAddress.fqdn}" \
  -o json
```

### Test with curl

```bash
# Replace <CONTAINER_IP_OR_FQDN> with your container's IP or FQDN
curl -X POST "http://<CONTAINER_IP_OR_FQDN>:5000/text/analytics/v3.1/sentiment" \
  -H "Content-Type: application/json" \
  --data-ascii "{'documents':[{'id':1,'text':'The performance was amazing! The sound could have been clearer.'},{'id':2,'text':'The food and service were unacceptable. While the host was nice, the waiter was rude and food was cold.'}]}"
```

### Or Use the Test Script

```bash
cd mslearn-ai-services/Labfiles/04-use-a-container
./test-container.sh <CONTAINER_IP_OR_FQDN>
```

---

## 🐳 Step 5: Deploy Locally with Docker (Optional)

If you have Docker installed locally, you can run the container on your machine:

```bash
docker run --rm -it -p 5000:5000 \
  --memory 8g --cpus 1 \
  mcr.microsoft.com/azure-cognitive-services/textanalytics/sentiment:latest \
  Eula=accept \
  Billing=<your-endpoint> \
  ApiKey=<your-key>
```

Then test with:
```bash
curl -X POST "http://localhost:5000/text/analytics/v3.1/sentiment" \
  -H "Content-Type: application/json" \
  --data-ascii "{'documents':[{'id':1,'text':'Hello world!'}]}"
```

---

## ✅ What This Lab Demonstrates

1. **Container Deployment**: How to deploy AI services in containers
2. **Data Privacy**: Containerized services don't send data to Azure (only billing info)
3. **Flexibility**: Deploy containers in ACI, AKS, or local Docker
4. **Control**: More control over infrastructure and deployment

---

## 🔍 Troubleshooting

### Container Status Shows "Running" but Requests Fail

**Symptoms:**
- `curl: (52) Empty reply from server`
- `curl: (56) Recv failure: Connection reset by peer`

**Solutions:**
1. Wait 5-10 minutes after deployment (containers need time to initialize)
2. Check container logs:
   ```bash
   az container logs \
     --resource-group AI-102 \
     --name <your-container-name>
   ```
3. Look for: "Model loaded from /input/TextAnalytics/v3.x/Sentiment"
4. Try v3.0 endpoint instead of v3.1:
   ```bash
   curl -X POST "http://<CONTAINER_IP>:5000/text/analytics/v3.0/sentiment?model-version=latest" \
     -H "Content-Type: application/json" \
     -d '{"documents":[{"id":"1","text":"Hello world!"}]}'
   ```

### Check Container Status Endpoint

```bash
curl http://<CONTAINER_IP>:5000/status
```

### View Container Logs

```bash
az container logs \
  --resource-group AI-102 \
  --name <your-container-name> \
  --follow
```

---

## 📚 Additional Resources

- [Azure AI Services Containers](https://learn.microsoft.com/azure/ai-services/cognitive-services-container-support)
- [Azure Container Instances](https://learn.microsoft.com/azure/container-instances/)
- [Container Images](https://learn.microsoft.com/azure/ai-services/cognitive-services-container-support#container-images)

---

## 🧹 Clean Up

After completing the lab:

```bash
# Delete the container instance
az container delete \
  --resource-group AI-102 \
  --name <your-container-name> \
  --yes
```

**Note**: Keep your Azure AI Services resource for the next labs!

---

**Next**: Lab 5 - Implement Content Safety


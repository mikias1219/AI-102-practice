# Lab 3: Monitor AI Services - Setup Guide

## 🎯 Lab Objectives
- Configure alerts for Azure AI Services
- Monitor metrics and usage
- Set up activity log monitoring
- Visualize service utilization

---

## 📋 Prerequisites

1. ✅ Completed Lab 1 (Azure AI Services resource created)
2. ✅ Azure subscription with monitoring permissions
3. ✅ Access to Azure Portal

---

## 🔧 Step 1: Configure an Alert

### In Azure Portal:

1. **Navigate to Your AI Services Resource**
   - Go to Azure Portal → Your Azure AI Services resource (`ai-102-practice-111`)
   - In the left menu, go to **Monitoring** → **Alerts**

2. **Create Alert Rule**
   - Click **+ Create** → **Alert rule**
   - **Scope**: Verify your AI Services resource is selected

3. **Configure Condition**
   - Click **Condition** tab
   - Click **See all signals**
   - In **Signal type**, scroll to **Activity Log** section
   - Select **List Keys (Cognitive Services API Account)**
   - Click **Apply**
   - Review activity over past 6 hours

4. **Configure Actions** (Optional)
   - Click **Actions** tab
   - You can create an action group for email notifications
   - For this lab, we'll skip this step

5. **Set Alert Details**
   - Click **Details** tab
   - **Alert rule name**: `Key List Alert`
   - Click **Review + create** → **Create**

---

## 🧪 Step 2: Test the Alert

### Using Azure CLI:

1. **List Keys to Trigger Alert**
   ```bash
   az cognitiveservices account keys list \
     --name ai-102-practice-111 \
     --resource-group AI-102
   ```

2. **Check Alert**
   - Go back to Azure Portal → Your AI Services resource → **Alerts**
   - Refresh the page (may take up to 5 minutes)
   - You should see a **Sev 4** alert listed
   - Click the alert to see details

---

## 📊 Step 3: Visualize Metrics

### In Azure Portal:

1. **Open Metrics**
   - Go to your Azure AI Services resource
   - Navigate to **Monitoring** → **Metrics**

2. **Create Chart**
   - Click **+ New chart** (if no chart exists)
   - **Metric**: Select **Total Calls**
   - **Aggregation**: Select **Count**
   - This shows total API calls over time

3. **Generate Test Requests**

   **Using curl (Linux/Mac/Git Bash):**
   ```bash
   curl -X POST "https://ai-102-practice-111.cognitiveservices.azure.com/language/:analyze-text?api-version=2023-04-01" \
     -H "Content-Type: application/json" \
     -H "Ocp-Apim-Subscription-Key: <your-key>" \
     --data-ascii "{'analysisInput':{'documents':[{'id':1,'text':'hello'}]}, 'kind': 'LanguageDetection'}"
   ```

   **Or use the provided script:**
   ```bash
   cd mslearn-ai-services/Labfiles/03-monitor-ai-services
   ./rest-test.sh
   ```

4. **Run Multiple Requests**
   - Run the curl command 5-10 times
   - Use the **^** key to cycle through previous commands
   - Each request increments the call count

5. **View Updated Metrics**
   - Return to **Metrics** page in Azure Portal
   - Refresh the chart
   - Wait a few minutes for metrics to update
   - You should see the call count increase

---

## 🔍 Step 4: Additional Monitoring Options

### Diagnostic Logging (Optional - Advanced)

Diagnostic logging captures detailed information about resource usage. It can take over an hour to generate data, so it's not covered in this lab.

**To enable diagnostic logging:**
1. Go to your AI Services resource → **Monitoring** → **Diagnostic settings**
2. Click **+ Add diagnostic setting**
3. Configure logs and metrics to send to:
   - Log Analytics workspace
   - Storage account
   - Event Hub
   - Partner solution

**Learn more**: [Azure AI Services Diagnostic Logging](https://docs.microsoft.com/azure/ai-services/diagnostic-logging)

---

## 📝 Quick Reference Commands

### List Keys (Triggers Alert)
```bash
az cognitiveservices account keys list \
  --name ai-102-practice-111 \
  --resource-group AI-102
```

### Test API Call (Increments Metrics)
```bash
curl -X POST "https://ai-102-practice-111.cognitiveservices.azure.com/language/:analyze-text?api-version=2023-04-01" \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: <your-key>" \
  --data-ascii "{'analysisInput':{'documents':[{'id':1,'text':'hello'}]}, 'kind': 'LanguageDetection'}"
```

### Get Your Key
```bash
az cognitiveservices account keys list \
  --name ai-102-practice-111 \
  --resource-group AI-102 \
  --query "key1" -o tsv
```

---

## ✅ What This Lab Demonstrates

1. **Alert Configuration**: How to set up alerts for specific activities
2. **Activity Monitoring**: Track important operations (like key listing)
3. **Metrics Visualization**: Monitor service usage and performance
4. **Best Practices**: 
   - Set up alerts for security-sensitive operations
   - Monitor usage to understand service utilization
   - Use metrics to track performance and costs

---

## 🔍 Troubleshooting

### Alert Not Appearing
- Wait up to 5 minutes for alert to appear
- Verify the alert rule was created successfully
- Check that you actually triggered the condition (listed keys)

### Metrics Not Updating
- Metrics can take 2-5 minutes to appear
- Make sure you're making actual API calls
- Verify the endpoint and key are correct
- Check that the service is working (test with curl first)

### curl Command Fails
- Verify endpoint URL is correct
- Check that the API key is valid
- Ensure you're using the correct API version
- Try with `--verbose` flag to see detailed error

---

## 📚 Additional Resources

- [Azure AI Services Monitoring](https://docs.microsoft.com/azure/ai-services/monitor-usage)
- [Azure Monitor Alerts](https://docs.microsoft.com/azure/azure-monitor/alerts/alerts-overview)
- [Azure Metrics](https://docs.microsoft.com/azure/azure-monitor/essentials/data-platform-metrics)

---

## 🧹 Clean Up (Optional)

After completing the lab, you can:
- Delete the alert rule (if not needed)
- Keep the resource for next labs

**Note**: Keep your Azure AI Services resource for the next labs!

---

**Next**: Lab 4 - Use Containers


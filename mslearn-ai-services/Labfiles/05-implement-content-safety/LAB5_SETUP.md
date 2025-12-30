# Lab 5: Implement Content Safety - Setup Guide

## 🎯 Lab Objectives
- Provision Azure AI Content Safety resource
- Implement content moderation for text and images
- Use Prompt Shields to detect attacks
- Configure responsible AI features

---

## 📋 Prerequisites

1. ✅ Completed Lab 1 (Azure AI Services resource created)
2. ✅ Azure subscription with permissions
3. ✅ Access to Azure Portal and Azure AI Foundry

---

## 🔧 Step 1: Provision Content Safety Resource

### Using Azure CLI (Automated):

The resource has been created automatically:
- **Name**: `ai-102-content-safety`
- **Resource Group**: `AI-102`
- **Location**: East US
- **Pricing Tier**: F0 (Free)

### Using Azure Portal (Manual):

1. **Create Content Safety Resource**
   - Go to Azure Portal → Create a resource
   - Search for "Azure AI Content Safety"
   - Click **Create**

2. **Configure Settings**
   - **Subscription**: Your subscription
   - **Resource group**: AI-102
   - **Region**: East US
   - **Name**: `ai-102-content-safety` (or unique name)
   - **Pricing tier**: F0 (Free) or S (Standard)

3. **Configure Access**
   - Go to **Access Control (IAM)**
   - Click **+ Add** → **Add role assignment**
   - Select **Cognitive Services User** role
   - Add your account
   - Click **Review + assign**

4. **Get Keys and Endpoint**
   - Go to **Keys and Endpoint**
   - Copy **Endpoint** and **Key 1**

---

## ⚙️ Step 2: Configure Environment Variables

The Content Safety credentials have been automatically added to your shared `.env` file:

**Location**: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env`

The file now includes:
```env
CONTENT_SAFETY_ENDPOINT=https://ai-102-content-safety.cognitiveservices.azure.com/
CONTENT_SAFETY_KEY=<your-key>
```

---

## 🧪 Step 3: Test in Azure AI Foundry

### Access Azure AI Foundry:

1. **Open Azure AI Foundry**
   - Go to https://ai.azure.com/explore/contentsafety
   - Sign in with your Azure account

2. **Test Text Moderation**
   - Under **Moderate text content**, click **Try it out**
   - Select your Content Safety resource
   - Try **Multiple risk categories in one sentence**
   - Click **Run test** and review results

3. **Test Protected Material Detection**
   - Select **Protected material detection for text**
   - Try **Protected lyrics** sample
   - Click **Run test**

4. **Test Image Moderation**
   - Select **Moderate image content**
   - Try **Self-harm content** sample
   - Click **Run test**

5. **Test Prompt Shields** ⭐ (Main Focus)
   - Select **Prompt shields**
   - Under **Azure AI Services**, select your Content Safety resource
   - Select **Prompt & document attack content**
   - Review the user prompt and document
   - Click **Run test**
   - Verify that **Jailbreak attacks** were detected

6. **Get Sample Code**
   - Under **Next steps**, click **View code**
   - Select Python or C#
   - Copy the sample code

---

## 🚀 Step 4: Run the Application

### Option 1: Using the Python Script

```bash
cd "/home/mikias/Mikias/AI_Data_Engineering/Certifications/practice test/AI-102-AIEngineer/mslearn-ai-services/Labfiles/05-implement-content-safety/Python"
source ../../01-use-azure-ai-services/Python/venv/bin/activate
python prompt-shield.py
```

### Option 2: Using the Run Script

```bash
cd "/home/mikias/Mikias/AI_Data_Engineering/Certifications/practice test/AI-102-AIEngineer/mslearn-ai-services/Labfiles/05-implement-content-safety/Python"
./run.sh
```

---

## 📝 Code Overview

The `prompt-shield.py` script:
- Loads credentials from shared `.env` file
- Tests user prompt for harmful content
- Tests document content for inappropriate material
- Uses Azure AI Content Safety Text Analysis API
- Displays content moderation results

**Note**: Prompt Shields (jailbreak detection) is available through Azure AI Foundry. The script demonstrates standard content moderation. For Prompt Shields, use Azure AI Foundry to get the latest API code.

---

## ✅ What This Lab Demonstrates

1. **Content Safety**: Protect applications from harmful content
2. **Prompt Shields**: Detect jailbreak and prompt injection attacks
3. **Text Moderation**: Identify inappropriate text content
4. **Image Moderation**: Detect inappropriate images
5. **Responsible AI**: Implement safety measures in AI applications

---

## 🔍 Troubleshooting

### Error: "CONTENT_SAFETY_ENDPOINT not found"
- Verify the `.env` file has the Content Safety credentials
- Check the file location: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env`

### Error: "401 Unauthorized"
- Verify the Content Safety key is correct
- Check that your account has "Cognitive Services User" role

### Error: "404 Not Found" or "Invalid API version"
- The API version might have changed
- Check Azure documentation for latest API version
- Current version in code: `2024-09-01-preview`

### API Endpoint Issues
- Content Safety uses a different endpoint format
- Endpoint should be: `https://<resource-name>.cognitiveservices.azure.com/`
- Not the same as regular AI Services endpoint

---

## 📚 Additional Resources

- [Azure AI Content Safety Documentation](https://learn.microsoft.com/azure/ai-services/content-safety/)
- [Prompt Shields Overview](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-prompt-shields)
- [Content Safety API Reference](https://learn.microsoft.com/rest/api/contentsafety/)
- [Responsible AI](https://learn.microsoft.com/azure/ai-services/responsible-ai)

---

## 🧹 Clean Up (Optional)

After completing the lab:

```bash
# Delete Content Safety resource
az cognitiveservices account delete \
  --name ai-102-content-safety \
  --resource-group AI-102 \
  --yes
```

**Note**: Keep your Azure AI Services resource for other labs!

---

**Next**: Day 2 - Generative AI Solutions


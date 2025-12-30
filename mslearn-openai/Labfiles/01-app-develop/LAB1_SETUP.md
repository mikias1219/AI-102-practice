# Day 2 - Lab 1: Azure OpenAI App Development
## Setup Guide

## 🎯 Lab Objectives
- Provision Azure OpenAI resource
- Deploy GPT-4o model
- Integrate Azure OpenAI into application
- Apply prompt engineering techniques
- Use grounding context and chat history

---

## 📋 Prerequisites

1. ✅ Azure subscription with Azure OpenAI access
2. ✅ Completed Day 1 labs (shared environment setup)
3. ✅ Python 3.x installed

---

## 🔧 Step 1: Azure OpenAI Resource

### ✅ Already Created:
- **Resource Name**: `ai-102-openai`
- **Resource Group**: `AI-102`
- **Location**: East US
- **Pricing Tier**: Standard S0
- **Deployment**: `gpt-4o` (GPT-4o model)

### Manual Creation (if needed):

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name ai-102-openai \
  --resource-group AI-102 \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Deploy GPT-4o model
az cognitiveservices account deployment create \
  --resource-group AI-102 \
  --name ai-102-openai \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version 2024-05-13 \
  --model-format OpenAI \
  --sku-name "Standard" \
  --sku-capacity 5
```

---

## ⚙️ Step 2: Environment Configuration

### ✅ Already Configured:
The Azure OpenAI credentials have been added to your shared `.env` file:

**Location**: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env`

```env
# Azure OpenAI Configuration (for Day 2: Lab 1)
AZURE_OAI_ENDPOINT=https://eastus.api.cognitive.microsoft.com/
AZURE_OAI_KEY=<your-key>
AZURE_OAI_DEPLOYMENT=gpt-4o
```

### Dependencies:
- ✅ `openai==1.65.2` installed in shared venv
- ✅ `python-dotenv` already installed

---

## 🚀 Step 3: Run the Application

### Option 1: Using the Run Script

```bash
cd mslearn-openai/Labfiles/01-app-develop/Python
./run.sh
```

### Option 2: Manual Execution

```bash
cd mslearn-openai/Labfiles/01-app-develop/Python
source ../../../../mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/venv/bin/activate
python application.py
```

---

## 📝 Application Features

### 1. **Prompt Engineering Examples**

The application demonstrates different prompt engineering techniques:

**Example 1: Basic Prompt**
- System: "You are an AI assistant"
- User: "Write an intro for a new wildlife Rescue"

**Example 2: Structured Prompt**
- System: "You are an AI assistant helping to write emails"
- User: "Write a promotional email for a new wildlife rescue, including the following: ..."

**Example 3: Tone Specification**
- System: "You are an AI assistant that helps write promotional emails... Your tone is light, chit-chat oriented..."
- User: "Write a promotional email..."

### 2. **Grounding Context**

The application uses `grounding.txt` to provide context:
- Initializes chat history with grounding text
- Maintains conversation context across messages
- Demonstrates RAG-like behavior

### 3. **Chat History**

- Maintains conversation history
- Supports follow-up questions
- Uses previous context to answer questions

---

## 🧪 Testing the Application

### Test 1: Basic Prompt
1. Edit `system.txt`: `You are an AI assistant`
2. Run the app
3. Enter: `Write an intro for a new wildlife Rescue`
4. Observe the generic response

### Test 2: Structured Email
1. Edit `system.txt`: `You are an AI assistant helping to write emails`
2. Enter: `Write a promotional email for a new wildlife rescue, including the following: - Rescue name is Contoso - It specializes in elephants - Call for donations to be given at our website`
3. Observe the formatted email response

### Test 3: Grounding Context
1. The app automatically loads `grounding.txt`
2. System: `You're an AI assistant who helps people find information. You'll provide answers from the text provided in the prompt, and respond concisely.`
3. User: `What animal is the favorite of children at Contoso?`
4. User (follow-up): `How can they interact with it at Contoso?`
5. Observe how the model uses grounding context and chat history

---

## 📚 Key Concepts

### Prompt Engineering
- **System Messages**: Define the AI's role and behavior
- **User Messages**: Provide specific instructions
- **Structured Prompts**: Include format requirements
- **Tone Specification**: Control response style

### Grounding Context
- Provides background information
- Initializes chat history
- Enables context-aware responses

### Chat History
- Maintains conversation state
- Supports follow-up questions
- Enables multi-turn conversations

### Azure OpenAI Parameters
- **temperature**: Controls randomness (0.0-1.0)
- **max_tokens**: Limits response length
- **model**: Specifies which model to use

---

## 🔍 Troubleshooting

### Error: "AZURE_OAI_ENDPOINT not found"
- Verify the `.env` file has Azure OpenAI credentials
- Check file location: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env`

### Error: "401 Unauthorized"
- Verify the Azure OpenAI key is correct
- Check that the resource is provisioned and active

### Error: "Deployment not found"
- Verify the deployment name is `gpt-4o`
- Check that the model is deployed in Azure Portal

### Error: "Rate limit exceeded"
- The deployment has a capacity of 5 (5,000 tokens/minute)
- Wait a moment and try again

---

## 📚 Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Prompt Engineering Guide](https://learn.microsoft.com/azure/ai-services/openai/concepts/prompt-engineering)
- [Azure OpenAI SDK](https://github.com/openai/openai-python)
- [Microsoft Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)

---

## ✅ Completion Checklist

- [x] Azure OpenAI resource created
- [x] GPT-4o model deployed
- [x] Environment configured
- [x] Application code updated
- [x] Dependencies installed
- [x] Run script created
- [ ] Test basic prompts
- [ ] Test structured prompts
- [ ] Test grounding context
- [ ] Test chat history

---

**Next**: Lab 2 - RAG with Own Data


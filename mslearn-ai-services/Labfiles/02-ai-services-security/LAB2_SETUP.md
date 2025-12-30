# Lab 2: AI Services Security - Setup Guide

## 🎯 Lab Objectives
- Manage authentication keys for Azure AI Services
- Secure keys using Azure Key Vault
- Use service principals for secure access
- Implement best practices for key management

---

## 📋 Prerequisites

1. ✅ Completed Lab 1 (Azure AI Services resource created)
2. ✅ Azure subscription with permissions to create:
   - Azure Key Vault
   - Service Principal (App Registration)

---

## 🔧 Step 1: Manage Authentication Keys

### Get Your Keys

**Option A: Azure Portal**
1. Go to your Azure AI Services resource
2. Navigate to **Keys and Endpoint**
3. Copy **Key 1** and **Endpoint**

**Option B: Azure CLI**
```bash
az cognitiveservices account keys list \
  --name ai-102-practice-111 \
  --resource-group <your-resource-group>
```

### Test with curl
```bash
curl -X POST "https://ai-102-practice-111.cognitiveservices.azure.com/language/:analyze-text?api-version=2023-04-01" \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: <your-key>" \
  --data-ascii "{'analysisInput':{'documents':[{'id':1,'text':'hello'}]}, 'kind': 'LanguageDetection'}"
```

### Regenerate a Key (if needed)
```bash
az cognitiveservices account keys regenerate \
  --name ai-102-practice-111 \
  --resource-group <your-resource-group> \
  --key-name key1
```

---

## 🔐 Step 2: Create Azure Key Vault

### In Azure Portal:

1. **Create Key Vault**
   - Go to Azure Portal → Create a resource
   - Search for "Key Vault"
   - Click **Create**

2. **Configure Basics**
   - **Subscription**: Your subscription
   - **Resource group**: Same as your AI Services resource
   - **Key vault name**: `ai-102-keyvault-<your-initials>` (must be globally unique)
   - **Region**: Same as your AI Services resource
   - **Pricing tier**: Standard

3. **Configure Access**
   - **Permission model**: Vault access policy
   - **Access policies**: Select your user account
   - Click **Review + create** → **Create**

4. **Add Secret**
   - Go to your Key Vault → **Secrets**
   - Click **+ Generate/Import**
   - **Upload options**: Manual
   - **Name**: `AI-Services-Key` ⚠️ **Must match exactly!**
   - **Secret value**: Your Azure AI Services **Key 1**
   - Click **Create**

---

## 👤 Step 3: Create Service Principal

### Using Azure CLI:

1. **Create Service Principal**
   ```bash
   az ad sp create-for-rbac -n "api://ai-102-app-<your-initials>"
   ```
   
   **Save the output!** You'll need:
   - `appId`
   - `password` (can't be retrieved later!)
   - `tenant`

2. **Get Object ID**
   ```bash
   az ad sp show --id <appId>
   ```
   Copy the `id` value from the output.

3. **Grant Key Vault Access**
   ```bash
   az keyvault set-policy \
     -n <your-key-vault-name> \
     --object-id <objectId> \
     --secret-permissions get list
   ```

---

## ⚙️ Step 4: Configure Environment Variables

Update the shared `.env` file at:
`mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env`

Add these values (you already have the first two from Lab 1):

```env
# Azure AI Services (from Lab 1)
AI_SERVICE_ENDPOINT=https://ai-102-practice-111.cognitiveservices.azure.com/
AI_SERVICE_KEY=<your-ai-service-key>

# Azure Key Vault Configuration (Lab 2)
KEY_VAULT=ai-102-keyvault-<your-initials>
TENANT_ID=<your-tenant-id>
APP_ID=<your-app-id>
APP_PASSWORD=<your-app-password>
```

**Example:**
```env
KEY_VAULT=ai-102-keyvault-mikias
TENANT_ID=1234abcd-5678-efgh-ijkl-1234567890ab
APP_ID=abcd1234-5678-efgh-ijkl-1234567890ab
APP_PASSWORD=1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6
```

---

## 🚀 Step 5: Run the Application

### Option 1: Using the run script
```bash
cd "/home/mikias/Mikias/AI_Data_Engineering/Certifications/practice test/AI-102-AIEngineer/mslearn-ai-services/Labfiles/02-ai-services-security/Python/keyvault_client"
./run.sh
```

### Option 2: Manual
```bash
cd "/home/mikias/Mikias/AI_Data_Engineering/Certifications/practice test/AI-102-AIEngineer/mslearn-ai-services/Labfiles/02-ai-services-security/Python/keyvault_client"
source ../../01-use-azure-ai-services/Python/venv/bin/activate
python keyvault-client.py
```

### Test the Application
- Enter text in different languages:
  - "Hello" (English)
  - "Bonjour" (French)
  - "Gracias" (Spanish)
- Type "quit" to exit

---

## ✅ What This Lab Demonstrates

1. **Key Management**: How to regenerate keys when compromised
2. **Key Vault**: Secure storage of sensitive credentials
3. **Service Principal**: Identity-based access (better than storing keys in code)
4. **Best Practices**: 
   - Never hardcode keys in application code
   - Use Key Vault for production applications
   - Use Managed Identity when possible (instead of service principal passwords)

---

## 🔍 Troubleshooting

### Error: "The specified vault does not exist"
- Check that `KEY_VAULT` name in `.env` matches your Key Vault name (without `.vault.azure.net`)

### Error: "Access denied"
- Verify service principal has `get` and `list` permissions on Key Vault
- Check that the secret name is exactly `AI-Services-Key`

### Error: "Invalid client secret"
- Verify `APP_PASSWORD` in `.env` matches the password from service principal creation
- Note: If you lost the password, you'll need to create a new service principal

### Error: "Secret not found"
- Verify the secret name in Key Vault is exactly `AI-Services-Key` (case-sensitive)
- Check that the secret exists in your Key Vault

---

## 📚 Additional Resources

- [Azure Key Vault Documentation](https://docs.microsoft.com/azure/key-vault/)
- [Service Principal Authentication](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal)
- [Azure AI Services Security](https://docs.microsoft.com/azure/ai-services/security-features)

---

## 🧹 Clean Up (Optional)

After completing the lab, you can delete:
- Azure Key Vault resource
- Service Principal (App Registration)
- Or delete the entire resource group

**Note**: Keep your Azure AI Services resource for the next labs!

---

**Next**: Lab 3 - Monitor AI Services


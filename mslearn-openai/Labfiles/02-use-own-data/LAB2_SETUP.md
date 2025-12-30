# Day 2 - Lab 2: RAG with Own Data
## Setup Guide

## 🎯 Lab Objectives
- Provision Azure AI Search resource
- Create Azure Storage Account and upload data
- Deploy text-embedding-ada-002 model
- Create vectorized index in Azure AI Search
- Implement RAG pattern with Azure OpenAI

---

## 📋 Prerequisites

1. ✅ Azure OpenAI resource (from Lab 1)
2. ✅ Completed Lab 1 setup
3. ✅ Python 3.x installed

---

## 🔧 Step 1: Azure Resources

### ✅ Already Created:

1. **Azure AI Search**
   - **Name**: `ai-102-search`
   - **Resource Group**: `AI-102`
   - **Location**: East US
   - **Pricing Tier**: Basic

2. **Azure Storage Account**
   - **Name**: `ai102storage<timestamp>`
   - **Resource Group**: `AI-102`
   - **Location**: East US
   - **Container**: `margies-travel` (created)

3. **Model Deployments**
   - ✅ `gpt-4o` (from Lab 1)
   - ✅ `text-embedding-ada-002` (for vectorization)

4. **Data Uploaded**
   - ✅ PDF brochures uploaded to blob storage

---

## ⚙️ Step 2: Create Azure AI Search Index

### Manual Steps Required in Azure Portal:

1. **Navigate to Azure AI Search**
   - Go to Azure Portal → `ai-102-search` resource

2. **Import and Vectorize Data**
   - Click **Import and vectorize data**
   - Select **Azure Blob Storage**
   - Configure:
     - **Subscription**: Your subscription
     - **Blob storage account**: `ai102storage<timestamp>`
     - **Blob container**: `margies-travel`
     - **Blob folder**: (leave blank)
     - **Enable deletion tracking**: Unselected
     - **Authenticate using managed identity**: Unselected

3. **Vectorize Text**
   - **Kind**: Azure OpenAI
   - **Subscription**: Your subscription
   - **Azure OpenAI Service**: `ai-102-openai`
   - **Model deployment**: `text-embedding-ada-002`
   - **Authentication type**: API key
   - ✅ Check acknowledgment checkbox

4. **Skip Image Vectorization**
   - Do NOT select image vectorization or AI skills

5. **Enable Semantic Ranking**
   - Enable semantic ranking
   - Schedule indexer to run once

6. **Create Index**
   - **Objects name prefix**: `margies-index`
   - Click **Create**

### Wait for Indexing
- The indexer will process the PDF files
- This may take 5-10 minutes
- Check status in Azure Portal

---

## ⚙️ Step 3: Environment Configuration

### ✅ Already Configured:

The Azure AI Search credentials have been added to your shared `.env` file:

**Location**: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env`

```env
# Azure AI Search Configuration (for Day 2: Lab 2 - RAG)
AZURE_SEARCH_ENDPOINT=https://ai-102-search.search.windows.net
AZURE_SEARCH_KEY=<your-key>
AZURE_SEARCH_INDEX=margies-index
```

---

## 🚀 Step 4: Run the Application

### Option 1: Using the Run Script

```bash
cd mslearn-openai/Labfiles/02-use-own-data/Python
./run.sh
```

### Option 2: Manual Execution

```bash
cd mslearn-openai/Labfiles/02-use-own-data/Python
source ../../../../mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/venv/bin/activate
python ownData.py
```

**Note**: The application uses `query_type: "simple"` to avoid semantic search configuration requirements. If you want to use semantic or vector search, ensure your Azure AI Search index has the proper configuration.

---

## 📝 Application Features

### RAG Pattern Implementation

The application uses **Retrieval Augmented Generation (RAG)**:

1. **User Query**: User asks a question
2. **Vector Search**: Azure AI Search finds relevant documents
3. **Context Retrieval**: Relevant text chunks are retrieved
4. **Prompt Augmentation**: Retrieved context is added to the prompt
5. **Response Generation**: GPT-4o generates answer using retrieved context

### Example Queries

Try these questions:
- `Tell me about London`
- `What are the attractions in Dubai?`
- `What services does Margie's Travel offer?`
- `What are the highlights of New York?`

---

## 🔍 How RAG Works

### 1. **Data Preparation**
- PDF documents uploaded to blob storage
- Text extracted from PDFs
- Text chunked into smaller pieces

### 2. **Vectorization**
- Each text chunk converted to vector embeddings
- Uses `text-embedding-ada-002` model
- Vectors stored in Azure AI Search index

### 3. **Query Processing**
- User query converted to vector embedding
- Similar vectors found in search index
- Relevant document chunks retrieved

### 4. **Response Generation**
- Retrieved context added to prompt
- GPT-4o generates answer using context
- Citations can be shown (if enabled)

---

## 🧪 Testing the Application

### Test 1: Basic Query
1. Run the application
2. Enter: `Tell me about London`
3. Observe the response with citations

### Test 2: Enable Citations
1. Edit `ownData.py`
2. Set `showCitations = True`
3. Run again with the same query
4. See the source documents used

### Test 3: Different Queries
- Try questions about different cities
- Ask about specific services
- Test follow-up questions

---

## 📚 Key Concepts

### RAG (Retrieval Augmented Generation)
- **Retrieval**: Find relevant information from your data
- **Augmentation**: Add retrieved info to the prompt
- **Generation**: Generate response using retrieved context

### Vector Embeddings
- Text converted to numerical vectors
- Similar text has similar vectors
- Enables semantic search

### Azure AI Search
- Vector search capabilities
- Semantic ranking
- Document indexing
- Query processing

### Data Sources
- Azure Blob Storage for documents
- Azure AI Search for indexing
- Azure OpenAI for embeddings and generation

---

## 🔍 Troubleshooting

### Error: "Index not found"
- Verify the index name matches your actual index (may be `azureblob-index` or `margies-index`)
- Check the index name in your `.env` file: `AZURE_SEARCH_INDEX`
- Check that indexing completed successfully
- Wait for indexer to finish (5-10 minutes)

### Error: "AZURE_SEARCH_ENDPOINT not found"
- Verify the `.env` file has search credentials
- Check file location: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/Python/.env`

### Error: "401 Unauthorized"
- Verify the Azure AI Search key is correct
- Check that the search service is active

### Error: "No results found"
- Verify documents were uploaded to blob storage
- Check that indexer completed successfully
- Verify index contains documents

### Error: "Semantic configuration" or "semanticConfiguration query parameter"
- **Solution**: The code uses `query_type: "simple"` to avoid this error
- If you need semantic search, configure it in Azure AI Search (requires Standard tier)
- Or use vector search with proper embedding endpoint configuration

### Indexing Issues
- Check indexer status in Azure Portal
- Verify blob storage connection
- Check embedding model deployment

---

## 📚 Additional Resources

- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [RAG Pattern Guide](https://learn.microsoft.com/azure/ai-services/openai/concepts/use-your-data)
- [Vector Search](https://learn.microsoft.com/azure/search/vector-search-overview)
- [Azure OpenAI Embeddings](https://learn.microsoft.com/azure/ai-services/openai/concepts/embeddings)

---

## ✅ Completion Checklist

- [x] Azure AI Search resource created
- [x] Azure Storage Account created
- [x] Blob container created
- [x] PDF files uploaded
- [x] text-embedding-ada-002 model deployed
- [x] Environment configured
- [x] Application code updated
- [ ] Create index in Azure Portal (manual step)
- [ ] Wait for indexing to complete
- [ ] Test the application
- [ ] Verify citations work

---

## ⚠️ Important Notes

1. **Index Creation**: Must be done manually in Azure Portal
2. **Indexing Time**: Allow 5-10 minutes for indexing to complete
3. **Cost**: Azure AI Search Basic tier incurs costs
4. **Storage**: Blob storage also incurs costs

---

**Next**: Lab 3 - DALL-E Image Generation


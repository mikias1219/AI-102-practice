# AI-102 Study Plan - One Week
## Based on Official Exam Guide (Updated December 23, 2025)

> **Reference**: [Official AI-102 Study Guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102)

## Overview
This study plan is aligned with the **official AI-102 exam objectives** as of December 23, 2025. The exam now focuses heavily on **Microsoft Foundry Services** (formerly Azure AI Foundry) and includes new topics like generative AI solutions, agentic solutions, and Content Understanding.

### Exam Weightings (as of Dec 23, 2025)
- **Plan and manage an Azure AI solution** (20–25%)
- **Implement generative AI solutions** (15–20%) ⭐ NEW FOCUS
- **Implement an agentic solution** (5–10%) ⭐ NEW
- **Implement computer vision solutions** (10–15%)
- **Implement natural language processing solutions** (15–20%)
- **Implement knowledge mining and information extraction solutions** (15–20%)

---

## **Day 1: Microsoft Foundry Services Foundation** (20-25% of exam)
**Focus**: Plan and manage Azure AI solutions with Microsoft Foundry Services

### Morning (3-4 hours)
1. **mslearn-ai-services/Instructions/Labs/01-use-azure-ai-services.md**
   - ✅ **Select appropriate Microsoft Foundry Services** for different solutions
   - ✅ **Create Azure AI resource** (now part of Foundry)
   - ✅ **Determine default endpoint** for a service
   - ✅ **Install and utilize SDKs and APIs**
   - **Lab files**: `mslearn-ai-services/Labfiles/01-use-azure-ai-services/`
   - **Exam focus**: Selecting services, provisioning resources, SDK usage

2. **mslearn-ai-services/Instructions/Labs/02-ai-services-security.md**
   - ✅ **Manage and protect account keys**
   - ✅ **Manage authentication** for Microsoft Foundry Service resources
   - ✅ **Plan for Responsible AI principles**
   - **Lab files**: `mslearn-ai-services/Labfiles/02-ai-services-security/`
   - **Exam focus**: Security, authentication, Responsible AI planning

### Afternoon (2-3 hours)
3. **mslearn-ai-services/Instructions/Labs/03-monitor-ai-services.md**
   - ✅ **Monitor Azure AI resource**
   - ✅ **Manage costs** for Microsoft Foundry Services
   - **Lab files**: `mslearn-ai-services/Labfiles/03-monitor-ai-services/`
   - **Exam focus**: Monitoring, cost management

4. **mslearn-ai-services/Instructions/Labs/04-use-a-container.md**
   - ✅ **Plan and implement container deployment**
   - ✅ **Deploy AI models using appropriate deployment options**
   - **Lab files**: `mslearn-ai-services/Labfiles/04-use-a-container/`
   - **Exam focus**: Container deployment, deployment options

### Evening (1-2 hours)
5. **mslearn-ai-services/Instructions/Labs/05-implement-content-safety.md**
   - ✅ **Implement content moderation solutions**
   - ✅ **Configure responsible AI insights**, including content safety
   - ✅ **Implement responsible AI**, including content filters and blocklists
   - ✅ **Prevent harmful behavior**, including prompt shields and harm detection
   - **Lab files**: `mslearn-ai-services/Labfiles/05-implement-content-safety/`
   - **Exam focus**: Responsible AI implementation, content safety

**📚 Additional Study**: Review Microsoft Foundry documentation for:
- Service selection criteria
- CI/CD pipeline integration
- Model selection and deployment options

---

## **Day 2: Generative AI Solutions** (15-20% of exam) ⭐ HIGH PRIORITY
**Focus**: Build generative AI solutions with Microsoft Foundry and Azure OpenAI

### Morning (3-4 hours)
1. **mslearn-openai/Instructions/Labs/01-app-develop.md**
   - ✅ **Provision Azure OpenAI in Foundry Models resource**
   - ✅ **Select and deploy Azure OpenAI model**
   - ✅ **Submit prompts** to generate code and natural language responses
   - ✅ **Integrate Azure OpenAI** into your own application
   - ✅ **Configure parameters** to control generative behavior
   - ✅ **Apply prompt engineering techniques** to improve responses
   - **Lab files**: `mslearn-openai/Labfiles/01-app-develop/`
   - **Exam focus**: Azure OpenAI provisioning, prompt engineering, integration

2. **mslearn-openai/Instructions/Labs/02-use-own-data.md**
   - ✅ **Implement RAG pattern** by grounding a model in your data
   - ✅ **Deploy hub, project, and necessary resources** with Microsoft Foundry
   - **Lab files**: `mslearn-openai/Labfiles/02-use-own-data/`
   - **Exam focus**: RAG patterns, Foundry projects, data grounding

### Afternoon (2-3 hours)
3. **mslearn-ai-vision/Instructions/Labs/09-dall-e.md**
   - ✅ **Use DALL-E model** to generate images
   - ✅ **Use large multimodal models** in Azure OpenAI
   - **Lab files**: `mslearn-ai-vision/Labfiles/dalle-client/`
   - **Exam focus**: Image generation, multimodal models

4. **mslearn-ai-vision/Instructions/Labs/08-gen-ai-vision.md**
   - ✅ **Plan and prepare for a generative AI solution**
   - ✅ **Deploy appropriate generative AI model** for your use case
   - **Lab files**: `mslearn-ai-vision/Labfiles/gen-ai-vision/`
   - **Exam focus**: Generative AI planning, model deployment

### Evening (2-3 hours) - Advanced Generative AI
5. **Study Topics** (Review documentation - labs may be limited):
   - ✅ **Implement prompt flow solution** (Microsoft Foundry)
   - ✅ **Evaluate models and flows**
   - ✅ **Integrate project into application** with Microsoft Foundry SDK
   - ✅ **Utilize prompt templates** in generative AI solution
   - ✅ **Configure model monitoring and diagnostic settings**
   - ✅ **Optimize and manage resources** for deployment
   - ✅ **Enable tracing and collect feedback**
   - ✅ **Implement model reflection**
   - ✅ **Deploy containers** for local and edge devices
   - ✅ **Implement orchestration** of multiple generative AI models
   - ✅ **Fine-tune a generative model**

**📚 Critical Study**: Microsoft Foundry documentation on:
- Prompt flows
- Model evaluation
- Foundry SDK integration
- Prompt templates
- Model optimization and monitoring

---

## **Day 3: Agentic Solutions** (5-10% of exam) ⭐ NEW TOPIC
**Focus**: Create custom agents with Microsoft Foundry Agent Service

### Full Day (4-5 hours)
**⚠️ Note**: Agentic solutions are NEW in the exam. Labs may be limited. Focus on documentation and concepts.

1. **Study Topics** (Review Microsoft Foundry Agent documentation):
   - ✅ **Understand role and use cases** of an agent
   - ✅ **Configure necessary resources** to build an agent
   - ✅ **Create agent with Microsoft Foundry Agent Service**
   - ✅ **Implement complex agents** with Microsoft Agent Framework
   - ✅ **Implement complex workflows** including:
     - Orchestration for multi-agent solutions
     - Multiple users
     - Autonomous capabilities
   - ✅ **Test, optimize and deploy** an agent

**📚 Critical Resources**:
- Microsoft Foundry Agent Service documentation
- Microsoft Agent Framework documentation
- Agent orchestration patterns
- Multi-agent solutions

**Practice**: Try to create a simple agent using Microsoft Foundry if available in your subscription.

---

## **Day 4: Computer Vision Solutions** (10-15% of exam)
**Focus**: Analyze images, implement custom vision, analyze videos

### Morning (2-3 hours)
1. **mslearn-ai-vision/Instructions/Labs/01-analyze-images.md**
   - ✅ **Select visual features** to meet image processing requirements
   - ✅ **Detect objects in images** and generate image tags
   - ✅ **Include image analysis features** in an image processing request
   - ✅ **Interpret image processing responses**
   - **Lab files**: `mslearn-ai-vision/Labfiles/analyze-images/`
   - **Exam focus**: Image analysis, object detection, visual features

2. **mslearn-ai-vision/Instructions/Labs/02-ocr.md**
   - ✅ **Extract text from images** using Azure Vision in Foundry Tools
   - ✅ **Convert handwritten text** using Azure Vision in Foundry Tools
   - **Lab files**: `mslearn-ai-vision/Labfiles/ocr/`
   - **Exam focus**: OCR, handwritten text recognition (Foundry Tools)

### Afternoon (2-3 hours)
3. **mslearn-ai-vision/Instructions/Labs/03-face-service.md**
   - ✅ Face detection and recognition
   - **Lab files**: `mslearn-ai-vision/Labfiles/face/`
   - **Exam focus**: Face service capabilities

4. **mslearn-ai-vision/Instructions/Labs/04-image-classification.md**
   - ✅ **Choose between image classification and object detection** models
   - ✅ **Label images**
   - ✅ **Train custom image model** (image classification)
   - ✅ **Evaluate custom vision model metrics**
   - ✅ **Publish a custom vision model**
   - ✅ **Consume a custom vision model**
   - ✅ **Build custom vision model code first**
   - **Lab files**: `mslearn-ai-vision/Labfiles/image-classification/`
   - **Exam focus**: Custom vision models, training, evaluation

### Evening (1-2 hours)
5. **mslearn-ai-vision/Instructions/Labs/05-custom-vision-object-detection.md**
   - ✅ **Train custom image model** (object detection)
   - ✅ **Evaluate custom vision model metrics**
   - **Lab files**: `mslearn-ai-vision/Labfiles/object-detection/`
   - **Exam focus**: Object detection models

6. **mslearn-ai-vision/Instructions/Labs/06-video-indexer.md**
   - ✅ **Use Azure AI Video Indexer** to extract insights from video or live stream
   - ✅ **Use Azure Vision in Foundry Tools Spatial Analysis** to detect presence and movement of people in video
   - **Lab files**: `mslearn-ai-vision/Labfiles/video-indexer/`
   - **Exam focus**: Video analysis, spatial analysis (Foundry Tools)

---

## **Day 5: Natural Language Processing** (15-20% of exam)
**Focus**: Text analysis, translation, speech processing, custom language models

### Morning (2-3 hours)
1. **mslearn-ai-language/Instructions/Labs/01-analyze-text.md**
   - ✅ **Extract key phrases and entities**
   - ✅ **Determine sentiment** of text
   - ✅ **Detect language** used in text
   - ✅ **Detect PII** in text
   - **Lab files**: `mslearn-ai-language/Labfiles/01-analyze-text/`
   - **Exam focus**: Text analysis, sentiment, PII detection

2. **mslearn-ai-language/Instructions/Labs/06-translate-text.md**
   - ✅ **Translate text and documents** using Azure Translator in Foundry Tools
   - ✅ **Implement custom translation**, including training, improving, and publishing a custom model
   - **Lab files**: `mslearn-ai-language/Labfiles/06-translator-sdk/`
   - **Exam focus**: Translation (Foundry Tools), custom translation models

### Afternoon (2-3 hours)
3. **mslearn-ai-language/Instructions/Labs/07-speech.md**
   - ✅ **Implement text-to-speech and speech-to-text** using Azure Speech in Foundry Tools
   - ✅ **Improve text-to-speech** using SSML
   - ✅ **Implement custom speech solutions** with Azure Speech in Foundry Tools
   - ✅ **Integrate generative AI speaking capabilities** in an application
   - **Lab files**: `mslearn-ai-language/Labfiles/07-speech/`
   - **Exam focus**: Speech services (Foundry Tools), SSML, custom speech

4. **mslearn-ai-language/Instructions/Labs/08-translate-speech.md**
   - ✅ **Translate speech-to-speech and speech-to-text** using Azure Speech in Foundry Tools
   - ✅ **Implement intent and keyword recognition** with Azure Speech in Foundry Tools
   - **Lab files**: `mslearn-ai-language/Labfiles/08-speech-translation/`
   - **Exam focus**: Speech translation, intent recognition (Foundry Tools)

### Evening (2-3 hours)
5. **mslearn-ai-language/Instructions/Labs/03-language-understanding.md**
   - ✅ **Create intents, entities, and add utterances**
   - ✅ **Train, evaluate, deploy, and test** a language understanding model
   - ✅ **Optimize, backup, and recover** language understanding model
   - ✅ **Consume a language model** from a client application
   - **Lab files**: `mslearn-ai-language/Labfiles/03-language/`
   - **Exam focus**: Language understanding models, CLU/LUIS

6. **mslearn-ai-language/Instructions/Labs/02-qna.md**
   - ✅ **Create custom question answering project**
   - ✅ **Add question-and-answer pairs** and import sources
   - ✅ **Train, test, and publish** a knowledge base
   - ✅ **Create multi-turn conversation**
   - ✅ **Add alternate phrasing and chit-chat** to knowledge base
   - ✅ **Export a knowledge base**
   - ✅ **Create multi-language question answering** solution
   - **Lab files**: `mslearn-ai-language/Labfiles/02-qna/`
   - **Exam focus**: Question answering, knowledge bases

7. **mslearn-ai-language/Instructions/Labs/04-text-classification.md**
   - ✅ Custom text classification
   - **Lab files**: `mslearn-ai-language/Labfiles/04-text-classification/`

8. **mslearn-ai-language/Instructions/Labs/05-extract-custom-entities.md**
   - ✅ Custom entity recognition
   - **Lab files**: `mslearn-ai-language/Labfiles/05-custom-entity-recognition/`

---

## **Day 6: Knowledge Mining & Information Extraction** (15-20% of exam)
**Focus**: Azure AI Search, Document Intelligence, Content Understanding

### Morning (2-3 hours)
1. **mslearn-knowledge-mining/Instructions/Labs/01-azure-search.md**
   - ✅ **Provision Azure AI Search resource**, create an index, and define a skillset
   - ✅ **Create data sources and indexers**
   - ✅ **Query an index**, including syntax, sorting, filtering, and wildcards
   - **Lab files**: `mslearn-knowledge-mining/Labfiles/01-azure-search/`
   - **Exam focus**: Azure AI Search basics, indexing, querying

2. **mslearn-knowledge-mining/Instructions/Labs/02-search-skills.md**
   - ✅ **Implement custom skills** and include them in a skillset
   - ✅ **Create and run an indexer**
   - **Lab files**: `mslearn-knowledge-mining/Labfiles/02-search-skill/`
   - **Exam focus**: Custom skills, skillsets, indexers

### Afternoon (2-3 hours)
3. **mslearn-knowledge-mining/Instructions/Labs/03-knowledge-store.md**
   - ✅ **Manage Knowledge Store projections**, including file, object, and table projections
   - **Lab files**: `mslearn-knowledge-mining/Labfiles/03-knowledge-store/`
   - **Exam focus**: Knowledge Store, projections

4. **mslearn-knowledge-mining/Instructions/Labs/09-semantic-search-exercise.md**
   - ✅ **Implement semantic** solutions
   - **Lab files**: Check instructions
   - **Exam focus**: Semantic search

5. **mslearn-knowledge-mining/Instructions/Labs/10-vector-search-exercise.md**
   - ✅ **Implement vector store** solutions
   - **Lab files**: Check instructions
   - **Exam focus**: Vector search

### Evening (2-3 hours)
6. **mslearn-ai-document-intelligence/Instructions/Labs/01-use-prebuilt-models.md**
   - ✅ **Provision Document Intelligence resource**
   - ✅ **Use prebuilt models** to extract data from documents
   - **Lab files**: `mslearn-ai-document-intelligence/Labfiles/01-prebuild-models/`
   - **Exam focus**: Document Intelligence (Foundry Tools), prebuilt models

7. **mslearn-ai-document-intelligence/Instructions/Labs/02-custom-document-intelligence.md**
   - ✅ **Implement custom document intelligence model**
   - ✅ **Train, test, and publish** a custom document intelligence model
   - **Lab files**: `mslearn-ai-document-intelligence/Labfiles/02-custom-document-intelligence/`
   - **Exam focus**: Custom Document Intelligence models

8. **mslearn-ai-document-intelligence/Instructions/Labs/03-composed-model.md**
   - ✅ **Create composed document intelligence model**
   - **Lab files**: `mslearn-ai-document-intelligence/Labfiles/03-composed-model/`
   - **Exam focus**: Composed models

---

## **Day 7: Content Understanding & Review** (15-20% of exam)
**Focus**: Azure Content Understanding in Foundry Tools + Comprehensive Review

### Morning (2-3 hours)
1. **mslearn-ai-document-intelligence/Instructions/Labs/05-content-understanding.md**
   - ✅ **Extract information with Azure Content Understanding in Foundry Tools**
   - ✅ **Create OCR pipeline** to extract text from images and documents
   - ✅ **Summarize, classify, and detect attributes** of documents
   - ✅ **Extract entities, tables, and images** from documents
   - ✅ **Process and ingest documents, images, videos, and audio** with Azure Content Understanding in Foundry Tools
   - **Lab files**: `mslearn-ai-document-intelligence/Labfiles/05-content-understanding/`
   - **Exam focus**: Content Understanding (Foundry Tools) ⭐ NEW TOPIC

2. **Additional Foundry Tools Study**:
   - Review Azure Vision in Foundry Tools capabilities
   - Review Azure Speech in Foundry Tools capabilities
   - Review Azure Translator in Foundry Tools capabilities
   - Review Azure Document Intelligence in Foundry Tools capabilities

### Afternoon (2-3 hours) - Review & Practice
3. **Review Remaining Labs**:
   - `mslearn-knowledge-mining/Instructions/Labs/04-08.md` (if time permits)
   - `mslearn-ai-language/Instructions/Labs/09-11.md` (audio chat, voice live API)

4. **Exam Preparation Review**:
   - ✅ Review all Microsoft Foundry Services selection criteria
   - ✅ Review Responsible AI principles and implementation
   - ✅ Review deployment options (containers, endpoints, etc.)
   - ✅ Review monitoring and cost management
   - ✅ Review authentication and security best practices

### Evening (2-3 hours) - Final Preparation
5. **Practice Exam Topics**:
   - Create resources from scratch
   - Understand pricing tiers and quotas
   - Practice troubleshooting common issues
   - Review service selection scenarios
   - Review Foundry Tools vs traditional services

6. **Take Practice Assessment**:
   - [Free Practice Assessment](https://learn.microsoft.com/en-us/credentials/certifications/exams/ai-102/practice/assessment?assessment-type=practice&assessmentId=61)

---

## **Key Changes in Exam (Dec 23, 2025)**

### ⚠️ Critical Updates:
1. **Microsoft Foundry Services** - Now the primary platform (replaces "Azure AI Foundry")
2. **Generative AI Solutions** - Major new focus (15-20%)
3. **Agentic Solutions** - Completely new topic (5-10%)
4. **Content Understanding in Foundry Tools** - New service
5. **Foundry Tools** - Services now accessed through Foundry:
   - Azure Vision in Foundry Tools
   - Azure Speech in Foundry Tools
   - Azure Translator in Foundry Tools
   - Azure Document Intelligence in Foundry Tools

### 📚 Essential Documentation to Review:
- [Microsoft Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI services](https://learn.microsoft.com/en-us/azure/ai-services/)
- [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/)
- [Responsible AI](https://learn.microsoft.com/en-us/azure/ai-services/responsible-ai/)

---

## **Quick Start Guide**

### Prerequisites
- Azure subscription (free trial available)
- Access to Azure Portal
- Microsoft Foundry access (may require approval)
- Cloud Shell or local development environment
- Python or C# (depending on lab preference)

### How to Use This Plan
1. **Start with Day 1** - Foundation is critical
2. **Prioritize Day 2** - Generative AI is 15-20% of exam
3. Follow labs in order for each day
4. Each lab typically takes 30-60 minutes
5. Focus on understanding concepts, not just completing tasks
6. Take notes on Foundry Services vs traditional services

### Tips for Success
- **Morning sessions**: Focus on new concepts when fresh
- **Afternoon sessions**: Practice and reinforce learning
- **Evening sessions**: Review and explore advanced topics
- **Take breaks**: Understanding is key, don't rush
- **Practice**: Try variations to reinforce learning
- **Documentation**: Read Foundry documentation alongside labs

### Exam Focus Areas
Based on exam weightings, prioritize:
1. **Plan and manage** (20-25%) - Day 1
2. **Generative AI** (15-20%) - Day 2 ⭐
3. **NLP** (15-20%) - Day 5
4. **Knowledge Mining** (15-20%) - Day 6
5. **Computer Vision** (10-15%) - Day 4
6. **Agentic Solutions** (5-10%) - Day 3

---

## **START HERE: Day 1, Lab 1**
**Begin with**: `mslearn-ai-services/Instructions/Labs/01-use-azure-ai-services.md`

**Reference**: [Official AI-102 Study Guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102)

Good luck with your studies! 🚀

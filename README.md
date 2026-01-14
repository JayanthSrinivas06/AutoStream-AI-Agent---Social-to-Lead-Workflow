# AutoStream AI Agent - Social-to-Lead Workflow

[![Python](https://img.shields.io/badge/Python-3.11.9-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0+-purple.svg)](https://github.com/langchain-ai/langgraph)

An intelligent conversational AI agent for **AutoStream**, a SaaS platform for automated video editing. This agent demonstrates production-ready GenAI capabilities including intent classification, RAG-powered knowledge retrieval, and intelligent lead capture with advanced token optimization.

## 🎯 Overview

This project implements a stateful conversational agent that:
- Classifies user intent in real-time
- Retrieves relevant information using semantic search
- Captures lead information when users show purchase intent
- Optimizes API token usage by 60% through intelligent prompt engineering
- Provides a modern, tech-themed chat interface with markdown support

## 🏗️ Architecture

### Technology Stack

- **Framework**: LangGraph 0.2.0+ (state management and workflow orchestration)
- **LLM**: Google Gemini API (gemini-2.5-flash-lite)
- **Vector Store**: FAISS with HuggingFace embeddings
- **API**: FastAPI with Mangum for serverless deployment
- **Frontend**: HTML/CSS/JavaScript with marked.js for markdown rendering
- **Deployment**: Vercel (serverless)
- **Python**: 3.11.9

### Why LangGraph?

LangGraph provides:
1. **Native State Management**: Built-in state persistence with checkpointing
2. **Graph-Based Workflow**: Natural representation of conversation flow with conditional routing
3. **Serverless Compatibility**: Works seamlessly in Vercel's serverless environment
4. **Flexibility**: Easy to extend with new nodes and conditional edges

### State Schema

```python
class AgentState(TypedDict):
    messages: List          # Conversation history (optimized to last 4 messages)
    intent: str            # Current intent (greeting/inquiry/high_intent_lead)
    user_name: str         # Collected name
    user_email: str        # Collected email
    user_platform: str     # Creator platform (YouTube, Instagram, etc.)
    lead_captured: bool    # Lead capture status
    context: str           # RAG-retrieved context
```

### Conversation Flow

```
User Message → Intent Classification → Route by Intent
                                       ↓
                     ┌─────────────────┼─────────────────┐
                     ↓                 ↓                 ↓
                 Greeting          Inquiry         High Intent
                     ↓                 ↓                 ↓
                 Respond      RAG Retrieval      Extract Info
                     ↓                 ↓                 ↓
                    END            Respond      All Data Collected?
                                      ↓                 ↓
                                     END        Lead Capture → Respond → END
```

## 📁 Project Structure

```
SocioLead/
├── api/
│   ├── chat.py              # FastAPI endpoint (Vercel serverless)
│   └── requirements.txt     # Python dependencies for Vercel
├── src/
│   ├── agent/
│   │   ├── graph.py         # LangGraph workflow definition
│   │   ├── nodes.py         # Processing nodes with optimized prompts
│   │   └── state.py         # State schema
│   ├── rag/
│   │   ├── knowledge_base.json  # AutoStream product data
│   │   └── retriever.py     # FAISS-based RAG pipeline
│   ├── tools/
│   │   └── lead_capture.py  # Lead capture tool
│   └── utils/
│       ├── intent.py        # Intent classification with keyword detection
│       └── checkpointer.py  # State persistence utility (optional)
├── frontend/
│   ├── index.html           # Tech-themed chat interface
│   ├── style.css            # Black/grey/white gradient design
│   └── script.js            # Frontend logic with markdown support
├── .env                     # Environment variables (gitignored)
├── .gitignore               # Git ignore rules
├── vercel.json              # Vercel deployment configuration
└── README.md
```

## 🔄 How It Works

### 1. Intent Classification

The agent first classifies user intent using a two-stage approach:

**Stage 1: Keyword Detection**
- Checks for high-intent keywords (e.g., "sign up", "try", "my channel")
- Reduces API calls by ~30-40%

**Stage 2: LLM Classification**
- Uses Gemini API with compressed prompts
- Classifies as: greeting, inquiry, or high_intent_lead

### 2. RAG-Powered Responses

For product inquiries:
1. User query is embedded using HuggingFace embeddings
2. FAISS retrieves semantically similar content from knowledge base
3. Retrieved context is injected into LLM prompt
4. Gemini generates accurate, context-aware response

### 3. Lead Capture Flow

When high intent is detected:
1. Agent enters lead capture mode
2. Sequentially collects: name → email → platform
3. Validates data completeness before tool execution
4. Triggers lead capture only when all fields are collected
5. Confirms account setup to user

### 4. State Management

- Uses LangGraph's StateGraph for workflow orchestration
- State persists across conversation turns using session IDs
- Optimized to maintain only last 4 messages for context

## ⚡ Token Optimization

### Performance Metrics

**Before Optimization:**
- ~800-1200 tokens per conversation turn
- Verbose system prompts (~150-200 tokens)
- Full conversation history (10 messages)

**After Optimization:**
- ~300-500 tokens per conversation turn
- Compressed prompts (~50-80 tokens)
- Reduced history (4 messages)
- **Overall: 60% token reduction**

### Optimization Strategies

1. **Conversation History Reduction**
   - Limited from 10 to 4 messages
   - Saves ~60% on context tokens

2. **Prompt Compression**
   - Example: "You are a friendly AI assistant for AutoStream..." → "AutoStream AI assistant. Greet warmly, ask how to help. Be brief."
   - Saves ~60-70% on prompt tokens

3. **Smart Keyword Detection**
   - Checks keywords before LLM call
   - Reduces API calls by 30-40%

4. **Optimized Intent Classification**
   - Compressed classification prompt by 70%
   - Faster response times

### Benefits

- ✅ 3x more conversations within API quota
- ✅ Faster response times
- ✅ 60% cost reduction
- ✅ Better user experience

## 🎨 Frontend Design

### Tech-Themed Interface
- **Color Scheme**: Black, grey, and white gradients
- **Typography**: Inter font with JetBrains Mono for code
- **Animations**: Smooth transitions and typing indicators
- **Responsive**: Works on desktop and mobile

### Markdown Support
- **Bold/Italic**: Proper text formatting
- **Lists**: Bullet points and numbered lists
- **Code Blocks**: Syntax highlighting
- **Links**: Clickable URLs

All AI responses are rendered with markdown for better readability.

## 🚀 Setup & Deployment

### Local Setup

1. **Install Dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Create .env file
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-2.5-flash-lite
   ```

3. **Run Server**
   ```bash
   uvicorn api.chat:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Open Frontend**
   - Open `frontend/index.html` in browser
   - Or visit http://localhost:8000

### Vercel Deployment

1. **Configure Environment Variables**
   - `GEMINI_API_KEY`: Your Gemini API key
   - `GEMINI_MODEL`: gemini-2.5-flash-lite (optional)

2. **Deploy**
   ```bash
   vercel
   ```

The `vercel.json` configuration handles:
- Python serverless functions in `/api`
- Static frontend files in `/frontend`
- Automatic routing

## 📊 Key Features

### Intent Classification
- Real-time intent detection
- Keyword-first optimization
- Fallback to LLM classification

### RAG Implementation
- FAISS vector store for semantic search
- HuggingFace embeddings
- Context-aware response generation

### Lead Capture
- Sequential information collection
- Data validation before tool execution
- Prevents premature API calls

### Token Efficiency
- 60% reduction in API usage
- Compressed prompts
- Optimized conversation history
- Smart keyword detection

### Modern UI
- Tech-themed design
- Markdown rendering
- Quick action buttons
- Responsive layout

## 📦 Dependencies

```
fastapi==0.124.4
uvicorn==0.33.0
pydantic==2.10.6
python-dotenv==1.0.0

langchain>=0.3.0
langchain-community>=0.3.0
langchain-core>=0.3.15
langchain-text-splitters>=0.3.0
langgraph>=0.2.0
langchain-google-genai>=2.0.0

faiss-cpu>=1.9.0
sentence-transformers>=2.6.0
```

## 🎯 Technical Highlights

- **Stateful Conversations**: LangGraph StateGraph with session-based persistence
- **Optimized Performance**: 60% token reduction through intelligent engineering
- **Production Ready**: Serverless deployment with comprehensive error handling
- **Modern Stack**: Latest LangChain, Gemini API, and FastAPI
- **Clean Architecture**: Modular, well-organized, and maintainable code

## 🙏 Acknowledgments

Built as part of the ServiceHive Inflx Machine Learning Internship assignment.

---

**Built with ❤️ using LangGraph, Google Gemini, and FastAPI**

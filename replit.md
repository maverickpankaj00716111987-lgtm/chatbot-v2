# RAG Chatbot - Production-Grade Document Q&A System

## Overview
A production-level RAG (Retrieval Augmented Generation) chatbot built with FastAPI, LangGraph, and LangSmith. The system enables users to upload documents, ask questions, and receive AI-powered responses with context from their document collection.

## Architecture

### Core Components
1. **FastAPI Backend** - REST API server with async support
2. **LangGraph Agent** - State-based conversation orchestration
3. **LangSmith Integration** - Observability and tracing
4. **Vector Store** - Custom lightweight vector similarity search
5. **PostgreSQL Database** - Conversation and state persistence
6. **Web Interface** - Interactive chat UI with document upload

### Key Features
- **Customizable Models**: Runtime switching between OpenAI GPT-4 and Anthropic Claude
- **Fallback System**: Automatic model fallback on primary model failure
- **Document Processing**: PDF and text file upload with chunking and embedding
- **Vector Search**: Semantic document retrieval using embeddings
- **Conversation Persistence**: Full chat history storage and retrieval
- **State Logging**: Complete agent state tracking for debugging
- **LangSmith Observability**: Distributed tracing and monitoring

## Project Structure
```
.
├── main.py                     # FastAPI application entry point
├── src/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── agent/
│   │   └── graph.py           # LangGraph agent implementation
│   ├── database/
│   │   ├── connection.py      # Database connection and session management
│   │   └── models.py          # SQLAlchemy models
│   ├── models/
│   │   └── config.py          # Configuration settings
│   ├── utils/
│   │   ├── document_processor.py  # Document chunking and text extraction
│   │   ├── llm_manager.py         # LLM and embedding management
│   │   └── conversation_manager.py # Chat session persistence
│   └── vector_store/
│       └── simple_vector_store.py # Vector similarity search
├── static/
│   ├── app.js                 # Frontend JavaScript
│   └── style.css              # Styling
├── templates/
│   └── index.html             # Chat interface
└── uploaded_docs/             # Document storage directory
```

## Configuration

### Required API Keys
- `OPENAI_API_KEY` - For GPT-4 and embeddings (primary model)
- `ANTHROPIC_API_KEY` - For Claude (fallback model)
- `LANGSMITH_API_KEY` - For observability (optional but recommended)

### Model Configuration
- Primary Model: GPT-4 Turbo Preview (customizable)
- Fallback Model: Claude 3 Sonnet (customizable)
- Embedding Model: text-embedding-3-small

### Database
- PostgreSQL database for conversation and state persistence
- Tables: conversation_sessions, messages, agent_states, documents, document_chunks

## API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send a message and get AI response
- `POST /api/sessions/new` - Create a new conversation session
- `GET /api/sessions` - List all conversation sessions
- `GET /api/sessions/{session_id}` - Get session details with full history

### Document Endpoints
- `POST /api/upload` - Upload documents (PDF, TXT, MD)
- `GET /api/documents` - List all uploaded documents

### Health
- `GET /api/health` - System health check and model status

## LangGraph Workflow

The agent follows this state machine:
1. **Retrieve** - Generate query embedding and retrieve relevant documents
2. **Generate** - Generate response using LLM with retrieved context
3. **Log State** - Persist state to database for observability

All state transitions are logged when `LOG_ALL_STATES=true`.

## LangSmith Integration

When enabled, LangSmith provides:
- Complete trace of all LLM calls
- State transition visualization
- Performance metrics
- Error tracking
- Token usage monitoring

Project name in LangSmith: Configured via `LANGSMITH_PROJECT` env var

## Usage

1. Start the application (workflow runs automatically)
2. Open the web interface at the provided URL
3. Upload documents using the sidebar
4. Start a new chat or continue existing conversations
5. Ask questions - the system retrieves relevant documents and generates answers
6. View conversation history and switch between sessions

## Production Features

### Error Handling
- Automatic retry with exponential backoff
- Model fallback on primary model failure
- Graceful degradation when no documents are available
- Comprehensive error logging

### Performance
- Lightweight vector store for fast similarity search
- Database indexing for efficient queries
- Async API endpoints for concurrent requests
- Connection pooling for database

### Observability
- Full state logging to database
- LangSmith tracing integration
- Structured logging throughout
- Health check endpoint

## Customization

### Adding Custom Tools
The tool registry in the agent can be extended by modifying `src/agent/graph.py` to add new nodes to the LangGraph workflow.

### Model Configuration
Change models by setting environment variables:
- `PRIMARY_MODEL` - Any OpenAI model
- `FALLBACK_MODEL` - Any Anthropic model
- `EMBEDDING_MODEL` - Any OpenAI embedding model

### Document Processing
Adjust chunking parameters:
- `CHUNK_SIZE` - Size of each document chunk (default: 1000)
- `CHUNK_OVERLAP` - Overlap between chunks (default: 200)
- `TOP_K_DOCS` - Number of documents to retrieve (default: 5)

## Recent Changes
- 2025-11-01: Initial implementation with all core features
- Production-ready RAG chatbot with LangGraph and LangSmith
- Full conversation persistence and state logging
- Customizable models with fallback mechanisms

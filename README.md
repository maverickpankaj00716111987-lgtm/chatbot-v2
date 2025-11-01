# RAG Chatbot - Production-Grade Document Q&A System

A production-ready conversational AI chatbot built with FastAPI, LangGraph, and LangSmith. Upload documents, ask questions, and receive AI-powered responses with context from your knowledge base.

## Features

- 🤖 **Customizable AI Models**: Switch between OpenAI GPT-4 and Anthropic Claude
- 🔄 **Automatic Fallback**: Seamless failover to backup model on errors
- 📄 **Document Processing**: Upload PDFs and text files with automatic chunking and embedding
- 🔍 **Vector Search**: Fast semantic search using custom vector store
- 💬 **Conversation Management**: Persistent chat history with PostgreSQL
- 📊 **LangSmith Observability**: Complete tracing and monitoring of agent states
- 🎯 **State Logging**: Full audit trail of all agent state transitions
- 🛡️ **Production Ready**: Comprehensive error handling and retry logic

## Quick Start

### 1. Get API Keys

You'll need API keys for the AI models:

- **OpenAI API Key** (primary model): Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic API Key** (fallback model): Get from [Anthropic Console](https://console.anthropic.com/)
- **LangSmith API Key** (optional, for observability): Get from [LangSmith](https://smith.langchain.com/)

The system will prompt you to add these keys when you first run the application.

### 2. Access the Application

Click the **Run** button or visit the webview URL. The chatbot interface will load automatically.

### 3. Upload Documents

1. Click the file upload button in the sidebar
2. Select PDF or text files (.pdf, .txt, .md)
3. Click "Upload" - the system will:
   - Extract and chunk the text
   - Generate embeddings
   - Index for vector search

### 4. Start Chatting

- Type your question in the input box
- The AI will search your documents and generate contextual answers
- View referenced documents and relevance scores
- Create new chat sessions or continue previous conversations

## Configuration

### Environment Variables

Create a `.env` file or set these through the Replit Secrets:

```bash
# Required: AI Model API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: Observability
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=rag-chatbot
ENABLE_LANGSMITH=true

# Model Configuration
PRIMARY_MODEL=gpt-4-turbo-preview
FALLBACK_MODEL=claude-3-sonnet-20240229
EMBEDDING_MODEL=text-embedding-3-small

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_DOCS=5

# Conversation Settings
SHORT_TERM_MEMORY_WINDOW=5
LOG_ALL_STATES=true
```

### Customizing Models

Change the AI models by updating the environment variables:

- **PRIMARY_MODEL**: Any OpenAI model (gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo)
- **FALLBACK_MODEL**: Any Anthropic model (claude-3-opus, claude-3-sonnet, claude-3-haiku)
- **EMBEDDING_MODEL**: OpenAI embedding model (text-embedding-3-small, text-embedding-3-large)

## API Endpoints

### Chat
- `POST /api/chat` - Send a message and receive AI response
  ```json
  {
    "message": "What is machine learning?",
    "session_id": "optional-session-id"
  }
  ```

### Documents
- `POST /api/upload` - Upload document (multipart/form-data)
- `GET /api/documents` - List all uploaded documents

### Sessions
- `POST /api/sessions/new` - Create new conversation session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{session_id}` - Get session details with full history

### Health
- `GET /api/health` - System status and model availability

## Architecture

### LangGraph Workflow

The agent follows a state machine:
1. **Retrieve**: Generate query embedding → Search vector store → Retrieve top-K documents
2. **Generate**: Build context → Call LLM with retrieved docs → Generate response
3. **Log State**: Persist state to database for observability

### Database Schema

PostgreSQL tables:
- `conversation_sessions`: Chat sessions with metadata
- `messages`: Individual messages (user/assistant)
- `agent_states`: Complete state transitions for debugging
- `documents`: Uploaded documents with embedding metadata
- `document_chunks`: Chunked text with vector embeddings

### Vector Search

Custom lightweight vector store using:
- NumPy for cosine similarity calculations
- JSON persistence for embeddings and metadata
- Fast in-memory search for production workloads

## Production Features

### Error Handling
- ✅ Automatic retry with exponential backoff
- ✅ Model fallback on primary failure
- ✅ Graceful degradation when no documents available
- ✅ Comprehensive error logging

### Security
- ✅ Path traversal protection on file uploads
- ✅ Secrets management via environment variables
- ✅ SQL injection prevention with ORM
- ✅ CORS configured for secure frontend access

### Observability
- ✅ Full state logging to database
- ✅ LangSmith tracing integration
- ✅ Structured logging throughout
- ✅ Health check endpoint

## Development

### Project Structure
```
├── main.py                        # FastAPI application
├── src/
│   ├── api/routes.py             # REST API endpoints
│   ├── agent/graph.py            # LangGraph agent
│   ├── database/                 # PostgreSQL models & connection
│   ├── models/config.py          # Configuration settings
│   ├── utils/                    # LLM, docs, conversation managers
│   └── vector_store/             # Custom vector search
├── static/                       # Frontend assets
├── templates/                    # HTML templates
└── uploaded_docs/                # Document storage
```

### Adding Custom Tools

Extend the LangGraph agent by adding nodes in `src/agent/graph.py`:

```python
def _custom_tool(self, state: AgentState) -> Dict:
    # Your custom logic
    return {"custom_result": result}

workflow.add_node("custom_tool", self._custom_tool)
workflow.add_edge("retrieve", "custom_tool")
workflow.add_edge("custom_tool", "generate")
```

## Troubleshooting

### Application won't start
- Verify all required API keys are set
- Check the workflow logs for errors
- Ensure DATABASE_URL is configured

### Document upload fails
- Supported formats: PDF, TXT, MD
- Check file size (large files may take time)
- Verify OpenAI API key for embeddings

### Chat responses are slow
- First response initializes models (may take 10-20 seconds)
- Subsequent responses are faster
- Check LangSmith for performance traces

### No documents retrieved
- Verify documents were successfully uploaded
- Check vector store has been saved
- Try broader queries if results are sparse

## LangSmith Integration

When enabled (set `LANGSMITH_API_KEY`), view:
- Complete traces of all LLM calls
- State transition visualization
- Performance metrics and latency
- Token usage and costs
- Error tracking

Visit [LangSmith](https://smith.langchain.com/) to view your project traces.

## Support

For issues or questions:
1. Check the workflow logs in Replit
2. Review the database state in the Replit Database pane
3. Enable debug logging: Set `LOG_LEVEL=DEBUG`

## License

MIT License - feel free to use and modify as needed.

# Getting Started with Your RAG Chatbot

## 🚀 Quick Start (5 Minutes)

Your production-grade RAG chatbot is already running! Follow these steps to start using it:

### Step 1: Add Your API Keys

The system needs API keys to function. Click on the **Secrets** tab (🔒) in the left sidebar and add:

**Required:**
- `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Sign up if needed (free tier available)
  - Create a new secret key
  - Copy and paste into Replit Secrets

**Optional (for fallback):**
- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com/)
  - Provides automatic fallback if OpenAI fails
  - Recommended for production reliability

**Optional (for monitoring):**
- `LANGSMITH_API_KEY` - Get from [LangSmith](https://smith.langchain.com/)
  - Enables detailed tracing and observability
  - Helpful for debugging and optimization

### Step 2: Restart the Application

After adding your API keys:
1. Stop the current workflow (if running)
2. Click the **Run** button again
3. Wait for "Application started successfully" in the console

### Step 3: Upload Your First Document

1. Open the webview (click the web browser icon or the URL)
2. Click "Choose Files" in the Upload Documents section
3. Select a PDF or text file (try a research paper, manual, or article)
4. Click "Upload"
5. Wait for the success message showing chunks created

**Supported formats:**
- PDF (.pdf)
- Plain text (.txt)
- Markdown (.md)

### Step 4: Ask Your First Question

1. Type a question related to your uploaded document in the input box
2. Press Enter or click "Send"
3. The AI will:
   - Search your documents for relevant context
   - Generate an answer based on the content
   - Show which documents were referenced

**Example questions:**
- "Summarize the main points of this document"
- "What does the document say about [specific topic]?"
- "Compare the approaches mentioned in the document"

## 📋 What Happens Behind the Scenes

When you ask a question:

1. **Embedding**: Your question is converted to a vector representation
2. **Search**: The system searches all uploaded documents for similar content
3. **Retrieval**: Top 5 most relevant document chunks are selected
4. **Generation**: The AI reads those chunks and generates a contextual answer
5. **Logging**: Everything is logged to the database for future reference

## 🎯 Tips for Best Results

### Document Upload
- Upload related documents together for better context
- Larger documents are automatically chunked (1000 characters per chunk)
- The system handles overlapping chunks to maintain context

### Asking Questions
- Be specific about what you're looking for
- Reference document names if you've uploaded multiple files
- Use follow-up questions to dive deeper

### Managing Conversations
- Click "New Chat" to start fresh
- Previous conversations are saved and can be resumed
- View conversation history in the sidebar

## 🔧 Configuration Options

### Change AI Models

Edit your Secrets to use different models:

```
PRIMARY_MODEL=gpt-4  # Try gpt-3.5-turbo for faster, cheaper responses
FALLBACK_MODEL=claude-3-haiku-20240307  # Faster fallback
```

### Adjust Document Processing

```
CHUNK_SIZE=500  # Smaller chunks for more precise retrieval
TOP_K_DOCS=10  # Retrieve more documents for comprehensive answers
```

### Conversation Memory

```
SHORT_TERM_MEMORY_WINDOW=10  # Remember last 10 messages
```

## 📊 Monitoring (with LangSmith)

If you added your LangSmith API key:

1. Visit [LangSmith](https://smith.langchain.com/)
2. Find your project (default name: "rag-chatbot")
3. View detailed traces of:
   - Every question asked
   - Documents retrieved
   - LLM calls made
   - Response generation process
   - Performance metrics

## 🐛 Troubleshooting

### "No documents retrieved"
- Make sure documents uploaded successfully
- Try broader or more specific questions
- Check if document content is text-based (not scanned images)

### Slow responses
- First response initializes models (10-20 seconds)
- Subsequent responses are faster
- Consider using gpt-3.5-turbo for speed

### Upload fails
- Check file format (PDF, TXT, MD only)
- Ensure file isn't corrupted
- Large files may take time to process

### API errors
- Verify API keys are correct in Secrets
- Check OpenAI account has available credits
- Try the fallback model if configured

## 📖 API Access

Your chatbot also has a REST API. Test it with curl:

```bash
# Create a new chat session
curl -X POST https://your-repl-url.replit.app/api/sessions/new

# Send a message
curl -X POST https://your-repl-url.replit.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?", "session_id": "your-session-id"}'

# List documents
curl https://your-repl-url.replit.app/api/documents

# Health check
curl https://your-repl-url.replit.app/api/health
```

## 🚀 Next Steps

1. **Add more documents** - Build your knowledge base
2. **Experiment with questions** - Test different query types
3. **Review conversations** - See how context improves answers
4. **Monitor with LangSmith** - Understand system behavior
5. **Customize models** - Fine-tune for your use case
6. **Deploy** - Click "Publish" to make it publicly accessible

## 💡 Use Cases

- **Research Assistant**: Upload papers, ask questions about findings
- **Documentation Helper**: Upload manuals, get instant answers
- **Study Companion**: Upload textbooks, quiz yourself
- **Content Analyzer**: Upload articles, extract insights
- **Code Documentation**: Upload README files, understand projects

## 🎓 Learn More

- See `README.md` for full technical documentation
- Check `replit.md` for architecture details
- Review the code in `src/` to understand implementation

---

**Ready to get started?** Add your OpenAI API key and upload your first document!

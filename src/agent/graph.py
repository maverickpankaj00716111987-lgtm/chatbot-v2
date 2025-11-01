from typing import TypedDict, List, Dict, Annotated, Sequence
import operator
import logging
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.utils.llm_manager import LLMManager
from src.vector_store.simple_vector_store import SimpleVectorStore
from src.database.connection import get_db
from src.database.models import AgentState as AgentStateModel
from src.models.config import settings
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    retrieved_docs: List[Dict]
    context: str
    response: str
    session_id: str
    metadata: Dict


class RAGAgent:
    def __init__(self, llm_manager: LLMManager, vector_store: SimpleVectorStore):
        self.llm_manager = llm_manager
        self.vector_store = vector_store
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate", self._generate_response)
        workflow.add_node("log_state", self._log_state)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "log_state")
        workflow.add_edge("log_state", END)
        
        return workflow.compile()
    
    def _retrieve_documents(self, state: AgentState) -> Dict:
        logger.info(f"Retrieving documents for query: {state['query'][:100]}...")
        
        try:
            query_embedding = self.llm_manager.generate_embedding(state["query"])
            
            results = self.vector_store.search(query_embedding, k=settings.top_k_docs)
            
            retrieved_docs = []
            for doc, score, metadata in results:
                retrieved_docs.append({
                    "content": doc,
                    "score": score,
                    "metadata": metadata
                })
            
            context = "\n\n".join([
                f"Document {i+1} (relevance: {doc['score']:.2f}):\n{doc['content']}"
                for i, doc in enumerate(retrieved_docs)
            ])
            
            if settings.log_all_states:
                self._persist_state(state["session_id"], "retrieve", {
                    "query": state["query"],
                    "retrieved_count": len(retrieved_docs),
                    "top_score": retrieved_docs[0]["score"] if retrieved_docs else 0
                })
            
            return {
                "retrieved_docs": retrieved_docs,
                "context": context,
                "metadata": {**state.get("metadata", {}), "retrieval_count": len(retrieved_docs)}
            }
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return {
                "retrieved_docs": [],
                "context": "",
                "metadata": {**state.get("metadata", {}), "retrieval_error": str(e)}
            }
    
    def _generate_response(self, state: AgentState) -> Dict:
        logger.info("Generating response...")
        
        try:
            messages = []
            
            system_message = {
                "role": "system",
                "content": """You are a helpful AI assistant with access to a document knowledge base. 
Use the provided context to answer user questions accurately. If the context doesn't contain 
relevant information, acknowledge this and provide the best answer you can based on your knowledge.
Always cite which documents you're referencing when applicable."""
            }
            messages.append(system_message)
            
            for msg in state.get("messages", [])[-settings.short_term_memory_window:]:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})
            
            if state.get("context"):
                context_message = {
                    "role": "user",
                    "content": f"Relevant context from documents:\n\n{state['context']}\n\nUser question: {state['query']}"
                }
            else:
                context_message = {
                    "role": "user",
                    "content": f"User question: {state['query']}"
                }
            
            if messages[-1]["role"] == "user":
                messages[-1] = context_message
            else:
                messages.append(context_message)
            
            response = self.llm_manager.generate_response(messages)
            
            if settings.log_all_states:
                self._persist_state(state["session_id"], "generate", {
                    "query": state["query"],
                    "response_length": len(response),
                    "context_used": bool(state.get("context"))
                })
            
            return {
                "response": response,
                "messages": [AIMessage(content=response)]
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_response = "I apologize, but I encountered an error generating a response. Please try again."
            return {
                "response": error_response,
                "messages": [AIMessage(content=error_response)],
                "metadata": {**state.get("metadata", {}), "generation_error": str(e)}
            }
    
    def _log_state(self, state: AgentState) -> Dict:
        logger.info("Logging final state...")
        
        if settings.log_all_states:
            self._persist_state(state["session_id"], "complete", {
                "query": state["query"],
                "response": state["response"],
                "documents_used": len(state.get("retrieved_docs", [])),
                "metadata": state.get("metadata", {})
            })
        
        return {}
    
    def _persist_state(self, session_id: str, state_name: str, state_data: Dict):
        try:
            with get_db() as db:
                agent_state = AgentStateModel(
                    session_id=session_id,
                    state_name=state_name,
                    state_data=state_data,
                    timestamp=datetime.utcnow(),
                    execution_metadata={}
                )
                db.add(agent_state)
                db.commit()
        except Exception as e:
            logger.error(f"Error persisting state: {e}")
    
    def run(self, query: str, session_id: str, conversation_history: List[BaseMessage] = None) -> Dict:
        logger.info(f"Running agent for session: {session_id}")
        
        initial_state = {
            "messages": conversation_history or [],
            "query": query,
            "retrieved_docs": [],
            "context": "",
            "response": "",
            "session_id": session_id,
            "metadata": {"start_time": datetime.utcnow().isoformat()}
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            return {
                "response": final_state.get("response", ""),
                "retrieved_docs": final_state.get("retrieved_docs", []),
                "metadata": final_state.get("metadata", {})
            }
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request.",
                "retrieved_docs": [],
                "metadata": {"error": str(e)}
            }

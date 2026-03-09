from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging
import json
from functools import wraps
import hashlib
from typing import Dict, List, Tuple, Optional

# -------------------------
# Load Environment Variables
# -------------------------
load_dotenv()

# -------------------------
# Setup Logging
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------
# Import Centralized LLM Config
# -------------------------
from llm_config import call_llm, LLMConfig, get_llm_client

# Validate LLM configuration on startup
LLMConfig.validate()

# -------------------------
# Flask Setup
# -------------------------
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# Embedding Model
# -------------------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# -------------------------
# In-Memory Data Store
# -------------------------
class ConversationManager:
    """Manages conversations and their associated data"""
    def __init__(self):
        self.conversations: Dict[str, dict] = {}
        self.file_index: Dict[str, dict] = {}
    
    def create_conversation(self, conversation_id: str):
        """Create a new conversation"""
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "files": {},
            "metadata": {
                "total_tokens": 0,
                "query_count": 0,
            }
        }
    
    def add_file_to_conversation(self, conversation_id: str, file_id: str, file_data: dict):
        """Add file to conversation"""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        self.conversations[conversation_id]["files"][file_id] = file_data
        self.file_index[file_id] = conversation_id
    
    def get_conversation(self, conversation_id: str):
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: dict = None):
        """Add message to conversation"""
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversations[conversation_id]["messages"].append(message)
        return message

# Initialize conversation manager
conversation_manager = ConversationManager()

# Store index in memory with conversation-based isolation
conversation_indices: Dict[str, dict] = {}

# -------------------------
# Helper Functions
# -------------------------
def hash_file(file_data: bytes) -> str:
    """Generate hash of file content"""
    return hashlib.md5(file_data).hexdigest()

def extract_text_from_pdf(filepath: str) -> Tuple[str, int]:
    """Extract text from PDF file"""
    text = ""
    page_count = 0
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise
    
    return text, page_count

def create_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Create overlapping chunks from text"""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def retry_on_error(max_retries: int = 3):
    """Decorator for retry logic"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            return None
        return wrapper
    return decorator

# -------------------------
# Endpoints
# -------------------------

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_conversations": len(conversation_manager.conversations)
    })

@app.route("/upload", methods=["POST"])
@retry_on_error(max_retries=3)
def upload():
    """Upload and process PDF file"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        conversation_id = request.form.get("conversationId", str(uuid.uuid4()))
        
        if not file.filename.endswith(".pdf"):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        # Ensure conversation exists
        if conversation_id not in conversation_manager.conversations:
            conversation_manager.create_conversation(conversation_id)
        
        # Save file
        file_id = str(uuid.uuid4())
        filepath = os.path.join(UPLOAD_FOLDER, f"{file_id}_{file.filename}")
        file.save(filepath)
        
        logger.info(f"Uploaded file: {filepath}")
        
        # Extract text
        text, page_count = extract_text_from_pdf(filepath)
        
        if not text.strip():
            os.remove(filepath)
            return jsonify({"error": "PDF file is empty or unreadable"}), 400
        
        # Create chunks
        chunks = create_chunks(text)
        
        if not chunks:
            os.remove(filepath)
            return jsonify({"error": "No content extracted from PDF"}), 400
        
        # Generate embeddings
        embeddings = embedding_model.encode(chunks)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))
        
        # Store in conversation
        file_data = {
            "id": file_id,
            "name": file.filename,
            "filepath": filepath,
            "size": os.path.getsize(filepath),
            "page_count": page_count,
            "chunk_count": len(chunks),
            "hash": hash_file(open(filepath, "rb").read()),
            "uploaded_at": datetime.now().isoformat(),
            "status": "ready"
        }
        
        conversation_indices[conversation_id] = {
            "index": index,
            "chunks": chunks,
            "files": [file_data],
            "embeddings": embeddings
        }
        
        conversation_manager.add_file_to_conversation(conversation_id, file_id, file_data)
        
        logger.info(f"Successfully processed file: {file.filename} ({len(chunks)} chunks)")
        
        return jsonify({
            "message": "File uploaded and indexed successfully",
            "file_id": file_id,
            "conversation_id": conversation_id,
            "chunks": len(chunks),
            "pages": page_count,
            "source": filepath
        }), 200
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"Upload failed: {str(e)}"
        }), 500

@app.route("/chat", methods=["POST"])
@retry_on_error(max_retries=2)
def chat():
    """Process chat message"""
    try:
        data = request.json
        question = data.get("message", "").strip()
        conversation_id = data.get("conversationId", str(uuid.uuid4()))
        
        if not question:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Create conversation if not exists
        if conversation_id not in conversation_manager.conversations:
            conversation_manager.create_conversation(conversation_id)
        
        # Check if conversation has files
        if conversation_id not in conversation_indices:
            return jsonify({
                "response": "Please upload a document first to ask questions.",
                "error": True
            }), 400
        
        # Retrieve context
        conv_data = conversation_indices[conversation_id]
        query_embedding = embedding_model.encode([question])
        
        # Search index
        D, I = conv_data["index"].search(np.array(query_embedding), k=5)
        
        # Get relevant chunks
        sources = []
        context_chunks = []
        for idx in I[0]:
            if idx < len(conv_data["chunks"]):
                chunk = conv_data["chunks"][idx]
                context_chunks.append(chunk)
                sources.append({
                    "file": conv_data["files"][0]["name"] if conv_data["files"] else "Unknown",
                    "chunk_index": int(idx),
                    "confidence": float(1 / (1 + D[0][I.tolist()[0].index(idx)]))
                })
        
        context = "\n\n".join(context_chunks)
        
        # Prepare prompt
        user_prompt = f"""You are a medical health assistant specialized in analyzing health reports and documents.

Context from document:
```
{context}
```

User Question: {question}

Please provide a detailed and accurate answer based ONLY on the information in the document. If the information is not in the document, clearly state that.

Answer:"""
        
        # Get response from LLM
        answer = call_llm(user_prompt)
        
        # Add messages to conversation
        conversation_manager.add_message(
            conversation_id, 
            "user", 
            question,
            {"type": "query"}
        )
        
        conversation_manager.add_message(
            conversation_id,
            "assistant",
            answer,
            {
                "type": "response",
                "sources": sources,
                "model": "local-llm",
                "tokens": len(answer.split())
            }
        )
        
        # Update conversation metadata
        conversation_manager.conversations[conversation_id]["metadata"]["query_count"] += 1
        conversation_manager.conversations[conversation_id]["metadata"]["total_tokens"] += len(answer.split())
        
        logger.info(f"Processed query for conversation {conversation_id}")
        
        return jsonify({
            "response": answer,
            "sources": sources,
            "model": "local-llm",
            "tokens": len(answer.split()),
            "conversation_id": conversation_id
        }), 200
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({
            "response": f"Error processing query: {str(e)}",
            "error": True
        }), 500

@app.route("/conversation/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id: str):
    """Get conversation details"""
    try:
        conv = conversation_manager.get_conversation(conversation_id)
        if not conv:
            return jsonify({"error": "Conversation not found"}), 404
        
        return jsonify(conv), 200
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/conversation/<conversation_id>/messages", methods=["GET"])
def get_messages(conversation_id: str):
    """Get messages from conversation"""
    try:
        conv = conversation_manager.get_conversation(conversation_id)
        if not conv:
            return jsonify({"error": "Conversation not found"}), 404
        
        return jsonify({
            "conversation_id": conversation_id,
            "messages": conv["messages"],
            "message_count": len(conv["messages"])
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/conversation/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        if conversation_id in conversation_manager.conversations:
            # Delete associated files
            conv = conversation_manager.conversations[conversation_id]
            for file_id, file_data in conv["files"].items():
                if os.path.exists(file_data["filepath"]):
                    os.remove(file_data["filepath"])
            
            # Delete from managers
            del conversation_manager.conversations[conversation_id]
            if conversation_id in conversation_indices:
                del conversation_indices[conversation_id]
            
            logger.info(f"Deleted conversation: {conversation_id}")
            return jsonify({"message": "Conversation deleted successfully"}), 200
        
        return jsonify({"error": "Conversation not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/conversation/<conversation_id>/export", methods=["GET"])
def export_conversation(conversation_id: str):
    """Export conversation as JSON"""
    try:
        conv = conversation_manager.get_conversation(conversation_id)
        if not conv:
            return jsonify({"error": "Conversation not found"}), 404
        
        return jsonify(conv), 200
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/stats", methods=["GET"])
def get_stats():
    """Get application statistics"""
    try:
        total_conversations = len(conversation_manager.conversations)
        total_messages = sum(
            len(conv["messages"]) 
            for conv in conversation_manager.conversations.values()
        )
        total_files = sum(
            len(conv["files"]) 
            for conv in conversation_manager.conversations.values()
        )
        
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_files": total_files,
            "active_indices": len(conversation_indices)
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["OPTIONS"])
def chat_options():
    """Handle CORS preflight"""
    response = app.make_default_options_response()
    headers = response.headers
    headers["Access-Control-Allow-Origin"] = "*"
    headers["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET"
    headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.after_request
def after_request(response):
    """Add CORS headers to response"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS,DELETE"
    return response

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting GutBot server...")
    app.run(port=5000, debug=False, threaded=True)

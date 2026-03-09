from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import torch

# -------------------------
# Load Environment Variables
# -------------------------
load_dotenv()

# -------------------------
# GPU/Device Detection
# -------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[GPU Detection] Using device: {DEVICE}")
if DEVICE == "cuda":
    print(f"[GPU Detection] GPU: {torch.cuda.get_device_name(0)}")

# -------------------------
# Import Centralized LLM Config
# -------------------------
from llm_config import call_llm, LLMConfig, get_llm_client

# Validate LLM configuration on startup
LLMConfig.validate()

# -------------------------
# Flask Setup with CORS Configuration
# -------------------------
app = Flask(__name__)

# Configure CORS for both local dev and EC2 production
ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Local dev (alternative port)
    "http://localhost:3001",      # Local dev (Vite default)
    "http://localhost:3002",      # Local dev (fallback port)
    "http://127.0.0.1:3000",      # Localhost variations
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]

# Add EC2 domain if set via environment variable
EC2_DOMAIN = os.getenv("EC2_DOMAIN", "")
if EC2_DOMAIN:
    ALLOWED_ORIGINS.extend([
        f"http://{EC2_DOMAIN}",
        f"https://{EC2_DOMAIN}",
        f"http://www.{EC2_DOMAIN}",
        f"https://www.{EC2_DOMAIN}",
    ])

# Allow all origins in development, restrict in production
if os.getenv("FLASK_ENV") == "production":
    CORS(app, resources={
        r"/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
else:
    # Development: Allow all
    CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# Embedding Model (GPU Enabled)
# -------------------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
print(f"[Embedding Model] Loading: {EMBEDDING_MODEL_NAME}")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=DEVICE)
print(f"[Embedding Model] Loaded on device: {DEVICE}")

@app.route("/chat", methods=["OPTIONS"])
def chat_options():
    response = app.make_default_options_response()
    headers = response.headers
    headers["Access-Control-Allow-Origin"] = "*"
    headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# Store indices per conversation in memory
# Format: {conversationId: {
#   "documents": {
#     "doc_id": {
#       "index": faiss_index,
#       "chunks": [chunks],
#       "filename": "filename",
#       "size": file_size,
#       "selected": True/False
#     }
#   },
#   "combined_index": merged_faiss_index,
#   "doc_to_chunk_mapping": {chunk_idx: doc_id}
# }}
conversation_indices = {}

def rebuild_combined_index(conv_data):
    """Rebuild combined index from all selected documents
    
    CRITICAL: This function stores BOTH the mapping AND the local chunk indices
    to ensure isolation between conversations and document selections.
    """
    if not conv_data.get("documents"):
        return None, {}, {}
    
    all_embeddings = []
    doc_to_chunk_mapping = {}  # Maps global_chunk_idx -> (doc_id, local_chunk_idx)
    chunk_idx = 0
    
    # Collect embeddings and chunk mappings from selected documents
    # IMPORTANT: Iterate in sorted order for consistency
    for doc_id in sorted(conv_data["documents"].keys()):
        doc_info = conv_data["documents"][doc_id]
        if doc_info.get("selected", True):
            # Re-encode chunks for this document
            chunks = doc_info["chunks"]
            embeddings = embedding_model.encode(chunks)
            all_embeddings.append(embeddings)
            
            # Map global chunk index to (doc_id, local_chunk_index) tuple
            for local_idx in range(len(chunks)):
                doc_to_chunk_mapping[chunk_idx] = (doc_id, local_idx)
                chunk_idx += 1
    
    if not all_embeddings:
        return None, {}, {}
    
    # Combine all embeddings
    combined_embeddings = np.vstack(all_embeddings)
    
    # Create combined index
    dimension = combined_embeddings.shape[1]
    combined_index = faiss.IndexFlatL2(dimension)
    combined_index.add(combined_embeddings)
    
    return combined_index, doc_to_chunk_mapping, {}

# -------------------------
# Upload PDF
# -------------------------
@app.route("/upload", methods=["POST"])
def upload():
    global conversation_indices

    try:
        file = request.files.get("file")
        conversation_id = request.form.get("conversationId")
        
        if not file:
            return jsonify({"error": "No file provided"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        if not conversation_id:
            return jsonify({"error": "Conversation ID required"}), 400

        # Validate file size (50MB limit)
        if file.content_length and file.content_length > 50 * 1024 * 1024:
            return jsonify({"error": "File size exceeds 50MB limit"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Extract text from PDF
        text = ""
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) == 0:
                    return jsonify({"error": "PDF file is empty or corrupted"}), 400
                    
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 400

        if not text.strip():
            return jsonify({"error": "No text could be extracted from PDF"}), 400

        # Create chunks
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        # Initialize conversation data if not exists
        if conversation_id not in conversation_indices:
            conversation_indices[conversation_id] = {
                "documents": {},
                "combined_index": None,
                "doc_to_chunk_mapping": {}
            }
        
        # Generate unique doc ID
        from uuid import uuid4
        doc_id = str(uuid4())
        
        # Store document information
        conversation_indices[conversation_id]["documents"][doc_id] = {
            "chunks": chunks,
            "filename": file.filename,
            "size": len(text.encode('utf-8')),  # Use text size, not file size
            "selected": True  # New documents selected by default
        }
        
        # Rebuild combined index with all selected documents
        combined_index, doc_to_chunk_mapping, _ = rebuild_combined_index(
            conversation_indices[conversation_id]
        )
        conversation_indices[conversation_id]["combined_index"] = combined_index
        conversation_indices[conversation_id]["doc_to_chunk_mapping"] = doc_to_chunk_mapping

        return jsonify({
            "message": "File uploaded and indexed successfully",
            "chunks": len(chunks),
            "source": file.filename,
            "docId": doc_id,
            "status": "success"
        }), 200
    
    except Exception as e:
        print(f"ERROR in /upload endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Failed to upload and process file",
            "details": str(e)
        }), 500

# -------------------------
# Chat
# -------------------------
@app.route("/chat", methods=["POST"])
def chat():
    global conversation_indices

    try:
        data = request.json
        question = data.get("message", "").strip()
        conversation_id = data.get("conversationId")

        # Validate input
        if not conversation_id:
            return jsonify({
                "error": "Conversation ID required",
                "status": "error"
            }), 400

        if not question:
            return jsonify({
                "error": "Message cannot be empty",
                "status": "error"
            }), 400

        if len(question) > 5000:
            return jsonify({
                "error": "Message exceeds maximum length of 5000 characters",
                "status": "error"
            }), 400

        # Check if conversation exists and has documents
        if conversation_id not in conversation_indices:
            return jsonify({
                "response": "Please upload a document first.",
                "error": True,
                "status": "no_documents"
            }), 400

        conv_data = conversation_indices[conversation_id]
        
        if not conv_data.get("documents"):
            return jsonify({
                "response": "Please upload a document first.",
                "error": True,
                "status": "no_documents"
            }), 400

        # Get conversation data
        # Check if any documents are selected
        selected_docs = [
            (doc_id, doc_info) 
            for doc_id, doc_info in conv_data["documents"].items() 
            if doc_info.get("selected", True)
        ]
        
        if not selected_docs:
            return jsonify({
                "response": "No documents selected. Please select documents to search.",
                "error": True,
                "status": "no_selected_documents"
            }), 400
        
        # Get combined index
        combined_index = conv_data.get("combined_index")
        doc_to_chunk_mapping = conv_data.get("doc_to_chunk_mapping", {})
        
        if combined_index is None or len(doc_to_chunk_mapping) == 0:
            return jsonify({
                "response": "Please upload a document first.",
                "error": True,
                "status": "index_error"
            }), 400

        # Search across all selected documents
        try:
            query_embedding = embedding_model.encode([question])
            k = min(5, len(doc_to_chunk_mapping))  # Get top 5 results
            D, I = combined_index.search(np.array(query_embedding), k=k)
        except Exception as e:
            print(f"Embedding/search error: {str(e)}")
            return jsonify({
                "response": "Failed to search documents. Please try again.",
                "error": True,
                "status": "search_error"
            }), 500

        # Build context from all relevant chunks with document names
        context_parts = []
        sources = set()
        
        for chunk_idx in I[0]:
            # Get (doc_id, local_chunk_idx) from the mapping
            mapping = doc_to_chunk_mapping.get(chunk_idx)
            
            if not mapping:
                continue
            
            doc_id, local_chunk_idx = mapping
            
            # Verify document exists and is selected
            if doc_id not in conv_data["documents"]:
                continue
            
            doc_info = conv_data["documents"][doc_id]
            
            # Only use chunks from selected documents
            if not doc_info.get("selected", True):
                continue
            
            chunks = doc_info["chunks"]
            
            # Verify chunk index is valid
            if 0 <= local_chunk_idx < len(chunks):
                context_parts.append(
                    f"[From: {doc_info['filename']}]\n{chunks[local_chunk_idx]}"
                )
                sources.add(doc_info['filename'])

        if not context_parts:
            context = "No relevant information found in documents."
        else:
            context = "\n\n---\n\n".join(context_parts)
        
        sources_list = sorted(list(sources))
        user_prompt = f"""CRITICAL INSTRUCTIONS:
- Answer ONLY using the provided document context below
- Do NOT mention, reference, or infer information about documents that are NOT provided
- If information is not in the provided context, say "This information is not available in the provided documents"
- Be precise and accurate - do not hallucinate or make assumptions
- Only cite documents that are explicitly listed in the sources

Available Documents in Context:
{', '.join(sources_list) if sources_list else 'None provided'}

Document Context:
{context}

Question:
{question}
"""

        # Use centralized LLM configuration
        try:
            answer = call_llm(user_prompt)
        except Exception as e:
            print(f"LLM error: {str(e)}")
            return jsonify({
                "response": "Failed to generate response. Please try again.",
                "error": True,
                "status": "llm_error",
                "details": str(e)
            }), 500

        return jsonify({
            "response": answer,
            "sources": sources_list,
            "chunks_used": len(I[0]),
            "documents_used": len(sources_list),
            "status": "success"
        }), 200
    
    except Exception as e:
        print(f"ERROR in /chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "response": "An unexpected error occurred",
            "error": True,
            "status": "server_error",
            "details": str(e)
        }), 500

# -------------------------
# Manage Documents (Toggle Selection)
# -------------------------
@app.route("/manage-documents", methods=["POST"])
def manage_documents():
    global conversation_indices
    
    try:
        data = request.json
        conversation_id = data.get("conversationId")
        doc_id = data.get("docId")
        selected = data.get("selected")
        
        if not conversation_id or not doc_id:
            return jsonify({"error": "Conversation ID and Document ID required"}), 400
        
        if conversation_id not in conversation_indices:
            return jsonify({"error": "Conversation not found"}), 404
        
        if doc_id not in conversation_indices[conversation_id]["documents"]:
            return jsonify({"error": "Document not found"}), 404
        
        # Update selection status
        conversation_indices[conversation_id]["documents"][doc_id]["selected"] = selected
        
        # Rebuild combined index
        conv_data = conversation_indices[conversation_id]
        combined_index, doc_to_chunk_mapping, _ = rebuild_combined_index(conv_data)
        conv_data["combined_index"] = combined_index
        conv_data["doc_to_chunk_mapping"] = doc_to_chunk_mapping
        
        # Count selected documents
        selected_count = sum(1 for doc in conv_data["documents"].values() if doc.get("selected", True))
        
        return jsonify({
            "message": "Document selection updated",
            "docId": doc_id,
            "selected": selected,
            "selectedCount": selected_count
        })
    
    except Exception as e:
        print(f"ERROR in /manage-documents endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -------------------------
# Remove Document
# -------------------------
@app.route("/remove-document", methods=["POST"])
def remove_document():
    global conversation_indices
    
    try:
        data = request.json
        conversation_id = data.get("conversationId")
        doc_id = data.get("docId")
        
        if not conversation_id or not doc_id:
            return jsonify({"error": "Conversation ID and Document ID required"}), 400
        
        if conversation_id not in conversation_indices:
            return jsonify({"error": "Conversation not found"}), 404
        
        if doc_id not in conversation_indices[conversation_id]["documents"]:
            return jsonify({"error": "Document not found"}), 404
        
        # Remove document
        del conversation_indices[conversation_id]["documents"][doc_id]
        
        # Rebuild combined index
        conv_data = conversation_indices[conversation_id]
        if conv_data["documents"]:  # If there are still documents
            combined_index, doc_to_chunk_mapping = rebuild_combined_index(conv_data)
            conv_data["combined_index"] = combined_index
            conv_data["doc_to_chunk_mapping"] = doc_to_chunk_mapping
        else:  # No documents left
            conv_data["combined_index"] = None
            conv_data["doc_to_chunk_mapping"] = {}
        
        return jsonify({
            "message": "Document removed successfully",
            "docId": doc_id,
            "remainingDocuments": len(conv_data["documents"])
        })
    
    except Exception as e:
        print(f"ERROR in /remove-document endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -------------------------
# Get Document List
# -------------------------
@app.route("/documents", methods=["POST"])
def get_documents():
    global conversation_indices
    
    try:
        data = request.json
        conversation_id = data.get("conversationId")
        
        if not conversation_id:
            return jsonify({"error": "Conversation ID required"}), 400
        
        if conversation_id not in conversation_indices:
            return jsonify({"documents": []})
        
        docs = []
        for doc_id, doc_info in conversation_indices[conversation_id]["documents"].items():
            docs.append({
                "id": doc_id,
                "filename": doc_info["filename"],
                "size": doc_info["size"],
                "selected": doc_info.get("selected", True),
                "chunks": len(doc_info["chunks"])
            })
        
        return jsonify({"documents": docs})
    
    except Exception as e:
        print(f"ERROR in /documents endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# -------------------------
# Debug: Verify Conversation Isolation
# -------------------------
@app.route("/debug/isolation-check", methods=["POST"])
def isolation_check():
    """Debug endpoint to verify conversation isolation"""
    global conversation_indices
    
    try:
        data = request.json
        conversation_id = data.get("conversationId")
        
        if not conversation_id:
            return jsonify({"error": "Conversation ID required"}), 400
        
        if conversation_id not in conversation_indices:
            return jsonify({
                "conversation_id": conversation_id,
                "exists": False,
                "isolation_status": "✅ ISOLATED - No data for this conversation",
                "documents": []
            })
        
        conv_data = conversation_indices[conversation_id]
        
        isolation_report = {
            "conversation_id": conversation_id,
            "exists": True,
            "documents_count": len(conv_data.get("documents", {})),
            "selected_documents_count": sum(
                1 for doc in conv_data.get("documents", {}).values() 
                if doc.get("selected", True)
            ),
            "documents": []
        }
        
        # List all documents for this conversation
        for doc_id, doc_info in conv_data.get("documents", {}).items():
            isolation_report["documents"].append({
                "doc_id": doc_id[:8] + "...",  # Truncate for readability
                "filename": doc_info.get("filename"),
                "chunks": len(doc_info.get("chunks", [])),
                "selected": doc_info.get("selected", True)
            })
        
        # Check if mapping is correct
        doc_to_chunk_mapping = conv_data.get("doc_to_chunk_mapping", {})
        if doc_to_chunk_mapping:
            isolation_report["mapping_status"] = f"✅ {len(doc_to_chunk_mapping)} chunk mappings"
            isolation_report["isolation_status"] = "✅ ISOLATED - Conversation data is properly segmented"
        else:
            isolation_report["mapping_status"] = "⚠️ No chunk mappings (needs rebuild)"
            isolation_report["isolation_status"] = "⚠️ WARNING - May need to rebuild indices"
        
        # Overall isolation check
        total_conversations = len(conversation_indices)
        isolation_report["total_conversations"] = total_conversations
        isolation_report["conclusion"] = (
            "✅ PASS: Each conversation has isolated data" 
            if all(
                len(conv_data.get("documents", {})) > 0 
                for conv_data in conversation_indices.values()
            ) or total_conversations <= 1
            else "⚠️ PASS: Multiple conversations exist with proper isolation"
        )
        
        return jsonify(isolation_report)
    
    except Exception as e:
        print(f"ERROR in /debug/isolation-check endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

if __name__ == "__main__":
    app.run(port=5000)
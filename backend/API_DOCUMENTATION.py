"""
GutBot API Documentation

This document provides detailed information about all available API endpoints
and their usage for the GutBot application.
"""

# ============================================================================
# BASE URL
# ============================================================================
BASE_URL = "http://localhost:5000"

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

"""
1. GET /health
   Description: Health check endpoint to verify server is running
   
   Response (200):
   {
       "status": "healthy",
       "timestamp": "2024-03-03T10:30:00.000Z",
       "active_conversations": 5
   }
   
   Usage:
   - Can be used for monitoring and load balancing
   - No authentication required
   - Returns quickly with server status
"""

"""
2. GET /stats
   Description: Get application statistics
   
   Response (200):
   {
       "timestamp": "2024-03-03T10:30:00.000Z",
       "total_conversations": 10,
       "total_messages": 150,
       "total_files": 15,
       "active_indices": 8
   }
   
   Usage:
   - Get overview of application activity
   - Monitor resource usage
   - Track user engagement
"""

# ============================================================================
# FILE UPLOAD ENDPOINTS
# ============================================================================

"""
3. POST /upload
   Description: Upload and process a PDF file
   
   Request:
   - Method: POST
   - Content-Type: multipart/form-data
   - Body:
     * file: Binary PDF file (required)
     * conversationId: UUID string (optional, generated if not provided)
   
   Response (200):
   {
       "message": "File uploaded and indexed successfully",
       "file_id": "uuid-string",
       "conversation_id": "uuid-string",
       "chunks": 125,
       "pages": 15,
       "source": "uploads/file-path.pdf"
   }
   
   Response (400):
   {
       "error": "Only PDF files are supported" or other error message
   }
   
   Response (500):
   {
       "error": "Upload failed: error details"
   }
   
   Usage:
   - Upload medical documents, reports, or PDFs
   - Documents are automatically indexed for semantic search
   - Supports files up to 50MB
   - Each upload is associated with a conversation
   
   Example:
   ```python
   import requests
   
   files = {'file': open('report.pdf', 'rb')}
   data = {'conversationId': 'my-conversation-id'}
   response = requests.post('http://localhost:5000/upload', 
                           files=files, data=data)
   ```
"""

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

"""
4. POST /chat
   Description: Send a message and get AI response
   
   Request:
   - Method: POST
   - Content-Type: application/json
   - Body:
     {
         "message": "What is the diagnosis from this report?",
         "conversationId": "uuid-string",
         "files": [array of file objects]
     }
   
   Response (200):
   {
       "response": "The diagnosis shows...",
       "sources": [
           {
               "file": "report.pdf",
               "chunk_index": 5,
               "confidence": 0.92
           }
       ],
       "model": "local-llm",
       "tokens": 250,
       "conversation_id": "uuid-string"
   }
   
   Response (400):
   {
       "error": "Please upload a document first to ask questions.",
       "error": true
   }
   
   Response (500):
   {
       "response": "Error processing query: error details",
       "error": true
   }
   
   Usage:
   - Ask questions about uploaded documents
   - Get answers based on document content only
   - Includes source attribution for transparency
   - Supports multi-turn conversations
   
   Example:
   ```python
   import requests
   import json
   
   payload = {
       "message": "What are the key findings?",
       "conversationId": "my-conversation-id"
   }
   response = requests.post('http://localhost:5000/chat',
                           json=payload)
   ```
"""

"""
5. OPTIONS /chat
   Description: CORS preflight request handler
   
   Response (200):
   - Handles browser CORS preflight checks
   - No body required
"""

# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

"""
6. GET /conversation/<conversation_id>
   Description: Get conversation details including all messages
   
   Request:
   - Method: GET
   - URL: /conversation/uuid-string
   
   Response (200):
   {
       "id": "uuid-string",
       "created_at": "2024-03-03T10:00:00.000Z",
       "messages": [
           {
               "id": "uuid-string",
               "role": "user",
               "content": "question",
               "timestamp": "2024-03-03T10:00:10.000Z",
               "metadata": {}
           },
           ...
       ],
       "files": {
           "file-id": {
               "id": "uuid-string",
               "name": "report.pdf",
               "size": 1024000,
               "page_count": 10,
               "chunk_count": 50,
               ...
           }
       },
       "metadata": {
           "total_tokens": 2000,
           "query_count": 5
       }
   }
   
   Response (404):
   {
       "error": "Conversation not found"
   }
   
   Usage:
   - Retrieve full conversation history
   - Access all messages and context
   - Check metadata and statistics
"""

"""
7. GET /conversation/<conversation_id>/messages
   Description: Get only messages from a conversation
   
   Response (200):
   {
       "conversation_id": "uuid-string",
       "messages": [...],
       "message_count": 15
   }
   
   Usage:
   - Lighter weight than full conversation endpoint
   - Just get message history without files
"""

"""
8. DELETE /conversation/<conversation_id>
   Description: Delete a conversation and associated files
   
   Request:
   - Method: DELETE
   - URL: /conversation/uuid-string
   
   Response (200):
   {
       "message": "Conversation deleted successfully"
   }
   
   Response (404):
   {
       "error": "Conversation not found"
   }
   
   Usage:
   - Permanently delete conversation and files
   - Free up storage space
   - Irreversible operation
"""

"""
9. GET /conversation/<conversation_id>/export
   Description: Export conversation as JSON
   
   Response (200):
   - Returns complete conversation data in JSON format
   - Same structure as GET /conversation/<conversation_id>
   
   Usage:
   - Export conversation for backup
   - Transfer conversation data
   - External processing or analysis
"""

# ============================================================================
# ERROR HANDLING
# ============================================================================

"""
Error Response Format:

All error responses follow this format:
{
    "error": "Human-readable error message",
    "status": HTTP_STATUS_CODE
}

Common HTTP Status Codes:
- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Internal Server Error

Common Error Messages:
- "No file provided"
- "Only PDF files are supported"
- "File size exceeds maximum limit (50MB)"
- "Please upload a document first"
- "Conversation not found"
- "Invalid conversation ID"
"""

# ============================================================================
# REQUEST EXAMPLES
# ============================================================================

"""
Example 1: Complete Workflow

1. Upload a document
   POST /upload
   Content-Type: multipart/form-data
   
   Response:
   {
       "file_id": "abc123",
       "conversation_id": "conv456",
       "chunks": 50
   }

2. Ask a question
   POST /chat
   {
       "message": "What is the patient's diagnosis?",
       "conversationId": "conv456"
   }
   
   Response:
   {
       "response": "Based on the report, the patient shows...",
       "sources": [{"file": "report.pdf", "chunk_index": 5}]
   }

3. Continue conversation
   POST /chat
   {
       "message": "What are the recommended treatments?",
       "conversationId": "conv456"
   }
   
   Response:
   {
       "response": "The recommended treatments include..."
   }

4. Export conversation
   GET /conversation/conv456/export
   
   Response: JSON file with complete conversation history

5. Delete conversation
   DELETE /conversation/conv456
   
   Response: {"message": "Conversation deleted successfully"}
"""

# ============================================================================
# RATE LIMITING & QUOTAS
# ============================================================================

"""
Rate Limiting:
- 100 requests per 60 seconds per IP address
- Applies to all endpoints
- Rate limit info in response headers

File Upload Limits:
- Maximum file size: 50MB
- Supported formats: PDF only
- Concurrent uploads: Limited by system resources

Processing Limits:
- Maximum response time: 60 seconds
- Maximum message length: 5000 characters
- Chunk size: 500 characters with 50 character overlap
"""

# ============================================================================
# AUTHENTICATION
# ============================================================================

"""
Current Implementation:
- No authentication required
- All endpoints are publicly accessible
- Add authentication/authorization as needed for production

Future Enhancements:
- API key authentication
- JWT token-based auth
- Per-user conversation isolation
- Rate limiting per user
"""

# ============================================================================
# CACHING STRATEGY
# ============================================================================

"""
Caching:
- Embeddings are cached for uploaded files
- Conversation data cached in memory
- Consider Redis for distributed caching
- TTL: Configurable (default: 1 hour)
"""

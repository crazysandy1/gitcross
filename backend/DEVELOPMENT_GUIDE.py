"""
GUTBOT - PRODUCTION-GRADE ENTERPRISE CHATBOT
Development & Deployment Guide

This guide covers installation, configuration, development, and deployment
of the GutBot AI-powered health analysis chatbot.
"""

# ============================================================================
# SYSTEM REQUIREMENTS
# ============================================================================

REQUIREMENTS = """
Minimum System Requirements:
- Python 3.8 or higher
- Node.js 16 or higher
- RAM: 4GB minimum (8GB recommended)
- Storage: 10GB free space
- GPU: Optional (CUDA 11.0+ for faster processing)

Operating Systems:
- Windows 10/11
- macOS 10.14+
- Ubuntu 18.04+
- Any Linux distribution with Python 3.8+
"""

# ============================================================================
# INSTALLATION GUIDE
# ============================================================================

INSTALLATION = """
Step 1: Clone Repository
    git clone https://github.com/yourusername/gutbot.git
    cd gutbot

Step 2: Set Up Backend
    2a. Create Python Virtual Environment
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\\Scripts\\activate

    2b. Install Backend Dependencies
        pip install -r requirements_backend.txt

    2c. Configure Environment
        Copy .env.example to .env
        Update .env with your configuration

Step 3: Set Up Frontend
    3a. Navigate to Frontend Directory
        cd frontend

    3b. Install Frontend Dependencies
        npm install

    3c. Configure Environment
        Copy .env.example to .env
        Update VITE_API_URL if needed

    3d. Return to Root Directory
        cd ..

Step 4: Verify Installation
    python --version  # Should be 3.8+
    npm --version    # Should be 6+
"""

# ============================================================================
# CONFIGURATION GUIDE
# ============================================================================

CONFIGURATION = """
Backend Configuration (.env):

API Configuration:
    FLASK_ENV=development
    FLASK_DEBUG=False
    BACKEND_HOST=0.0.0.0
    BACKEND_PORT=5000
    CORS_ORIGINS=*

File Upload:
    MAX_UPLOAD_SIZE=52428800  # 50MB
    UPLOAD_FOLDER=uploads

LLM Configuration:
    LLM_PROVIDER=local
    LLM_MODEL=local-llm
    LLM_TIMEOUT=60

Processing:
    PDF_CHUNK_SIZE=500
    PDF_CHUNK_OVERLAP=50
    SEARCH_TOP_K=5
    SIMILARITY_THRESHOLD=0.3

Frontend Configuration (.env):
    VITE_API_URL=http://localhost:5000
    VITE_APP_NAME=GutBot
    VITE_DEBUG_MODE=false
"""

# ============================================================================
# RUNNING THE APPLICATION
# ============================================================================

RUNNING = """
Development Mode:

Option 1: Using Start Scripts
    Windows:
        start.bat

    Linux/Mac:
        chmod +x start.sh
        ./start.sh

Option 2: Manual Startup
    Terminal 1 - Backend:
        python app_enhanced.py
        Backend runs on: http://localhost:5000

    Terminal 2 - Frontend:
        cd frontend
        npm run dev
        Frontend runs on: http://localhost:3000

Option 3: Using Docker
    docker-compose up

Verify Installation:
    1. Open browser: http://localhost:3000
    2. Check health: http://localhost:5000/health
    3. Upload a PDF and ask questions
"""

# ============================================================================
# FEATURES IMPLEMENTED
# ============================================================================

FEATURES = """
Core Features:
✓ PDF Document Upload & Processing
✓ Semantic Search using FAISS
✓ AI-Powered Q&A
✓ Conversation Management
✓ Multi-turn Conversations
✓ Source Attribution
✓ Upload Progress Tracking
✓ Error Handling & Retry Logic

User Interface Features:
✓ Modern, Responsive Design
✓ Sidebar Conversation History
✓ File Management
✓ Export Conversations (JSON)
✓ Download Transcripts
✓ Error Messages & Notifications
✓ Loading States
✓ Mobile Friendly

Backend Features:
✓ Centralized Logging
✓ Error Handling with Retry Logic
✓ CORS Support
✓ Health Check Endpoint
✓ Statistics Endpoint
✓ File Hash Verification
✓ Chunk Embeddings Caching
✓ Memory-based Conversation Storage

Production Features:
✓ Configurable Environments
✓ Docker Support
✓ Environment Variables
✓ Comprehensive Logging
✓ API Documentation
✓ Error Boundaries
✓ Request/Response Logging
✓ Rate Limiting Ready
"""

# ============================================================================
# PROJECT STRUCTURE
# ============================================================================

STRUCTURE = """
gutbot/
├── app_enhanced.py              # Enhanced Flask backend
├── llm_config.py               # LLM configuration
├── backend_config.py           # Backend configuration
├── requirements_backend.txt    # Backend dependencies
├── Dockerfile                  # Backend container config
├── docker-compose.yml          # Docker compose setup
├── start.bat                   # Windows startup script
├── start.sh                    # Unix startup script
├── .env.example               # Environment template
├── API_DOCUMENTATION.py       # API reference
│
├── frontend/
│   ├── package.json           # Frontend dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── index.html             # HTML entry point
│   ├── .env.example           # Frontend env template
│   ├── Dockerfile.frontend    # Frontend container
│   └── src/
│       ├── main.jsx           # Application entry
│       ├── App.jsx            # Main component
│       ├── App.css            # Main styles
│       ├── index.css          # Global styles
│       ├── config.js          # Configuration
│       ├── components/
│       │   ├── Header.jsx     # Top navigation
│       │   ├── Sidebar.jsx    # Conversation list
│       │   ├── ChatContainer.jsx # Messages display
│       │   ├── ChatInput.jsx  # Message input
│       │   ├── UploadZone.jsx # File upload
│       │   ├── LoadingSpinner.jsx # Loading state
│       │   ├── ErrorBoundary.jsx  # Error handling
│       │   └── [CSS files]    # Component styles
│       └── utils/
│           ├── api.js         # API calls
│           └── helpers.js     # Utility functions
│
├── uploads/                    # Uploaded files
└── logs/                       # Application logs
"""

# ============================================================================
# DEVELOPMENT WORKFLOW
# ============================================================================

WORKFLOW = """
1. Making Changes
    - Modify component files in frontend/src/
    - Vite will hot-reload automatically
    - Check browser console for errors

2. Testing
    - Test file uploads with sample PDFs
    - Test various questions
    - Check browser console for errors
    - Check backend logs for issues

3. Building for Production
    Frontend:
        cd frontend
        npm run build
        Build output: frontend/dist/

4. Debugging
    Browser DevTools:
        F12 to open dev tools
        Check Console tab for errors
        Check Network tab for API calls

    Backend Logs:
        Running logs in terminal
        Check for ERROR or WARNING messages

5. Performance Optimization
    - Monitor memory usage
    - Check response times
    - Optimize chunk sizes if needed
    - Consider caching strategies
"""

# ============================================================================
# DEPLOYMENT GUIDE
# ============================================================================

DEPLOYMENT = """
Docker Deployment:

1. Build and Run
    docker-compose build
    docker-compose up -d

2. Verify Services
    docker ps
    curl http://localhost:5000/health

3. View Logs
    docker-compose logs -f backend
    docker-compose logs -f frontend

Production Checklist:
    [ ] Set FLASK_ENV=production
    [ ] Disable FLASK_DEBUG
    [ ] Configure proper CORS_ORIGINS
    [ ] Set up proper logging
    [ ] Enable rate limiting
    [ ] Configure database if needed
    [ ] Set up backup strategy
    [ ] Monitor disk space for uploads
    [ ] Enable health checks
    [ ] Set up SSL/HTTPS
    [ ] Configure reverse proxy (nginx/apache)
    [ ] Set up monitoring/alerting
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

TROUBLESHOOTING = """
Common Issues:

1. Backend won't start
    - Check Python version: python --version
    - Check port 5000 is not in use: lsof -i :5000
    - Install dependencies: pip install -r requirements_backend.txt

2. Frontend won't start
    - Check Node version: node --version
    - Clear npm cache: npm cache clean --force
    - Reinstall: npm install

3. Upload fails
    - Check file is PDF format
    - Check file size < 50MB
    - Check backend logs for errors
    - Verify UPLOAD_FOLDER exists

4. Chat response is slow
    - Check backend logs
    - Monitor CPU/RAM usage
    - Check LLM response time
    - Consider larger chunk overlap

5. CORS errors
    - Check CORS_ORIGINS setting
    - Check API_URL in frontend config
    - Verify backend is running

6. File not found errors
    - Ensure uploads/ directory exists
    - Check file permissions
    - Verify file path in logs
"""

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

PERFORMANCE = """
Optimization Tips:

Memory Optimization:
    - Adjust PDF_CHUNK_SIZE based on document type
    - Implement conversation cleanup
    - Use database instead of in-memory storage

Speed Optimization:
    - Reduce PDF_CHUNK_SIZE for faster searching
    - Increase SEARCH_TOP_K if missing relevant info
    - Cache embeddings in database
    - Use GPU for embedding generation

Storage Optimization:
    - Implement file cleanup policy
    - Compress old conversations
    - Archive uploads periodically

Database Optimization (if implemented):
    - Index conversation_id
    - Index message timestamp
    - Index file_id

Scaling Strategies:
    - Use Redis for caching
    - Implement message queues
    - Load balance across multiple instances
    - Use managed database services
"""

# ============================================================================
# SECURITY CONSIDERATIONS
# ============================================================================

SECURITY = """
Security Checklist:

Authentication:
    [ ] Implement user authentication
    [ ] Add API key management
    [ ] Implement JWT tokens
    [ ] Add session management

Authorization:
    [ ] Restrict file access per user
    [ ] Validate conversation ownership
    [ ] Implement role-based access

Data Protection:
    [ ] Encrypt sensitive files
    [ ] Implement HTTPS/SSL
    [ ] Secure password storage
    [ ] Data privacy compliance

Input Validation:
    [ ] Validate file uploads
    [ ] Sanitize user input
    [ ] Prevent injection attacks
    [ ] Rate limiting

Logging & Monitoring:
    [ ] Log security events
    [ ] Monitor for anomalies
    [ ] Set up alerts
    [ ] Regular security audits

Deployment Security:
    [ ] Use environment variables
    [ ] Don't commit secrets
    [ ] Regular updates
    [ ] Security headers
    [ ] CORS policy
"""

# ============================================================================
# MAINTENANCE
# ============================================================================

MAINTENANCE = """
Regular Tasks:

Daily:
    - Monitor error logs
    - Check disk space
    - Monitor API response times

Weekly:
    - Review conversation statistics
    - Check for failed uploads
    - Backup important data

Monthly:
    - Update dependencies
    - Review and optimize chunks
    - Analyze performance metrics
    - Clean up old files

Quarterly:
    - Security audit
    - Performance review
    - Database optimization
    - Capacity planning

Yearly:
    - Major version upgrades
    - Complete security review
    - Disaster recovery testing
    - Architecture assessment
"""

# ============================================================================
# RESOURCES & SUPPORT
# ============================================================================

RESOURCES = """
Documentation:
    - API Documentation: API_DOCUMENTATION.py
    - Backend Config: backend_config.py
    - Frontend Config: frontend/src/config.js

Key Files:
    - Backend Entry: app_enhanced.py
    - Frontend Entry: frontend/src/main.jsx
    - Components: frontend/src/components/

Links:
    - Flask Documentation: https://flask.palletsprojects.com/
    - React Documentation: https://react.dev/
    - FAISS Documentation: https://github.com/facebookresearch/faiss
    - Vite Documentation: https://vitejs.dev/

Common Commands:

Backend:
    python app_enhanced.py          # Run backend
    python -m pytest               # Run tests

Frontend:
    npm run dev                    # Development
    npm run build                  # Build production
    npm run lint                   # Check code quality

Docker:
    docker build -t gutbot .       # Build image
    docker run -p 5000:5000 gutbot # Run container
    docker-compose up              # Full stack
"""

print(__doc__)

"""
GUTBOT - QUICK START GUIDE

Get started with GutBot in 5 minutes!
"""

QUICK_START = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    GUTBOT - QUICK START GUIDE                             ║
║              Production-Grade AI Health Chatbot                            ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: PREREQUISITES CHECK (1 minute)
═══════════════════════════════════════════════════════════════════════════════

Open Terminal/Command Prompt and run:

    python --version      # Should output Python 3.8 or higher
    node --version        # Should output Node.js 16 or higher
    npm --version         # Should output npm 6 or higher

If any command fails:
    • Python: Install from https://www.python.org/
    • Node.js: Install from https://nodejs.org/


STEP 2: SETUP (2 minutes)
═══════════════════════════════════════════════════════════════════════════════

Windows Users:
    1. Navigate to project folder
    2. Double-click start.bat
    3. Wait for both servers to start

Linux/Mac Users:
    1. Navigate to project folder
    2. Run: chmod +x start.sh && ./start.sh
    3. Wait for both servers to start

Docker Users:
    1. Ensure Docker is installed
    2. Run: docker-compose up
    3. Wait for services to start


STEP 3: VERIFY & ACCESS (1 minute)
═══════════════════════════════════════════════════════════════════════════════

Open your browser:

    Frontend:    http://localhost:3000
    Backend:     http://localhost:5000
    Health Check: http://localhost:5000/health

You should see:
    ✓ GutBot interface loaded in browser
    ✓ Health check returns {"status": "healthy"}
    ✓ No errors in browser console (F12)


STEP 4: TEST THE APPLICATION (1 minute)
═══════════════════════════════════════════════════════════════════════════════

1. Upload a PDF Document
   • Click "Upload Your Document" or drag a PDF file
   • Wait for upload to complete
   • See confirmation message

2. Ask a Question
   • Type a question about the document
   • Press Enter or click Send
   • Wait for AI response
   • See sources cited

3. Continue Conversation
   • Ask follow-up questions
   • Chat history is maintained
   • All sessions saved locally


FEATURES TO EXPLORE
═══════════════════════════════════════════════════════════════════════════════

After getting started, try these features:

✓ New Chat
  - Click "➕ New Chat" to start new conversation
  - Each chat maintains separate history
  - Quick organization

✓ Conversation Management
  - View all conversations in sidebar
  - Search by conversation name
  - Delete individual or all conversations

✓ Export & Download
  - Save entire conversation as JSON (💾 button)
  - Download chat transcript as text file (📥 button)
  - Perfect for record keeping

✓ File Information
  - See uploaded documents in conversation
  - View file sizes and page counts
  - Multiple files per conversation

✓ Error Handling
  - Application handles errors gracefully
  - User-friendly error messages
  - Automatic retry on network issues


TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

Problem: Ports already in use
Solution: 
    - Kill existing process on port 5000 or 3000
    - Or change ports in configuration

Problem: "Module not found" errors
Solution:
    - Backend: pip install -r requirements_backend.txt
    - Frontend: npm install

Problem: Upload fails
Solution:
    - Ensure file is PDF format
    - Check file size < 50MB
    - Check backend is running
    - Check browser console for errors

Problem: Slow responses
Solution:
    - Check CPU/RAM usage
    - Restart servers
    - Clear browser cache
    - Check backend logs


KEYBOARD SHORTCUTS
═══════════════════════════════════════════════════════════════════════════════

Enter          - Send message
Shift+Enter    - New line in message
Ctrl+K         - New chat (when implemented)


DEFAULT SETTINGS
═══════════════════════════════════════════════════════════════════════════════

File Upload:
    Max Size: 50 MB
    Format: PDF only
    
Chat:
    Max Message: 5000 characters
    Auto-save: Every message

Search:
    Top Results: 5 chunks per query
    Chunk Size: 500 characters
    Overlap: 50 characters


CONFIGURATION FILES
═══════════════════════════════════════════════════════════════════════════════

Backend (.env):
    BACKEND_PORT=5000
    UPLOAD_FOLDER=uploads
    MAX_UPLOAD_SIZE=52428800  (50MB)

Frontend (frontend/.env):
    VITE_API_URL=http://localhost:5000
    VITE_DEBUG_MODE=false


WHAT'S NEXT?
═══════════════════════════════════════════════════════════════════════════════

1. Basic Usage
   • Upload a PDF
   • Ask questions
   • Explore conversation features

2. Advanced Features
   • Check API_DOCUMENTATION.py for all endpoints
   • Review DEVELOPMENT_GUIDE.py for detailed info
   • Explore backend_config.py for settings

3. Production Deployment
   • Review DEPLOYMENT GUIDE section
   • Configure environment variables
   • Set up Docker/docker-compose
   • Configure SSL/HTTPS
   • Set up monitoring

4. Customization
   • Modify UI colors in CSS files
   • Adjust chunk sizes in backend_config.py
   • Change LLM model settings
   • Add authentication (when needed)


SUPPORT & RESOURCES
═══════════════════════════════════════════════════════════════════════════════

Documentation:
    • DEVELOPMENT_GUIDE.py - Full development guide
    • API_DOCUMENTATION.py - API reference
    • IMPLEMENTATION_SUMMARY.py - Feature overview
    • backend_config.py - Configuration details

File Organization:
    • app_enhanced.py - Main backend
    • frontend/src/ - React components
    • frontend/src/components/ - UI components
    • frontend/src/utils/ - Helper functions

Logs:
    • Backend: Console output in terminal
    • Frontend: Browser console (F12)


QUICK LINKS
═══════════════════════════════════════════════════════════════════════════════

🌐 Frontend: http://localhost:3000
🔧 Backend: http://localhost:5000
❤️ Health: http://localhost:5000/health
📚 API: See API_DOCUMENTATION.py


IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════════════════

✓ All data is stored locally (no cloud)
✓ Conversations are saved in browser localStorage
✓ Files are stored in uploads/ folder
✓ No user login required (optional for production)
✓ All chats visible to user (single browser)


GETTING HELP
═══════════════════════════════════════════════════════════════════════════════

1. Check browser console (F12) for errors
2. Check backend terminal for errors
3. Review error messages in application
4. Check TROUBLESHOOTING section above
5. Review relevant documentation files


═══════════════════════════════════════════════════════════════════════════════

You're all set! 🚀

Start using GutBot now: http://localhost:3000

═══════════════════════════════════════════════════════════════════════════════
"""

print(QUICK_START)

# Debug Guide for Knowledge Base Chatbot

This guide explains how to debug your server using the provided debug configurations.

## Debug Configurations Available

### 1. Local Python Debugging
**File**: `.vscode/launch.json` - "Debug Backend Server"

**How to use:**
1. Open VS Code
2. Go to Run and Debug (Ctrl+Shift+D)
3. Select "Debug Backend Server" from the dropdown
4. Click the green play button or press F5
5. Set breakpoints in your code by clicking on the line numbers
6. The debugger will stop at your breakpoints

**Requirements:**
- PostgreSQL running locally on port 5432
- Environment variables set in `.env` file

### 2. Docker Debugging
**File**: `docker-compose.yml` - "Debug Backend Server (Docker)"

**How to use:**
1. **Option A: Regular server with debug port exposed (Recommended)**
   ```bash
   docker-compose up
   ```
   The server will automatically enable debugpy when `DEBUG=true`
   Then connect debugger to port 5678

2. **Option B: Debug server (waits for debugger)**
   - Uncomment the debug command in `docker-compose.yml`:
     ```yaml
     command: python debug_server.py
     ```
   - Set `DEBUG_WAIT_FOR_ATTACH=true` in environment
   - Start containers:
     ```bash
     docker-compose up
     ```
   - Connect debugger in VS Code

3. In VS Code, go to Run and Debug
4. Select "Debug Backend Server (Docker)" from the dropdown
5. Click the green play button
6. Set breakpoints in your code
7. The debugger will connect to the running container

**Requirements:**
- Docker and Docker Compose installed
- Environment variables set in `.env` file

### 3. Test Script Debugging
**Files**: 
- `backend/test_notion_sync.py` - "Debug Notion Sync"
- `backend/test_vector_search.py` - "Debug Vector Store"

**How to use:**
1. Select the appropriate test configuration
2. Set breakpoints in the test script or the code being tested
3. Run the debugger
4. Step through the code to understand the flow

## Setting Up Environment Variables

Create a `.env` file in the root directory with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/knowledgebase

# Notion (for real testing)
NOTION_TOKEN=your_notion_integration_token
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
NOTION_REDIRECT_URI=http://localhost:3000/auth/notion/callback

# JWT
JWT_SECRET_KEY=your_jwt_secret_key

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key

# Other services (optional)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
RESEND_API_KEY=your_resend_api_key
```

## Debugging Tips

### 1. Setting Breakpoints
- Click on the line number in VS Code to set a breakpoint
- Red dots indicate active breakpoints
- You can set conditional breakpoints by right-clicking on a breakpoint

### 2. Debug Console
- Use the Debug Console to execute Python code in the current context
- Inspect variables and their values
- Execute expressions to test code

### 3. Step Through Code
- **F10**: Step Over (execute current line)
- **F11**: Step Into (enter function calls)
- **Shift+F11**: Step Out (exit current function)
- **F5**: Continue execution

### 4. Inspecting Variables
- Hover over variables to see their values
- Use the Variables panel to see all local variables
- Use the Watch panel to monitor specific expressions

### 5. Debugging the Notion Sync Issue
To debug the current `'str' object is not callable` error:

1. Set a breakpoint in `backend/app/services/postgres_vector_store.py` at line 238
2. Run the "Debug Backend Server" configuration
3. Trigger a Notion sync from the frontend
4. When the breakpoint hits, inspect the variables:
   - Check `chunk["chunk_id"]` - is it a string or integer?
   - Check `chunk` - what does the chunk object look like?
   - Check `i` - what is the loop index?

### 6. Common Debug Scenarios

**Debugging Database Issues:**
- Set breakpoints in `postgres_vector_store.py`
- Check SQL queries and parameters
- Inspect database connection status

**Debugging Embedding Issues:**
- Set breakpoints in `embedding_service.py`
- Check if models are loading correctly
- Inspect embedding generation process

**Debugging Notion API Issues:**
- Set breakpoints in `notion_service.py`
- Check API responses and error handling
- Inspect token validation

## Troubleshooting

### Debugger Not Connecting
- Check if the port 5678 is available
- Ensure the container is running with debug mode
- Verify the path mappings in the launch configuration

### Breakpoints Not Working
- Ensure you're using the correct Python interpreter
- Check if the code is actually being executed
- Verify the file paths match between local and container

### Environment Variables Not Loading
- Check the `.env` file is in the correct location
- Verify the environment variable names match
- Restart the debugger after changing environment variables

## Quick Start Commands

```bash
# Start Docker with debugging enabled
docker-compose up

# Start with debug server (waits for debugger)
# 1. Uncomment command: python debug_server.py in docker-compose.yml
# 2. Set DEBUG_WAIT_FOR_ATTACH=true
# 3. Run: docker-compose up
# 4. Connect debugger in VS Code

# Start local debugging (requires local PostgreSQL)
code . && # Open VS Code, select "Debug Backend Server", press F5

# Test specific functionality
python backend/test_notion_sync.py
python backend/test_vector_search.py
```

## Debugging the Current Issue

To debug the `'str' object is not callable` error:

1. **Set breakpoints** in `postgres_vector_store.py` at:
   - Line 213: `for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):`
   - Line 238: `"chunk_index": chunk["chunk_id"],`

2. **Run the debugger** with "Debug Backend Server"

3. **Trigger a Notion sync** from the frontend

4. **Inspect the variables** when the breakpoint hits:
   - What type is `chunk["chunk_id"]`?
   - What does the `chunk` object contain?
   - Is there a mismatch between expected and actual types?

This will help you identify exactly where the type mismatch is occurring and fix it accordingly.

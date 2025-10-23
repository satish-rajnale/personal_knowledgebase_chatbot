# Notion Authentication Flow Fix

## Problem
The recent changes to route Notion authentication through the backend caused the frontend to not get notified immediately when authentication completes. The backend now handles the redirect URI directly, but the frontend wasn't updated to handle this new flow.

## Root Cause
1. **Backend Changes**: The backend now handles OAuth callbacks directly and redirects to a mobile app URI
2. **Frontend Expectation**: The frontend was still expecting to handle OAuth callbacks in the browser
3. **Missing Polling**: No mechanism for the frontend to detect when authentication completes

## Solution

### 1. Frontend Updates (`frontend/src/App.js`)

#### **Added Redirect Handling**
```javascript
// Handle Notion OAuth redirect from backend (new flow)
useEffect(() => {
  const handleNotionRedirect = async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const status = urlParams.get('status');
    const workspace = urlParams.get('workspace');
    const message = urlParams.get('message');
    
    if (status && !callbackProcessed && !callbackProcessedRef.current) {
      // Handle success/error redirects from backend
      if (status === 'success') {
        // Show success message and refresh user data
      } else if (status === 'error') {
        // Show error message
      }
    }
  };
  
  handleNotionRedirect();
}, [callbackProcessed, refreshUserProfile, refreshUsage]);
```

#### **Added Polling Mechanism**
```javascript
// Polling mechanism for Notion connection status
useEffect(() => {
  let pollInterval;
  
  if (notionAuthInProgress && !callbackProcessed) {
    pollInterval = setInterval(async () => {
      try {
        const profile = await refreshUserProfile();
        
        if (profile?.notion_connected) {
          // Connection detected, show success and stop polling
          setNotionAuthInProgress(false);
          showModal('Notion Connected!', 'Success message', 'success');
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('❌ Polling error:', error);
      }
    }, 2000); // Poll every 2 seconds
  }
  
  return () => {
    if (pollInterval) {
      clearInterval(pollInterval);
    }
  };
}, [notionAuthInProgress, callbackProcessed, refreshUserProfile, refreshUsage]);
```

### 2. Backend Updates

#### **Updated Redirect URLs** (`backend/app/api/routes/auth.py`)
```python
# If successful, redirect to frontend with success status
frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
success_url = f"{frontend_url}?status=success&workspace={result.get('workspace_name', 'Unknown')}"

return RedirectResponse(url=success_url)
```

#### **Added Frontend URL Configuration** (`backend/app/core/config.py`)
```python
FRONTEND_URL: str = "http://localhost:3000"  # Frontend URL for OAuth redirects
```

#### **Updated Docker Configuration**
```yaml
# docker-compose.yml
environment:
  - FRONTEND_URL=http://localhost:3000

# docker-compose.override.yml
environment:
  - FRONTEND_URL=http://localhost:3000
```

## How It Works Now

### 1. **Authentication Flow**
1. User clicks "Connect Notion" in frontend
2. Frontend calls backend to get auth URL
3. User is redirected to Notion OAuth
4. Notion redirects to backend callback endpoint
5. Backend processes the callback and redirects to frontend with status
6. Frontend detects the redirect and shows success/error message

### 2. **Fallback Polling**
1. If redirect doesn't work, frontend starts polling
2. Polls user profile every 2 seconds to check `notion_connected` status
3. When connection is detected, shows success message
4. Stops polling after success or timeout

### 3. **Error Handling**
1. Backend redirects to frontend with error status
2. Frontend shows error message
3. User can retry authentication

## Benefits

1. **Immediate Notification**: Frontend gets notified immediately via redirect
2. **Fallback Support**: Polling ensures connection is detected even if redirect fails
3. **Better UX**: Users see success/error messages immediately
4. **Robust**: Works with both web and mobile app flows
5. **Backward Compatible**: Still supports legacy callback flow

## Testing

### 1. **Test Redirect Flow**
1. Start the application
2. Click "Connect Notion"
3. Complete OAuth flow
4. Verify you're redirected back to frontend with success message

### 2. **Test Polling Flow**
1. Start the application
2. Click "Connect Notion"
3. Complete OAuth flow
4. If redirect doesn't work, verify polling detects the connection

### 3. **Test Error Handling**
1. Start the application
2. Click "Connect Notion"
3. Cancel or fail OAuth flow
4. Verify error message is shown

## Configuration

### Environment Variables
```env
# Backend
FRONTEND_URL=http://localhost:3000

# For production
FRONTEND_URL=https://yourdomain.com
```

### Docker Configuration
```yaml
# docker-compose.yml
environment:
  - FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

### 1. **Frontend Not Getting Notified**
- Check if `FRONTEND_URL` is set correctly
- Verify redirect URL in browser
- Check browser console for errors
- Ensure polling is working

### 2. **Redirect Not Working**
- Check backend logs for redirect errors
- Verify `FRONTEND_URL` configuration
- Test redirect URL manually

### 3. **Polling Not Working**
- Check if `refreshUserProfile` is working
- Verify user profile API endpoint
- Check for network errors

## Future Improvements

1. **WebSocket Support**: Real-time notifications instead of polling
2. **Better Error Messages**: More specific error handling
3. **Retry Logic**: Automatic retry for failed connections
4. **Analytics**: Track authentication success/failure rates

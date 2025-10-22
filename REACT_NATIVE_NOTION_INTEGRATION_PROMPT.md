# React Native Expo Notion OAuth Integration Prompt

## Overview
You need to implement Notion OAuth integration in a React Native Expo app that connects to a FastAPI backend server. The backend already has comprehensive OAuth endpoints set up for mobile apps.

## Backend API Endpoints Available

### 1. Authentication Endpoints
- `POST /auth/anonymous` - Create anonymous user
- `POST /auth/email` - Login/register with email
- `GET /auth/profile` - Get user profile
- `POST /auth/logout` - Logout user

### 2. Notion OAuth Endpoints (Mobile-Specific)
- `POST /auth/notion/authorize/mobile` - Get OAuth URL for mobile
- `GET /auth/notion/callback` - Handle OAuth callback (URL parameters)
- `GET /notion/status` - Check Notion connection status
- `GET /notion/pages` - Get user's Notion pages
- `POST /notion/sync` - Sync specific Notion pages

## Required Dependencies
```bash
npm install expo-auth-session expo-crypto expo-web-browser
```

## Implementation Requirements

### 1. Authentication Context
Create an authentication context that:
- Manages JWT tokens
- Handles anonymous and email login
- Stores user state
- Provides auth methods to components

### 2. Notion OAuth Hook
Create a custom hook `useNotionAuth` that:
- Initiates OAuth flow using `expo-auth-session`
- Handles the callback from Notion
- Sends the authorization code to your backend
- Manages loading and error states
- Returns connection status and methods

### 3. Notion Integration Screen
Create a screen that:
- Shows current Notion connection status
- Provides "Connect Notion" button
- Displays connected workspace name
- Shows list of available Notion pages
- Allows syncing specific pages

### 4. API Service
Create an API service that:
- Handles all backend communication
- Manages JWT token in headers
- Provides typed methods for all endpoints
- Handles error responses properly

## Backend Configuration
The backend expects these environment variables:
```env
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
NOTION_REDIRECT_URI=http://localhost:3000/auth/notion/callback
NOTION_MOBILE_REDIRECT_URI=exp://localhost:19000/--/auth/notion/callback
```

## OAuth Flow Implementation

### Step 1: Get OAuth URL
```javascript
const response = await fetch('http://your-backend-url/auth/notion/authorize/mobile', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json',
  },
});
const { auth_url, state } = await response.json();
```

### Step 2: Start OAuth Session
```javascript
const result = await AuthSession.startAsync({
  authUrl: auth_url,
  returnUrl: makeRedirectUri({
    scheme: 'your-app-scheme',
    path: 'auth/notion/callback'
  }),
});
```

### Step 3: Handle Callback
```javascript
if (result.type === 'success') {
  const { code, state: returnedState } = result.params;
  
  // Send code to backend for token exchange
  const callbackResponse = await fetch('http://your-backend-url/auth/notion/callback', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${userToken}`,
    },
  });
}
```

## Expected API Responses

### OAuth Authorization Response
```json
{
  "auth_url": "https://api.notion.com/v1/oauth/authorize?...",
  "state": "uuid-state-parameter",
  "redirect_uri": "exp://localhost:19000/--/auth/notion/callback",
  "platform": "mobile"
}
```

### OAuth Callback Response
```json
{
  "message": "Notion connected successfully",
  "workspace_name": "My Workspace"
}
```

### Notion Status Response
```json
{
  "oauth_configured": true,
  "user_connected": true,
  "workspace_name": "My Workspace",
  "message": "Connected to Notion workspace: My Workspace"
}
```

### Notion Pages Response
```json
{
  "pages": [
    {
      "id": "page-id",
      "title": "Page Title",
      "url": "https://notion.so/page-id",
      "created_time": "2024-01-01T00:00:00.000Z",
      "last_edited_time": "2024-01-01T00:00:00.000Z"
    }
  ],
  "total": 1
}
```

## Error Handling
Handle these common error scenarios:
- Network connectivity issues
- Invalid or expired JWT tokens
- OAuth flow cancellation
- Backend server errors
- Notion API rate limits

## UI/UX Requirements
- Show loading states during OAuth flow
- Display clear error messages
- Provide retry mechanisms
- Show connection status clearly
- Allow disconnection/reconnection

## Security Considerations
- Validate state parameter to prevent CSRF
- Store JWT tokens securely
- Handle token refresh if needed
- Validate all API responses

## Testing
Test the following scenarios:
- First-time Notion connection
- Reconnection after disconnection
- OAuth flow cancellation
- Network error handling
- Invalid token handling

## File Structure Suggestion
```
src/
├── contexts/
│   └── AuthContext.js
├── hooks/
│   └── useNotionAuth.js
├── services/
│   └── api.js
├── screens/
│   └── NotionIntegrationScreen.js
└── components/
    └── NotionConnectionCard.js
```

## Additional Notes
- The backend supports both web and mobile redirect URIs
- OAuth callbacks can be handled via both GET and POST methods
- The backend automatically tries both redirect URIs during token exchange
- User tokens are stored per user in the database
- The backend includes comprehensive error handling and logging

## Success Criteria
- User can connect their Notion workspace
- Connection status is displayed correctly
- User can view their Notion pages
- User can sync specific pages
- Error states are handled gracefully
- OAuth flow works reliably on both iOS and Android

Implement this integration following React Native and Expo best practices, with proper error handling, loading states, and user feedback throughout the OAuth flow.

import React, { useState, useEffect, useRef } from 'react';
import ChatInterface from './components/ChatInterface';
import FileUpload from './components/FileUpload';
import NotionSync from './components/NotionSync';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import ContactForm from './components/ContactForm';
import Modal from './components/Modal';
import Snackbar from './components/Snackbar';
import { ChatProvider } from './context/ChatContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { authAPI } from './services/api';
import { MessageCircle, Upload, Database, Settings, User, Mail } from 'lucide-react';

function AppContent() {
  const { user, loading, refreshUsage, refreshUserProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('chat');
  const [isLoading, setIsLoading] = useState(false);
  const [notionTabHighlight, setNotionTabHighlight] = useState(false);
  const [callbackProcessed, setCallbackProcessed] = useState(false);
  
  // Notion OAuth state management
  const [notionAuthInProgress, setNotionAuthInProgress] = useState(false);
  const [notionAuthError, setNotionAuthError] = useState(null);
  const [notionAuthRetryCount, setNotionAuthRetryCount] = useState(0);
  const MAX_RETRY_ATTEMPTS = 3;
  const OAUTH_TIMEOUT = 300000; // 5 minutes timeout
  const callbackProcessedRef = useRef(false);
  
  // Modal and Snackbar state
  const [modal, setModal] = useState({ isOpen: false, title: '', message: '', type: 'info' });
  const [snackbar, setSnackbar] = useState({ isOpen: false, message: '', type: 'info' });

  // Listen for custom event to switch to Notion tab
  useEffect(() => {
    const handleSwitchToNotionTab = (event) => {
      console.log('🔄 Switching to Notion tab:', event.detail);
      console.log('📊 Current active tab:', activeTab);
      setActiveTab('notion');
      setNotionTabHighlight(true);
      console.log('✅ Tab switched to notion');
      
      // Remove highlight after animation
      setTimeout(() => {
        setNotionTabHighlight(false);
      }, 2000);
    };

    window.addEventListener('switchToNotionTab', handleSwitchToNotionTab);
    
    return () => {
      window.removeEventListener('switchToNotionTab', handleSwitchToNotionTab);
    };
  }, [activeTab]);

  // Handle Notion OAuth callback with retry logic
  useEffect(() => {
    const handleNotionCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      
      if (code && state && !callbackProcessed && !notionAuthInProgress && !callbackProcessedRef.current) {
        console.log('🔄 Processing Notion OAuth callback...');
        console.log(`📊 Retry attempt: ${notionAuthRetryCount + 1}/${MAX_RETRY_ATTEMPTS}`);
        
        callbackProcessedRef.current = true; // Mark as processed immediately
        setCallbackProcessed(true); // Mark as processed immediately
        setNotionAuthInProgress(true);
        setNotionAuthError(null);
        setIsLoading(true);
        
        try {
          console.log('📝 Calling backend callback with code:', code.substring(0, 10) + '...');
          console.log('🔐 State:', state);
          
          // Exchange code for token using authAPI
          const response = await authAPI.notionCallback(code, state);
          console.log('📡 Backend response:', response);
          console.log('📡 Response status:', response.status);
          console.log('📡 Response data:', response.data);
          
          if (response.status === 200) {
            const result = response.data;
            console.log('✅ Notion connected successfully:', result);
            
            // Clear URL parameters and route to main dashboard
            window.history.replaceState({}, document.title, '/');
            
            // Reset OAuth state
            setNotionAuthInProgress(false);
            setNotionAuthError(null);
            setNotionAuthRetryCount(0);
            
            // Switch to main dashboard tab to show the user they're back
            setActiveTab('dashboard');
            
            // Show success message only if we have a valid result and haven't shown it yet
            if (result && (result.message || result.workspace_name)) {
              const message = result.message || 'Notion connected successfully!';
              const workspaceName = result.workspace_name || 'Unknown';
              
              // Only show modal if we haven't already shown one for this session
              if (!sessionStorage.getItem('notion_success_alert_shown')) {
                sessionStorage.setItem('notion_success_alert_shown', 'true');
                showModal(
                  'Notion Connected Successfully!',
                  `${message}\n\nWorkspace: ${workspaceName}\n\nYou can now sync your Notion pages and chat with your content!`,
                  'success'
                );
                
                // Clear the flag after 5 seconds to allow future modals
                setTimeout(() => {
                  sessionStorage.removeItem('notion_success_alert_shown');
                }, 5000);
              } else {
                console.log('✅ Success modal already shown, skipping duplicate');
              }
            } else {
              console.warn('⚠️ Empty or invalid result received:', result);
            }
            
            // Refresh user data to get updated notion_connected status
            try {
              await refreshUserProfile();
              await refreshUsage();
            } catch (error) {
              console.warn('Failed to refresh user data:', error);
            }
          } else {
            throw new Error(response.data?.detail || response.data?.message || 'Unknown error');
          }
        } catch (error) {
          console.error('❌ Notion callback error:', error);
          const errorMessage = error.response?.data?.detail || error.message || 'Network error';
          
          // Check if we should retry
          if (notionAuthRetryCount < MAX_RETRY_ATTEMPTS) {
            console.log(`🔄 Retrying... Attempt ${notionAuthRetryCount + 1}/${MAX_RETRY_ATTEMPTS}`);
            setNotionAuthRetryCount(prev => prev + 1);
            setNotionAuthError(`Failed to connect Notion: ${errorMessage}. Retrying...`);
            
            // Wait 2 seconds before retry
            setTimeout(() => {
              setCallbackProcessed(false); // Allow retry
              setNotionAuthInProgress(false);
              callbackProcessedRef.current = false; // Reset the ref for retry
            }, 2000);
          } else {
            // Max retries reached
            setNotionAuthInProgress(false);
            setNotionAuthError(`Failed to connect Notion after ${MAX_RETRY_ATTEMPTS} attempts: ${errorMessage}`);
            showSnackbar(`Failed to connect Notion after ${MAX_RETRY_ATTEMPTS} attempts: ${errorMessage}`, 'error');
          }
        } finally {
          setIsLoading(false);
        }
      }
    };

    handleNotionCallback();
  }, [callbackProcessed, notionAuthInProgress, notionAuthRetryCount]); // Include all relevant dependencies

  // Handle Notion OAuth redirect from backend (new flow)
  useEffect(() => {
    const handleNotionRedirect = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const status = urlParams.get('status');
      const workspace = urlParams.get('workspace');
      const message = urlParams.get('message');
      
      // Handle direct redirect from backend
      if (status && !callbackProcessed && !callbackProcessedRef.current) {
        console.log('🔄 Processing Notion OAuth redirect...');
        console.log(`📊 Status: ${status}`);
        
        callbackProcessedRef.current = true;
        setCallbackProcessed(true);
        
        // Clear URL parameters
        window.history.replaceState({}, document.title, '/');
        
        if (status === 'success') {
          console.log('✅ Notion connected successfully via redirect');
          setNotionAuthInProgress(false);
          setNotionAuthError(null);
          setNotionAuthRetryCount(0);
          
          // Switch to dashboard tab
          setActiveTab('dashboard');
          
          // Show success message
          const successMessage = `Notion connected successfully! Connected to workspace: ${workspace || 'Unknown'}`;
          showModal(
            'Notion Connected!',
            successMessage,
            'success'
          );
          
          // Refresh user profile and usage stats
          try {
            await refreshUserProfile();
            await refreshUsage();
            console.log('✅ User profile and usage stats refreshed');
          } catch (error) {
            console.error('❌ Failed to refresh user data:', error);
          }
          
          return;
        } else if (status === 'error') {
          console.error('❌ Notion connection failed via redirect');
          setNotionAuthInProgress(false);
          setNotionAuthError(message || 'Failed to connect to Notion');
          
          // Show error message
          showSnackbar(message || 'Failed to connect to Notion. Please try again.', 'error');
          
          return;
        }
      }
    };
    
    handleNotionRedirect();
  }, [callbackProcessed, refreshUserProfile, refreshUsage]);

  // Polling mechanism for Notion connection status
  useEffect(() => {
    let pollInterval;
    
    if (notionAuthInProgress && !callbackProcessed) {
      console.log('🔄 Starting Notion connection polling...');
      
      pollInterval = setInterval(async () => {
        try {
          console.log('🔍 Polling for Notion connection status...');
          const profile = await refreshUserProfile();
          
          if (profile?.notion_connected) {
            console.log('✅ Notion connection detected via polling');
            setNotionAuthInProgress(false);
            setNotionAuthError(null);
            setNotionAuthRetryCount(0);
            setCallbackProcessed(true);
            callbackProcessedRef.current = true;
            
            // Switch to dashboard tab
            setActiveTab('dashboard');
            
            // Show success message
            showModal(
              'Notion Connected!',
              'Notion connected successfully! You can now sync your pages and chat with your content.',
              'success'
            );
            
            // Refresh usage stats
            try {
              await refreshUsage();
            } catch (error) {
              console.error('❌ Failed to refresh usage stats:', error);
            }
            
            // Clear polling
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

  // Auto-reset OAuth state after timeout
  useEffect(() => {
    let timeoutId;
    
    if (notionAuthInProgress) {
      timeoutId = setTimeout(() => {
        console.log('⏰ OAuth timeout reached, resetting state...');
        setNotionAuthInProgress(false);
        setNotionAuthError('OAuth process timed out. Please try again.');
        setNotionAuthRetryCount(0);
        setCallbackProcessed(false);
        callbackProcessedRef.current = false;
      }, OAUTH_TIMEOUT);
    }
    
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [notionAuthInProgress]);

  // Cleanup session storage on component unmount
  useEffect(() => {
    return () => {
      sessionStorage.removeItem('notion_success_alert_shown');
    };
  }, []);

  // Helper functions for notifications
  const showModal = (title, message, type = 'info') => {
    setModal({ isOpen: true, title, message, type });
  };

  const hideModal = () => {
    setModal({ isOpen: false, title: '', message: '', type: 'info' });
  };

  const showSnackbar = (message, type = 'info') => {
    setSnackbar({ isOpen: true, message, type });
  };

  const hideSnackbar = () => {
    setSnackbar({ isOpen: false, message: '', type: 'info' });
  };

  // Function to reset OAuth state manually
  const resetNotionAuthState = () => {
    console.log('🔄 Manually resetting Notion OAuth state...');
    setNotionAuthInProgress(false);
    setNotionAuthError(null);
    setNotionAuthRetryCount(0);
    setCallbackProcessed(false);
    callbackProcessedRef.current = false; // Reset the ref
    // Clear any success alert flags
    sessionStorage.removeItem('notion_success_alert_shown');
  };

  const tabs = [
    { id: 'chat', label: 'Chat', icon: MessageCircle },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'notion', label: 'Notion', icon: Database },
    { id: 'dashboard', label: 'Dashboard', icon: User },
    { id: 'contact', label: 'Contact', icon: Mail },
  ];

  // Show loading screen while auth is initializing
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!user) {
    return <Login />;
  }

  return (
    <ChatProvider>
      <div className="min-h-screen bg-gray-50">
        <Header />
        
        <main className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Tab Navigation */}
          <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm mb-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'bg-primary-600 text-white'
                      : tab.id === 'notion' && notionTabHighlight
                      ? 'bg-yellow-100 text-yellow-800 border-2 border-yellow-400'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={18} />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="animate-fade-in">
            {activeTab === 'chat' && <ChatInterface />}
            {activeTab === 'upload' && <FileUpload />}
            {activeTab === 'notion' && (
              <NotionSync 
                notionAuthInProgress={notionAuthInProgress}
                notionAuthError={notionAuthError}
                notionAuthRetryCount={notionAuthRetryCount}
                resetNotionAuthState={resetNotionAuthState}
                showSnackbar={showSnackbar}
              />
            )}
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'contact' && <ContactForm />}
          </div>
        </main>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
              <span className="text-gray-700">Processing...</span>
            </div>
          </div>
        )}

        {/* Modal */}
        <Modal
          isOpen={modal.isOpen}
          onClose={hideModal}
          title={modal.title}
          message={modal.message}
          type={modal.type}
        />

        {/* Snackbar */}
        <Snackbar
          isOpen={snackbar.isOpen}
          onClose={hideSnackbar}
          message={snackbar.message}
          type={snackbar.type}
        />
      </div>
    </ChatProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <AppContent />
      </ChatProvider>
    </AuthProvider>
  );
}

export default App; 
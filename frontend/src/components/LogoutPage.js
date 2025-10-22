import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, CheckCircle, AlertCircle } from 'lucide-react';

function LogoutPage() {
  const { logout, user } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [hasLoggedOut, setHasLoggedOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    
    // Simulate a brief delay for better UX
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Perform logout
    logout();
    setHasLoggedOut(true);
    setIsLoggingOut(false);
    
    // Redirect to login after a moment
    setTimeout(() => {
      window.location.reload();
    }, 2000);
  };

  useEffect(() => {
    // Auto-logout after 5 seconds if user doesn't confirm
    const timer = setTimeout(() => {
      if (!hasLoggedOut && !isLoggingOut) {
        handleLogout();
      }
    }, 5000);

    return () => clearTimeout(timer);
  }, [hasLoggedOut, isLoggingOut]);

  if (hasLoggedOut) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Logged Out Successfully</h2>
            <p className="text-gray-600 mb-6">
              Your session has been cleared. You will be redirected to the login page shortly.
            </p>
            <div className="animate-pulse">
              <div className="h-2 bg-gray-200 rounded-full mb-2"></div>
              <div className="h-2 bg-gray-200 rounded-full w-3/4 mx-auto"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
        <div className="text-center">
          <div className="bg-red-100 p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <LogOut className="h-8 w-8 text-red-600" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Confirm Logout</h2>
          
          <p className="text-gray-600 mb-6">
            Are you sure you want to logout? This will clear your session and you'll need to log in again.
          </p>

          {user && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600 mb-1">Current User:</p>
              <p className="font-medium text-gray-900">
                {user.email || 'Anonymous User'}
              </p>
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={() => window.history.back()}
              disabled={isLoggingOut}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors duration-200 disabled:opacity-50"
            >
              Cancel
            </button>
            
            <button
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="flex-1 px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors duration-200 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {isLoggingOut ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Logging out...</span>
                </>
              ) : (
                <>
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </>
              )}
            </button>
          </div>

          <div className="mt-4 text-xs text-gray-500">
            <p>You will be automatically logged out in 5 seconds if you don't confirm.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LogoutPage; 
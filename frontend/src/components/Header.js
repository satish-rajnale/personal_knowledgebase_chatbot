import React, { useState, useEffect } from 'react';
import { Brain, Github, User, LogOut, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Modal from './Modal';

function Header() {
  const { user, usage, logout } = useAuth();
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isUsageRefreshing, setIsUsageRefreshing] = useState(false);

  // Listen for usage refresh events
  useEffect(() => {
    const handleUsageRefreshStart = () => {
      setIsUsageRefreshing(true);
    };

    const handleUsageRefreshEnd = () => {
      setIsUsageRefreshing(false);
    };

    // Listen for custom events
    window.addEventListener('usage-refresh-start', handleUsageRefreshStart);
    window.addEventListener('usage-refresh-end', handleUsageRefreshEnd);

    return () => {
      window.removeEventListener('usage-refresh-start', handleUsageRefreshStart);
      window.removeEventListener('usage-refresh-end', handleUsageRefreshEnd);
    };
  }, []);

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                AI Knowledge Assistant
              </h1>
              <p className="text-sm text-gray-600">
                Multi-user SaaS with Notion integration
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {user && usage && (
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <User className="h-4 w-4" />
                  <span>{user.email || 'Anonymous'}</span>
                </div>
                <div className="flex items-center space-x-1">
                  {isUsageRefreshing ? (
                    <RefreshCw className="h-3 w-3 animate-spin text-gray-400" />
                  ) : (
                    <span className="transition-all duration-200 ease-in-out">
                      {usage.remaining_queries}
                    </span>
                  )}
                  <span>queries left</span>
                </div>
              </div>
            )}
            
            <a
              href="https://github.com/satish-rajnale/peronal_knowledgebase_chatbot"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-gray-900 transition-colors duration-200"
            >
              <Github className="h-5 w-5" />
            </a>
            
            {user && (
              <button
                onClick={() => setShowLogoutModal(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors duration-200"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            )}
          </div>
        </div>
      </div>
      
      {/* Logout Confirmation Modal */}
      <Modal
        isOpen={showLogoutModal}
        onClose={() => setShowLogoutModal(false)}
        title="Confirm Logout"
        message="Are you sure you want to logout? Your session will be cleared and you'll need to log in again."
        type="warning"
        showCloseButton={true}
        actions={[
          {
            label: 'Cancel',
            onClick: () => setShowLogoutModal(false),
            variant: 'secondary'
          },
          {
            label: 'Logout',
            onClick: () => {
              setShowLogoutModal(false);
              logout();
            },
            variant: 'danger'
          }
        ]}
      />
    </header>
  );
}

export default Header; 
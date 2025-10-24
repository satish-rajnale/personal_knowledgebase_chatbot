import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { notionAPI, authAPI } from '../services/api';
import { 
  User, 
  Database, 
  BarChart3, 
  Clock, 
  MessageSquare, 
  Settings, 
  LogOut,
  ExternalLink,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

const Dashboard = () => {
  const { user, usage, logout, refreshUsage } = useAuth();
  const [notionPages, setNotionPages] = useState([]);
  const [notionDatabases, setNotionDatabases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedPages, setSelectedPages] = useState([]);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user?.notion_connected) {
      loadNotionData();
    }
  }, [user]);

  const loadNotionData = async () => {
    setLoading(true);
    try {
      const [pagesResponse, databasesResponse] = await Promise.all([
        notionAPI.getPages(),
        notionAPI.getDatabases()
      ]);
      setNotionPages(pagesResponse.pages || []);
      setNotionDatabases(databasesResponse.databases || []);
    } catch (error) {
      console.error('Failed to load Notion data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncPages = async () => {
    if (selectedPages.length === 0) return;
    
    setSyncing(true);
    try {
      await notionAPI.syncNotion(selectedPages);
      await refreshUsage();
      setSelectedPages([]);
      // Show success message
    } catch (error) {
      console.error('Failed to sync pages:', error);
      // Show error message
    } finally {
      setSyncing(false);
    }
  };

  const togglePageSelection = (pageId) => {
    setSelectedPages(prev => 
      prev.includes(pageId) 
        ? prev.filter(id => id !== pageId)
        : [...prev, pageId]
    );
  };

  const handleConnectNotion = () => {
    console.log('🔗 Connect Notion button clicked!');
    
    // Redirect to the Notion tab where the user can connect
    // We'll use a custom event to trigger the Notion tab
    const event = new CustomEvent('switchToNotionTab', { 
      detail: { action: 'connect' } 
    });
    console.log('📡 Dispatching switchToNotionTab event:', event.detail);
    window.dispatchEvent(event);
    console.log('✅ Event dispatched successfully');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getUsagePercentage = () => {
    if (!usage) return 0;
    // Handle unlimited queries (when limit is disabled)
    if (usage.daily_limit === 0 || usage.remaining_queries === -1) return 0;
    return Math.round((usage.daily_query_count / usage.daily_limit) * 100);
  };

  const getUsageColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (!user) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Profile & Usage */}
        <div className="lg:col-span-1 space-y-6">
          {/* User Profile Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-4">
              <div className="bg-primary-100 p-3 rounded-full">
                <User className="h-6 w-6 text-primary-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900">
                  {user.email || 'Anonymous User'}
                </h3>
                <p className="text-sm text-gray-500">
                  Member since {formatDate(user.created_at)}
                </p>
              </div>
              <button
                onClick={logout}
                className="text-gray-400 hover:text-gray-600"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Usage Statistics */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Usage Today</h3>
              <button
                onClick={refreshUsage}
                className="text-primary-600 hover:text-primary-700"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
            
            {usage && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Queries Used</span>
                  <span className={`text-sm font-medium ${getUsageColor()}`}>
                    {usage.daily_limit === 0 || usage.remaining_queries === -1 
                      ? `${usage.daily_query_count} (Unlimited)` 
                      : `${usage.daily_query_count} / ${usage.daily_limit}`}
                  </span>
                </div>
                
                {usage.daily_limit === 0 || usage.remaining_queries === -1 ? (
                  <div className="w-full bg-green-200 rounded-full h-2">
                    <div className="h-2 rounded-full bg-green-500 w-full" />
                  </div>
                ) : (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        getUsagePercentage() >= 90 ? 'bg-red-500' :
                        getUsagePercentage() >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(getUsagePercentage(), 100)}%` }}
                    />
                  </div>
                )}
                
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Total Queries</span>
                  <span className="font-medium">{usage.total_queries}</span>
                </div>
                
                {usage.remaining_queries === 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <div className="flex items-center">
                      <AlertCircle className="h-4 w-4 text-red-400 mr-2" />
                      <span className="text-sm text-red-600">
                        Daily limit reached. Try again tomorrow.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Notion Connection Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Database className="h-5 w-5 text-gray-600" />
              <h3 className="text-lg font-medium text-gray-900">Notion Integration</h3>
            </div>
            
            {user.notion_connected ? (
              <div className="space-y-3">
                <div className="flex items-center text-green-600">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  <span className="text-sm font-medium">Connected</span>
                </div>

                {user.notion_workspace_name && (
                  <p className="text-sm text-gray-600">
                    Workspace: {user.notion_workspace_name}
                  </p>
                )}
                <button
                  onClick={() => window.location.href = '/notion'}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Manage Pages →
                </button>
              </div>
            ) : (
              <div className="space-y-3">

                <div className="flex items-center text-gray-500">
                  <XCircle className="h-4 w-4 mr-2" />
                  <span className="text-sm">Not Connected</span>
                </div>
                <p className="text-sm text-gray-600">
                  Connect your Notion workspace to sync your knowledge.
                </p>
                {error && (
                  <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                    {error}
                  </div>
                )}
                <button
                  onClick={handleConnectNotion}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Connect Notion →
                </button>
                

              </div>
            )}
          </div>
        </div>

        {/* Notion Content */}
        <div className="lg:col-span-2 space-y-6">
          {user.notion_connected ? (
            <>
              {/* Pages Section */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900">Notion Pages</h3>
                    <button
                      onClick={loadNotionData}
                      disabled={loading}
                      className="text-primary-600 hover:text-primary-700 disabled:opacity-50"
                    >
                      <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                  </div>
                </div>
                
                <div className="p-6">
                  {loading ? (
                    <div className="flex items-center justify-center py-8">
                      <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  ) : notionPages.length > 0 ? (
                    <div className="space-y-3">
                      {notionPages.map((page) => (
                        <div
                          key={page.id}
                          className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                          <input
                            type="checkbox"
                            checked={selectedPages.includes(page.id)}
                            onChange={() => togglePageSelection(page.id)}
                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                          />
                          <div className="flex-1">
                            <h4 className="text-sm font-medium text-gray-900">
                              {page.title}
                            </h4>
                            <p className="text-xs text-gray-500">
                              Last edited: {formatDate(page.last_edited_time)}
                            </p>
                          </div>
                          <a
                            href={page.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </div>
                      ))}
                      
                      {selectedPages.length > 0 && (
                        <div className="pt-4 border-t border-gray-200">
                          <button
                            onClick={handleSyncPages}
                            disabled={syncing}
                            className="w-full flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                          >
                            {syncing ? (
                              <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                            ) : (
                              <Database className="h-4 w-4 mr-2" />
                            )}
                            Sync {selectedPages.length} Selected Page{selectedPages.length !== 1 ? 's' : ''}
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">No pages found in your Notion workspace.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Databases Section */}
              {notionDatabases.length > 0 && (
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900">Notion Databases</h3>
                  </div>
                  
                  <div className="p-6">
                    <div className="space-y-3">
                      {notionDatabases.map((database) => (
                        <div
                          key={database.id}
                          className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg"
                        >
                          <div className="flex-1">
                            <h4 className="text-sm font-medium text-gray-900">
                              {database.title}
                            </h4>
                            <p className="text-xs text-gray-500">
                              Last edited: {formatDate(database.last_edited_time)}
                            </p>
                          </div>
                          <a
                            href={database.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Connect Your Notion Workspace
              </h3>
              <p className="text-gray-500 mb-6">
                Connect your Notion workspace to start syncing your knowledge and chatting with your documents.
              </p>
              <button 
                onClick={handleConnectNotion}
                className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
              >
                Connect Notion
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 
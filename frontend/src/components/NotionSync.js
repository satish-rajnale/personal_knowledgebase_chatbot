import React, { useState, useEffect } from 'react';
import { notionAPI } from '../services/api';
import { Database, RefreshCw, CheckCircle, AlertCircle, Settings, ExternalLink } from 'lucide-react';

function NotionSync() {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [lastSync, setLastSync] = useState(null);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const statusData = await notionAPI.getStatus();
      setStatus(statusData);
    } catch (err) {
      setError('Failed to check Notion status');
      console.error('Status check error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    setError(null);
    
    try {
      const result = await notionAPI.syncNotion();
      setLastSync(new Date());
      
      // Show success message
      setTimeout(() => {
        setLastSync(null);
      }, 5000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to sync Notion');
    } finally {
      setIsSyncing(false);
    }
  };

  const getStatusIcon = () => {
    if (isLoading) {
      return <RefreshCw className="h-5 w-5 text-gray-400 animate-spin" />;
    }
    
    if (status?.configured) {
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
    
    return <AlertCircle className="h-5 w-5 text-red-600" />;
  };

  const getStatusText = () => {
    if (isLoading) return 'Checking status...';
    if (status?.configured) return 'Connected';
    return 'Not configured';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Notion Integration</h2>
          <p className="text-sm text-gray-600">
            Sync your Notion workspace content to your knowledgebase
          </p>
        </div>
        <button
          onClick={checkStatus}
          disabled={isLoading}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Status Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Database className="h-6 w-6 text-primary-600" />
            <div>
              <h3 className="font-medium text-gray-900">Connection Status</h3>
              <p className="text-sm text-gray-600">Notion API integration</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="text-sm font-medium">{getStatusText()}</span>
          </div>
        </div>

        {status && (
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${status.token_configured ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-sm">API Token: {status.token_configured ? 'Configured' : 'Missing'}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${status.database_configured ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-sm">Database ID: {status.database_configured ? 'Configured' : 'Missing'}</span>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm text-gray-700">{status.message}</p>
            </div>
          </div>
        )}
      </div>

      {/* Sync Button */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium text-gray-900 mb-1">Sync Content</h3>
            <p className="text-sm text-gray-600">
              Import all pages from your Notion database
            </p>
          </div>
          <button
            onClick={handleSync}
            disabled={!status?.configured || isSyncing}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isSyncing ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Database className="h-4 w-4" />
            )}
            <span>{isSyncing ? 'Syncing...' : 'Sync Now'}</span>
          </button>
        </div>

        {lastSync && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-800">
                Successfully synced at {lastSync.toLocaleTimeString()}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <div>
              <p className="text-red-800 font-medium">Error</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Setup Instructions */}
      {!status?.configured && (
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Settings className="h-5 w-5 text-primary-600" />
            <h3 className="font-medium text-gray-900">Setup Instructions</h3>
          </div>
          
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">1. Create a Notion Integration</h4>
              <ol className="list-decimal list-inside space-y-1 text-gray-600 ml-4">
                <li>Go to <a href="https://www.notion.so/my-integrations" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline flex items-center space-x-1">
                  <span>https://www.notion.so/my-integrations</span>
                  <ExternalLink size={12} />
                </a></li>
                <li>Click "New integration"</li>
                <li>Give it a name and select your workspace</li>
                <li>Copy the "Internal Integration Token"</li>
              </ol>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">2. Share Your Database</h4>
              <ol className="list-decimal list-inside space-y-1 text-gray-600 ml-4">
                <li>Open your Notion database</li>
                <li>Click "Share" → "Invite" → Select your integration</li>
                <li>Copy the database ID from the URL</li>
              </ol>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">3. Configure Environment Variables</h4>
              <div className="bg-gray-100 rounded p-3 font-mono text-xs">
                NOTION_TOKEN=secret_your_token_here<br/>
                NOTION_DATABASE_ID=your_database_id
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Database className="h-5 w-5 text-blue-600" />
            </div>
            <h4 className="font-medium text-gray-900">Database Sync</h4>
          </div>
          <p className="text-sm text-gray-600">
            Import all pages and blocks from your Notion database into your knowledgebase
          </p>
        </div>
        
        <div className="card">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <RefreshCw className="h-5 w-5 text-green-600" />
            </div>
            <h4 className="font-medium text-gray-900">Automatic Updates</h4>
          </div>
          <p className="text-sm text-gray-600">
            Sync whenever you want to update your knowledgebase with the latest Notion content
          </p>
        </div>
      </div>
    </div>
  );
}

export default NotionSync; 
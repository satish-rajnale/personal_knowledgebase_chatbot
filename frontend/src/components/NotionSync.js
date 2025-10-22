import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import { notionAPI, authAPI } from "../services/api";
import {
  Database,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Settings,
  Shield,
  ExternalLink,
  Plus,
  Trash2,
  Link,
} from "lucide-react";

function NotionSync({
  notionAuthInProgress = false,
  notionAuthError = null,
  notionAuthRetryCount = 0,
  resetNotionAuthState = null,
  showSnackbar = null,
}) {
  const { user, refreshUsage } = useAuth();
  const [status, setStatus] = useState(null);
  const [pages, setPages] = useState([]);
  const [databases, setDatabases] = useState([]);
  const [selectedPages, setSelectedPages] = useState([]);
  const [selectedDatabases, setSelectedDatabases] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [signingStatus, setSigningStatus] = useState(null);
  const [lastSync, setLastSync] = useState(null);
  const [embeddingsInfo, setEmbeddingsInfo] = useState(null);
  const [isLoadingEmbeddings, setIsLoadingEmbeddings] = useState(false);

  const handleConnectNotion = useCallback(async () => {
    // Check if OAuth is already in progress
    if (notionAuthInProgress) {
      console.log("⚠️ OAuth already in progress, skipping...");
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      console.log("🔄 Starting Notion authorization...");
      const response = await authAPI.authorizeNotion();
      console.log("✅ Authorization URL received:", response.auth_url);

      if (response.auth_url) {
        // Show loading message before redirect
        setSigningStatus("Redirecting to Notion... Please wait.");
        setTimeout(() => {
          window.location.href = response.auth_url;
        }, 1000);
      } else {
        throw new Error("No authorization URL received");
      }
    } catch (err) {
      console.error("❌ Notion authorization failed:", err);
      const errorMessage = "Failed to start Notion authorization: " + (err.message || "Unknown error");
      setError(errorMessage);
      if (showSnackbar) {
        showSnackbar(errorMessage, 'error');
      }
      setIsConnecting(false);
    }
  }, [notionAuthInProgress]);

  useEffect(() => {
    if (user?.notion_connected) {
      checkStatus();
      loadNotionData();
      loadEmbeddingsInfo();
    }
  }, [user]);

  // Listen for auto-connect request from Dashboard
  useEffect(() => {
    const handleAutoConnect = (event) => {
      console.log("🎯 Auto-connect event received:", event.detail);
      if (
        event.detail?.action === "connect" &&
        !user?.notion_connected &&
        !notionAuthInProgress
      ) {
        console.log("🔄 Auto-connecting to Notion from Dashboard...");
        // Small delay to ensure the component is fully rendered
        setTimeout(() => {
          handleConnectNotion();
        }, 200);
      } else if (notionAuthInProgress) {
        console.log("⚠️ OAuth already in progress, skipping auto-connect");
      }
    };

    window.addEventListener("switchToNotionTab", handleAutoConnect);

    return () => {
      window.removeEventListener("switchToNotionTab", handleAutoConnect);
    };
  }, [user, handleConnectNotion, notionAuthInProgress]);

  const checkStatus = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const statusData = await notionAPI.getStatus();
      setStatus(statusData);
    } catch (err) {
      const errorMessage = "Failed to check Notion status";
      setError(errorMessage);
      if (showSnackbar) {
        showSnackbar(errorMessage, 'error');
      }
      console.error("Status check error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadNotionData = async () => {
    if (!user?.notion_connected) return;

    try {
      const [pagesResponse, databasesResponse] = await Promise.all([
        notionAPI.getPages(),
        notionAPI.getDatabases(),
      ]);
      setPages(pagesResponse.pages || []);
      setDatabases(databasesResponse.databases || []);
    } catch (err) {
      console.error("Failed to load Notion data:", err);
    }
  };

  const loadEmbeddingsInfo = async () => {
    if (!user?.notion_connected) return;

    setIsLoadingEmbeddings(true);
    try {
      const embeddingsData = await notionAPI.getEmbeddings();
      setEmbeddingsInfo(embeddingsData);
    } catch (err) {
      console.error("Failed to load embeddings info:", err);
    } finally {
      setIsLoadingEmbeddings(false);
    }
  };

  const handleSync = async () => {
    if (selectedPages.length === 0 && selectedDatabases.length === 0) {
      const errorMessage = "Please select at least one page or database to sync";
      setError(errorMessage);
      if (showSnackbar) {
        showSnackbar(errorMessage, 'warning');
      }
      return;
    }

    setIsSyncing(true);
    setError(null);

    try {
      // Sync selected pages
      if (selectedPages.length > 0) {
        await notionAPI.syncNotion(selectedPages);
      }

      setLastSync(new Date());
      await refreshUsage();

      // Clear selections
      setSelectedPages([]);
      setSelectedDatabases([]);

      // Refresh embeddings info to show updated data
      await loadEmbeddingsInfo();

      // Show success message
      if (showSnackbar) {
        showSnackbar('Notion content synced successfully!', 'success');
      }
      setTimeout(() => {
        setLastSync(null);
      }, 5000);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || "Failed to sync Notion";
      setError(errorMessage);
      if (showSnackbar) {
        showSnackbar(errorMessage, 'error');
      }
    } finally {
      setIsSyncing(false);
    }
  };

  const togglePageSelection = (pageId) => {
    setSelectedPages((prev) =>
      prev.includes(pageId)
        ? prev.filter((id) => id !== pageId)
        : [...prev, pageId]
    );
  };

  const toggleDatabaseSelection = (databaseId) => {
    setSelectedDatabases((prev) =>
      prev.includes(databaseId)
        ? prev.filter((id) => id !== databaseId)
        : [...prev, databaseId]
    );
  };

  const getStatusIcon = () => {
    if (isLoading) {
      return <RefreshCw className="h-5 w-5 text-gray-400 animate-spin" />;
    }

    if (user?.notion_connected) {
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    }

    return <AlertCircle className="h-5 w-5 text-red-600" />;
  };

  const getStatusText = () => {
    if (isLoading) return "Checking status...";
    if (user?.notion_connected) return "Connected";
    return "Not connected";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Notion Integration
          </h2>
          <p className="text-sm text-gray-600">
            Connect your Notion workspace and sync your content
          </p>
        </div>
        {user?.notion_connected && (
          <button
            onClick={loadNotionData}
            disabled={isLoading}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw
              className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`}
            />
            <span>Refresh</span>
          </button>
        )}
      </div>

      {/* Connection Status */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Database className="h-6 w-6 text-primary-600" />
            <div>
              <h3 className="font-medium text-gray-900">Connection Status</h3>
              <p className="text-sm text-gray-600">
                Notion workspace integration
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="text-sm font-medium">{getStatusText()}</span>
          </div>
        </div>

        {user?.notion_connected ? (
          <div className="space-y-3">
            <div className="flex items-center text-green-600">
              <CheckCircle className="h-4 w-4 mr-2" />
              <span className="text-sm font-medium">
                Connected to {user.notion_workspace_name}
              </span>
            </div>
            <p className="text-sm text-gray-600">
              You can now browse and sync your Notion pages and databases.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center text-gray-500">
              <AlertCircle className="h-4 w-4 mr-2" />
              <span className="text-sm">Not connected to Notion</span>
            </div>
            <p className="text-sm text-gray-600">
              Connect your Notion workspace to start syncing your content.
            </p>
            <button
              onClick={handleConnectNotion}
              disabled={isConnecting}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50"
            >
              {isConnecting ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <>
                  <Link className="h-4 w-4" />
                  <span>Connect Notion</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* OAuth State Display */}
      {(notionAuthInProgress || notionAuthError) && (
        <div className="card border-l-4 border-blue-500 bg-blue-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <RefreshCw
                className={`h-5 w-5 text-blue-600 ${
                  notionAuthInProgress ? "animate-spin" : ""
                }`}
              />
              <div>
                <h3 className="font-medium text-blue-900">OAuth Process</h3>
                {notionAuthInProgress && (
                  <p className="text-sm text-blue-700">
                    Processing Notion authorization...{" "}
                    {notionAuthRetryCount > 0 &&
                      `(Retry ${notionAuthRetryCount}/3)`}
                  </p>
                )}
                {notionAuthError && (
                  <p className="text-sm text-red-700">{notionAuthError}</p>
                )}
              </div>
            </div>
            {resetNotionAuthState && (
              <button
                onClick={resetNotionAuthState}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
              >
                Reset State
              </button>
            )}
          </div>
        </div>
      )}

      {/* Content Selection and Sync */}
      {user?.notion_connected && (
        <>
          {/* Pages Section */}
          {pages.length > 0 && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-gray-900">Pages</h3>
                <span className="text-sm text-gray-500">
                  {pages.length} pages available
                </span>
              </div>

              <div className="space-y-2 max-h-60 overflow-y-auto">
                {pages.map((page) => (
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
                        Last edited:{" "}
                        {new Date(page.last_edited_time).toLocaleDateString()}
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
              </div>
            </div>
          )}

          {/* Databases Section */}
          {databases.length > 0 && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-gray-900">Databases</h3>
                <span className="text-sm text-gray-500">
                  {databases.length} databases available
                </span>
              </div>

              <div className="space-y-2 max-h-60 overflow-y-auto">
                {databases.map((database) => (
                  <div
                    key={database.id}
                    className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <input
                      type="checkbox"
                      checked={selectedDatabases.includes(database.id)}
                      onChange={() => toggleDatabaseSelection(database.id)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900">
                        {database.title}
                      </h4>
                      <p className="text-xs text-gray-500">
                        Last edited:{" "}
                        {new Date(
                          database.last_edited_time
                        ).toLocaleDateString()}
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
          )}

          {/* Sync Button */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900 mb-1">
                  Sync Selected Content
                </h3>
                <p className="text-sm text-gray-600">
                  {selectedPages.length + selectedDatabases.length > 0
                    ? `Selected ${selectedPages.length} pages and ${selectedDatabases.length} databases`
                    : "Select pages or databases to sync"}
                </p>
              </div>
              <button
                onClick={handleSync}
                disabled={
                  (selectedPages.length === 0 &&
                    selectedDatabases.length === 0) ||
                  isSyncing
                }
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isSyncing ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Database className="h-4 w-4" />
                )}
                <span>{isSyncing ? "Syncing..." : "Sync Selected"}</span>
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

          {/* Synced Content Overview */}
          {embeddingsInfo && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-medium text-gray-900">Synced Content</h3>
                  <p className="text-sm text-gray-600">
                    Overview of your synced Notion pages and their embeddings
                  </p>
                </div>
                <button
                  onClick={loadEmbeddingsInfo}
                  disabled={isLoadingEmbeddings}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <RefreshCw
                    className={`h-4 w-4 ${isLoadingEmbeddings ? "animate-spin" : ""}`}
                  />
                  <span>Refresh</span>
                </button>
              </div>

              {isLoadingEmbeddings ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                  <span className="ml-2 text-gray-600">Loading embeddings...</span>
                </div>
              ) : embeddingsInfo.error ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-sm text-red-800">{embeddingsInfo.error}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-blue-600">
                        {embeddingsInfo.total_pages}
                      </div>
                      <div className="text-sm text-blue-800">Synced Pages</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-green-600">
                        {embeddingsInfo.total_chunks}
                      </div>
                      <div className="text-sm text-green-800">Content Chunks</div>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-purple-600">
                        {embeddingsInfo.pages.length > 0 ? "Ready" : "None"}
                      </div>
                      <div className="text-sm text-purple-800">Chat Status</div>
                    </div>
                  </div>

                  {embeddingsInfo.pages.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Recent Pages</h4>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {embeddingsInfo.pages.slice(0, 10).map((page, index) => (
                          <div
                            key={page.page_id}
                            className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                          >
                            <div className="flex-1">
                              <h5 className="text-sm font-medium text-gray-900">
                                {page.title}
                              </h5>
                              <p className="text-xs text-gray-500">
                                {page.chunks_count} chunks • Last edited: {page.last_edited_time ? new Date(page.last_edited_time).toLocaleDateString() : 'Unknown'}
                              </p>
                            </div>
                            <a
                              href={page.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary-600 hover:text-primary-700 p-1 rounded hover:bg-gray-100"
                              title="Open in Notion"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </>
      )}

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
      {/* loading Message */}
      {signingStatus && (
        <div className="bg-white-50 border border-black-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <Shield className="h-5 w-5 text-black-600" />
            <div>
              <p className="text-blue-800 font-medium">Signing In to Notion</p>
              <p className="text-blue-600 text-sm">{signingStatus}</p>
            </div>
          </div>
        </div>
      )}
      {/* Setup Instructions */}
      {!user?.notion_connected && (
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Settings className="h-5 w-5 text-primary-600" />
            <h3 className="font-medium text-gray-900">How It Works</h3>
          </div>

          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                1. Connect Your Notion Workspace
              </h4>
              <p className="text-gray-600">
                Click "Connect Notion" to securely connect your Notion workspace
                using OAuth. This allows you to access your pages and databases
                without sharing any tokens.
              </p>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                2. Select Content to Sync
              </h4>
              <p className="text-gray-600">
                Browse your Notion pages and databases, then select which ones
                you want to sync to your knowledge base. You can sync individual
                pages or entire databases.
              </p>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                3. Chat with Your Knowledge
              </h4>
              <p className="text-gray-600">
                Once synced, you can ask questions about your Notion content
                using the chat interface. The AI will search through your synced
                content to provide relevant answers.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Link className="h-5 w-5 text-blue-600" />
            </div>
            <h4 className="font-medium text-gray-900">Secure OAuth</h4>
          </div>
          <p className="text-sm text-gray-600">
            Connect securely using OAuth - no need to share API tokens or manage
            credentials
          </p>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <Plus className="h-5 w-5 text-green-600" />
            </div>
            <h4 className="font-medium text-gray-900">Selective Sync</h4>
          </div>
          <p className="text-sm text-gray-600">
            Choose exactly which pages and databases to sync - full control over
            your content
          </p>
        </div>
      </div>

      {/* Loading Overlay for Connection */}
      {isConnecting && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            <span className="text-gray-700">Connecting to Notion...</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default NotionSync;

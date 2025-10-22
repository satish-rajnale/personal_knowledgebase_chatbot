import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react';

function MessageSources({ sources }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  // Deduplicate sources by URL/page ID
  const deduplicatedSources = deduplicateSources(sources);
  
  const topSources = deduplicatedSources.slice(0, 2);
  const remainingSources = deduplicatedSources.slice(2);

  return (
    <div className="mt-3 border-t pt-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText size={14} className="text-gray-500" />
          <span className="text-xs font-medium text-gray-600">
            Sources ({deduplicatedSources.length})
          </span>
        </div>
        {deduplicatedSources.length > 2 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-primary-600 hover:text-primary-700 flex items-center space-x-1"
          >
            {isExpanded ? (
              <>
                <ChevronUp size={12} />
                <span>Show less</span>
              </>
            ) : (
              <>
                <ChevronDown size={12} />
                <span>Show more</span>
              </>
            )}
          </button>
        )}
      </div>

      <div className="mt-2 space-y-2">
        {/* Always show top sources */}
        {topSources.map((source, index) => (
          <SourceItem key={index} source={source} />
        ))}

        {/* Show remaining sources if expanded */}
        {isExpanded && remainingSources.map((source, index) => (
          <SourceItem key={index + 2} source={source} />
        ))}
      </div>
    </div>
  );
}

function deduplicateSources(sources) {
  const seen = new Map();
  const deduplicated = [];

  sources.forEach(source => {
    const { url, metadata } = source;
    
    // Get the unique identifier for this source
    const sourceUrl = url || (metadata && metadata.url);
    const pageId = metadata && metadata.page_id;
    
    // Create a unique key based on URL or page ID
    const uniqueKey = sourceUrl || pageId || `unknown-${Math.random()}`;
    
    if (!seen.has(uniqueKey)) {
      // First time seeing this source
      seen.set(uniqueKey, {
        ...source,
        chunkCount: 1,
        allChunks: [source]
      });
      deduplicated.push(seen.get(uniqueKey));
    } else {
      // We've seen this source before, update the existing entry
      const existing = seen.get(uniqueKey);
      existing.chunkCount += 1;
      existing.allChunks.push(source);
      
      // Update the text to include content from all chunks
      const allTexts = existing.allChunks.map(chunk => chunk.text).filter(Boolean);
      if (allTexts.length > 0) {
        existing.text = allTexts.slice(0, 2).join(' | '); // Show first 2 chunks
        if (allTexts.length > 2) {
          existing.text += ` (+${allTexts.length - 2} more chunks)`;
        }
      }
      
      // Use the highest relevance score
      const maxScore = Math.max(...existing.allChunks.map(chunk => chunk.score || 0));
      existing.score = maxScore;
    }
  });

  // Sort by relevance score (highest first)
  return deduplicated.sort((a, b) => (b.score || 0) - (a.score || 0));
}

function SourceItem({ source }) {
  const { text, source: sourceName, score, url, metadata, chunkCount } = source;
  
  // Extract URL from metadata if not directly available
  const sourceUrl = url || (metadata && metadata.url);
  
  // Format the source name for display
  const getDisplayName = () => {
    if (sourceName && sourceName !== 'Unknown source') {
      return sourceName;
    }
    
    // Try to extract name from metadata
    if (metadata) {
      if (metadata.source && metadata.source !== 'Unknown source') {
        return metadata.source;
      }
      if (metadata.title) {
        return metadata.title;
      }
      if (metadata.page_id) {
        return `Notion Page (${metadata.page_id.slice(0, 8)}...)`;
      }
    }
    
    return 'Unknown source';
  };
  
  // Format the URL for display
  const getDisplayUrl = () => {
    if (!sourceUrl) return null;
    
    // If it's a Notion URL, format it nicely
    if (sourceUrl.includes('notion.so')) {
      const pageId = sourceUrl.split('/').pop();
      return `notion.so/${pageId}`;
    }
    
    // For other URLs, show the domain
    try {
      const urlObj = new URL(sourceUrl);
      return urlObj.hostname + urlObj.pathname;
    } catch {
      return sourceUrl;
    }
  };
  
  // Get the actual URL to open
  const getActualUrl = () => {
    if (sourceUrl) return sourceUrl;
    
    // If no direct URL but we have a Notion page ID, construct the URL
    if (metadata && metadata.page_id) {
      return `https://notion.so/${metadata.page_id.replace(/-/g, '')}`;
    }
    
    return null;
  };
  
  return (
    <div className="bg-gray-50 rounded p-2 text-xs">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="font-medium text-gray-700 mb-1 flex items-center space-x-2">
            <span>{getDisplayName()}</span>
            {chunkCount > 1 && (
              <span className="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded text-xs">
                {chunkCount} chunks
              </span>
            )}
          </div>
          <div className="text-gray-600 line-clamp-2">
            {text}
          </div>
          {score && (
            <div className="text-gray-500 mt-1">
              Relevance: {(score * 100).toFixed(1)}%
            </div>
          )}
          {getActualUrl() && (
            <div className="mt-1">
              <a
                href={getActualUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 underline text-xs flex items-center space-x-1"
                title="Open source"
              >
                <ExternalLink size={10} />
                <span>{getDisplayUrl()}</span>
              </a>
            </div>
          )}
        </div>
        {getActualUrl() && (
          <a
            href={getActualUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 text-primary-600 hover:text-primary-700 p-1 rounded hover:bg-gray-100"
            title="Open source"
          >
            <ExternalLink size={12} />
          </a>
        )}
      </div>
    </div>
  );
}

export default MessageSources; 
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react';

function MessageSources({ sources }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  const topSources = sources.slice(0, 2);
  const remainingSources = sources.slice(2);

  return (
    <div className="mt-3 border-t pt-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText size={14} className="text-gray-500" />
          <span className="text-xs font-medium text-gray-600">
            Sources ({sources.length})
          </span>
        </div>
        {sources.length > 2 && (
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

function SourceItem({ source }) {
  const { text, source: sourceName, score, url } = source;
  
  return (
    <div className="bg-gray-50 rounded p-2 text-xs">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="font-medium text-gray-700 mb-1">
            {sourceName || 'Unknown source'}
          </div>
          <div className="text-gray-600 line-clamp-2">
            {text}
          </div>
          {score && (
            <div className="text-gray-500 mt-1">
              Relevance: {(score * 100).toFixed(1)}%
            </div>
          )}
        </div>
        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 text-primary-600 hover:text-primary-700"
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
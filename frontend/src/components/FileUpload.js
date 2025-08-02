import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadAPI } from '../services/api';
import { Upload, File, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';

function FileUpload() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    setIsUploading(true);
    setError(null);

    try {
      if (acceptedFiles.length === 1) {
        // Single file upload
        const result = await uploadAPI.uploadFile(acceptedFiles[0]);
        setUploadedFiles(prev => [...prev, {
          file: acceptedFiles[0],
          result,
          status: 'success'
        }]);
      } else {
        // Multiple files upload
        const result = await uploadAPI.uploadMultipleFiles(acceptedFiles);
        const newFiles = acceptedFiles.map(file => {
          const fileResult = result.results.find(r => r.filename === file.name);
          return {
            file,
            result: fileResult,
            status: fileResult?.status === 'success' ? 'success' : 'error'
          };
        });
        setUploadedFiles(prev => [...prev, ...newFiles]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md']
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setUploadedFiles([]);
    setError(null);
  };

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    switch (ext) {
      case 'pdf':
        return '📄';
      case 'txt':
        return '📝';
      case 'md':
        return '📋';
      default:
        return '📄';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Upload Documents</h2>
          <p className="text-sm text-gray-600">
            Upload PDF, TXT, or Markdown files to add to your knowledgebase
          </p>
        </div>
        {uploadedFiles.length > 0 && (
          <button
            onClick={clearAll}
            className="btn-secondary text-sm"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 cursor-pointer ${
          isDragActive
            ? 'border-primary-400 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-primary-600 font-medium">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-gray-600 mb-2">
              Drag & drop files here, or <span className="text-primary-600">click to select</span>
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, TXT, MD files up to 10MB
            </p>
          </div>
        )}
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <Loader className="h-5 w-5 text-blue-600 animate-spin" />
            <div>
              <p className="text-blue-800 font-medium">Uploading files...</p>
              <p className="text-blue-600 text-sm">Please wait while we process your documents</p>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <div>
              <p className="text-red-800 font-medium">Upload Error</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-md font-medium text-gray-900">Uploaded Files</h3>
          <div className="space-y-2">
            {uploadedFiles.map((fileData, index) => (
              <div
                key={index}
                className="bg-white border rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">{getFileIcon(fileData.file.name)}</div>
                  <div>
                    <p className="font-medium text-gray-900">{fileData.file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(fileData.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  {fileData.status === 'success' ? (
                    <div className="flex items-center space-x-2 text-green-600">
                      <CheckCircle size={16} />
                      <span className="text-sm">Success</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 text-red-600">
                      <AlertCircle size={16} />
                      <span className="text-sm">Error</span>
                    </div>
                  )}
                  
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Supported File Types</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">📄</span>
            <div>
              <p className="font-medium">PDF Files</p>
              <p className="text-gray-600">Text extraction from PDF documents</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-2xl">📝</span>
            <div>
              <p className="font-medium">Text Files</p>
              <p className="text-gray-600">Plain text documents (.txt)</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-2xl">📋</span>
            <div>
              <p className="font-medium">Markdown</p>
              <p className="text-gray-600">Markdown formatted documents (.md)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FileUpload; 
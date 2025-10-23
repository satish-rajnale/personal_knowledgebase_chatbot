# PDF Navigation & Source Attribution Implementation Guide

## 🎯 **Goal**
Implement a system that:
1. **Answers user questions** based on PDF content
2. **Provides source attribution** - showing which file and page the answer came from
3. **Enables navigation** to the correct file and page

## 📊 **Current System Analysis**

### ✅ **What's Already Working:**

1. **PDF Processing with OCR**: Your `PDFProcessor` class handles:
   - Converting PDFs to high-quality images (300 DPI)
   - OCR with Pix2Text for text, formulas, tables, and figures
   - Page-by-page processing with metadata

2. **Source Attribution**: Your system already tracks:
   - **File name**: `pdf_path` in metadata
   - **Page number**: `page_number` in metadata  
   - **Chunk type**: `chunk_type` (text, formula, table, figure)
   - **Bounding box**: `bbox` for precise location

3. **Vector Search**: Your chat system:
   - Searches relevant documents using embeddings
   - Returns sources with metadata
   - Shows source information in the frontend

### 🔧 **Current Metadata Structure:**

```python
metadata = {
    'pdf_path': '/path/to/document.pdf',
    'page_number': 5,
    'chunk_type': 'text',  # or 'formula', 'table', 'figure'
    'chunk_id': 'uuid-string',
    'bbox': [x1, y1, x2, y2],  # bounding box coordinates
    'raw_content': 'actual extracted text'
}
```

## 🚀 **Implementation Steps**

### **Step 1: Enhanced Source Attribution in Chat Response**

**File**: `backend/app/api/routes/chat.py`

Add this function after the existing imports:

```python
import os

def format_sources_with_navigation(relevant_docs):
    """Format sources with navigation information"""
    formatted_sources = []
    
    for doc in relevant_docs:
        metadata = doc.get('metadata', {})
        source_info = {
            'text': doc.get('text', '')[:200] + "...",
            'source': metadata.get('pdf_path', 'Unknown'),
            'page_number': metadata.get('page_number', 'Unknown'),
            'chunk_type': metadata.get('chunk_type', 'text'),
            'score': doc.get('score', 0),
            'navigation': {
                'file_name': os.path.basename(metadata.get('pdf_path', '')),
                'page': metadata.get('page_number'),
                'chunk_type': metadata.get('chunk_type'),
                'bbox': metadata.get('bbox')
            }
        }
        formatted_sources.append(source_info)
    
    return formatted_sources
```

**Update the chat endpoint** (around line 182):

```python
# Replace the existing sources formatting
sources = format_sources_with_navigation(relevant_docs)

# Save AI response with enhanced sources
ai_message = ChatMessage(
    session_id=session_id,
    role="assistant",
    content=ai_response,
    sources=json.dumps(sources)
)
```

### **Step 2: Enhanced Frontend Source Display**

**File**: `frontend/src/components/MessageSources.js`

Replace the existing `SourceItem` component:

```javascript
function SourceItem({ source }) {
  const { text, source: sourceName, score, navigation } = source;
  
  const getDisplayName = () => {
    if (navigation?.file_name) {
      return `${navigation.file_name} - Page ${navigation.page}`;
    }
    return sourceName || 'Unknown source';
  };
  
  const getChunkTypeIcon = (chunkType) => {
    switch(chunkType) {
      case 'formula': return '🧮';
      case 'table': return '📊';
      case 'figure': return '🖼️';
      default: return '📄';
    }
  };
  
  const handleViewPDF = () => {
    const pdfPath = navigation?.file_name;
    const pageNumber = navigation?.page;
    
    if (pdfPath) {
      // Create download link with page reference
      const link = document.createElement('a');
      link.href = `/api/pdf/download?file=${encodeURIComponent(pdfPath)}`;
      link.download = pdfPath;
      link.click();
      
      // Show page reference to user
      setTimeout(() => {
        alert(`📄 Open page ${pageNumber} in the downloaded PDF`);
      }, 100);
    }
  };
  
  return (
    <div className="bg-gray-50 rounded p-3 text-xs border-l-4 border-blue-400">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="font-medium text-gray-800">
            {getDisplayName()}
          </span>
          {navigation?.chunk_type && (
            <span className="text-lg">
              {getChunkTypeIcon(navigation.chunk_type)}
            </span>
          )}
        </div>
        <span className="text-gray-500">
          {Math.round(score * 100)}% match
        </span>
      </div>
      
      <div className="text-gray-600 mb-2">
        {text}
      </div>
      
      {navigation && (
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span>📄 Page {navigation.page}</span>
            {navigation.chunk_type && (
              <span>Type: {navigation.chunk_type}</span>
            )}
          </div>
          
          <button 
            onClick={handleViewPDF}
            className="px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600 transition-colors"
          >
            📄 View PDF
          </button>
        </div>
      )}
    </div>
  );
}
```

### **Step 3: PDF Download Endpoint**

**File**: `backend/app/api/routes/pdf_upload.py`

Add this new endpoint:

```python
from fastapi.responses import FileResponse
import os

@router.get("/pdf/download")
async def download_pdf(
    file: str,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Download PDF file with page reference
    """
    try:
        # Validate file path (security check)
        if not file or '..' in file or '/' in file:
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Construct full file path
        file_path = os.path.join(settings.UPLOAD_DIR, "temp_pdfs", file)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file for download
        return FileResponse(
            path=file_path,
            filename=file,
            media_type='application/pdf'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")
```

### **Step 4: Enhanced LLM Response with Source Citations**

**File**: `backend/app/services/llm.py`

Update the `_prepare_context` method:

```python
def _prepare_context(self, context: List[Dict[str, Any]]) -> str:
    """Prepare context with enhanced source information"""
    if not context:
        return "No relevant documents found."
    
    context_parts = []
    for i, doc in enumerate(context, 1):
        metadata = doc.get("metadata", {})
        source_info = metadata.get("pdf_path", "Unknown source")
        page_num = metadata.get("page_number", "Unknown")
        chunk_type = metadata.get("chunk_type", "text")
        
        content = doc.get("text", "")
        
        # Enhanced context with source details
        context_parts.append(
            f"**Source {i}** (File: {os.path.basename(source_info)}, "
            f"Page: {page_num}, Type: {chunk_type}):\n{content}\n"
        )
    
    return "\n".join(context_parts)
```

### **Step 5: Enhanced Chat Response Format**

**File**: `backend/app/services/llm.py`

Update the RAG response prompt:

```python
async def _generate_rag_response(self, query: str, context: List[Dict[str, Any]]) -> str:
    """Generate response using pure RAG approach"""
    context_text = self._prepare_context(context)
    
    prompt = f"""You are a helpful AI assistant that answers questions based on the provided context. 
Please use only the information from the context to answer the user's question. 
If the context doesn't contain enough information to answer the question, please say so.

**IMPORTANT: Format your response to be visually appealing and well-structured:**

1. **Use clear headings** with markdown formatting (##, ###)
2. **Use bullet points** (• or -) for lists
3. **Use bold text** (**text**) for emphasis
4. **Use code blocks** for policy numbers or technical details
5. **Structure your response** with clear sections
6. **Make it scannable** with proper spacing
7. **Always cite your sources** by mentioning the file name and page number

Context:
{context_text}

User Question: {query}

Please provide a helpful and accurate response based on the context above. 
Always mention which document and page you used to form your answer.
Format your response to be visually appealing and easy to read."""

    if self.provider == "openrouter":
        return await self._call_openrouter(prompt)
    elif self.provider == "ollama":
        return await self._call_ollama(prompt)
    else:
        raise ValueError(f"Unsupported provider: {self.provider}")
```

### **Step 6: Database Schema Enhancement (Optional)**

**File**: `backend/init.sql`

Add this table for better file management:

```sql
-- Enhanced PDF file tracking
CREATE TABLE IF NOT EXISTS pdf_files (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    total_pages INTEGER,
    upload_date TIMESTAMP DEFAULT NOW(),
    file_size BIGINT,
    processing_status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_pdf_files_user_id ON pdf_files(user_id);
CREATE INDEX IF NOT EXISTS idx_pdf_files_file_name ON pdf_files(file_name);
```

### **Step 7: Frontend PDF Viewer Integration (Advanced)**

**File**: `frontend/src/components/PDFViewer.js` (New file)

```javascript
import React, { useState } from 'react';

function PDFViewer({ pdfPath, pageNumber, onClose }) {
  const [currentPage, setCurrentPage] = useState(pageNumber || 1);
  
  const pdfUrl = `/api/pdf/viewer?file=${encodeURIComponent(pdfPath)}&page=${currentPage}`;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[90vh] overflow-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">
            PDF Viewer - Page {currentPage}
          </h3>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕ Close
          </button>
        </div>
        
        <div className="mb-4 flex items-center space-x-2">
          <button 
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            ← Previous
          </button>
          <span className="px-3 py-1 bg-blue-100 rounded">
            Page {currentPage}
          </span>
          <button 
            onClick={() => setCurrentPage(currentPage + 1)}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            Next →
          </button>
        </div>
        
        <iframe 
          src={pdfUrl}
          width="100%" 
          height="600px"
          title="PDF Viewer"
          className="border rounded"
        />
      </div>
    </div>
  );
}

export default PDFViewer;
```

**Update MessageSources.js to use PDFViewer:**

```javascript
import PDFViewer from './PDFViewer';

function MessageSources({ sources }) {
  const [showPDFViewer, setShowPDFViewer] = useState(false);
  const [selectedPDF, setSelectedPDF] = useState(null);
  
  const handleViewPDF = (source) => {
    setSelectedPDF({
      path: source.navigation?.file_name,
      page: source.navigation?.page
    });
    setShowPDFViewer(true);
  };
  
  return (
    <div>
      {/* ... existing code ... */}
      
      {showPDFViewer && selectedPDF && (
        <PDFViewer 
          pdfPath={selectedPDF.path}
          pageNumber={selectedPDF.page}
          onClose={() => {
            setShowPDFViewer(false);
            setSelectedPDF(null);
          }}
        />
      )}
    </div>
  );
}
```

## 🎯 **Implementation Priority**

### **Phase 1: Basic Navigation (Week 1)**
1. ✅ Enhanced source display with file names and page numbers
2. ✅ PDF download functionality with page references
3. ✅ Improved source formatting in chat responses

### **Phase 2: Advanced Features (Week 2-3)**
1. 🔄 PDF.js viewer integration for direct page navigation
2. 🔄 Enhanced metadata tracking in database
3. 🔄 Advanced search with file filtering

### **Phase 3: Polish & Optimization (Week 4)**
1. 🔄 Performance optimization for large PDFs
2. 🔄 Advanced UI/UX improvements
3. 🔄 Mobile responsiveness

## 🧪 **Testing Checklist**

- [ ] PDF upload and processing works correctly
- [ ] Source attribution shows correct file names and page numbers
- [ ] PDF download links work with page references
- [ ] Chat responses include proper source citations
- [ ] Frontend displays sources with navigation buttons
- [ ] Database stores metadata correctly
- [ ] Vector search returns relevant results with proper metadata

## 📝 **Notes**

- The current system already has most of the foundation needed
- Focus on enhancing the user experience for navigation and source attribution
- Consider adding PDF.js for advanced viewing capabilities
- Test with various PDF types (text, images, formulas, tables)
- Ensure mobile responsiveness for the new components

## 🚀 **Next Steps**

1. Start with **Step 1** and **Step 2** for immediate improvements
2. Test the basic functionality
3. Add **Step 3** for PDF download capability
4. Implement **Step 4** and **Step 5** for enhanced responses
5. Consider **Step 6** and **Step 7** for advanced features

This implementation will give you a robust system for PDF navigation and source attribution!

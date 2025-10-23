# PDF Processing Module Guide

## Overview

The PDF Processing Module provides comprehensive OCR capabilities for PDFs containing handwritten notes, printed text, mathematical formulas, and diagrams. It uses only free and open-source tools with compatible licenses.

## Features

### 🔍 OCR Capabilities
- **Printed Text**: High-quality OCR for standard printed text
- **Handwritten Text**: Recognition of handwritten notes and annotations
- **Mathematical Formulas**: Extraction and conversion to LaTeX format
- **Tables**: Structured table extraction with layout preservation
- **Diagrams**: Image and diagram detection
- **Layout Analysis**: Intelligent content segmentation

### 🚀 Performance Features
- **Multiprocessing**: Parallel processing for large PDFs
- **High DPI**: 300 DPI conversion for optimal OCR quality
- **Vector Embeddings**: 384-dimensional embeddings for semantic search
- **PostgreSQL Storage**: Efficient vector storage with pgvector

## Dependencies

All dependencies use free and open-source licenses:

```txt
# PDF Processing with OCR
pdf2image==1.16.3          # Apache 2.0 - PDF to image conversion
pix2text==0.2.0            # Apache 2.0 - OCR and layout analysis
Pillow==10.0.1             # PIL License - Image processing
opencv-python==4.8.1.78    # Apache 2.0 - Computer vision
```

## API Endpoints

### 1. Upload PDF (Asynchronous)
```http
POST /upload_pdf
Content-Type: multipart/form-data

file: PDF file
max_workers: Optional[int] (default: CPU count)
```

**Response:**
```json
{
  "success": true,
  "message": "PDF upload successful. Processing started.",
  "task_id": "uuid-string",
  "pdf_name": "document.pdf"
}
```

### 2. Upload PDF (Synchronous)
```http
POST /upload_pdf_sync
Content-Type: multipart/form-data

file: PDF file
max_workers: Optional[int]
```

**Response:**
```json
{
  "success": true,
  "message": "PDF processed successfully",
  "pdf_name": "document.pdf",
  "total_pages": 10,
  "processed_pages": 10,
  "total_chunks": 45,
  "stored_chunks": 45,
  "chunk_types": {
    "text": 30,
    "formula": 8,
    "table": 5,
    "figure": 2
  }
}
```

### 3. Check Processing Status
```http
GET /pdf_status/{task_id}
```

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "progress": {
    "current_page": 10,
    "total_pages": 10
  },
  "result": {
    "success": true,
    "total_pages": 10,
    "processed_pages": 10,
    "total_chunks": 45,
    "stored_chunks": 45,
    "chunk_types": {...}
  }
}
```

### 4. Get PDF Info
```http
GET /pdf_info
```

**Response:**
```json
{
  "supported_formats": ["PDF"],
  "max_file_size": 10485760,
  "features": [
    "OCR for printed text",
    "Handwritten text recognition",
    "Mathematical formula extraction (LaTeX)",
    "Table extraction",
    "Image and diagram detection",
    "Layout analysis",
    "Multiprocessing support"
  ],
  "ocr_engines": ["pix2text"],
  "supported_languages": ["English", "Multilingual"],
  "processing_modes": ["sync", "async"]
}
```

## Usage Examples

### Python Client Example

```python
import requests
import time

# Upload PDF asynchronously
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload_pdf',
        files={'file': f},
        data={'max_workers': 4}
    )

result = response.json()
task_id = result['task_id']

# Check processing status
while True:
    status_response = requests.get(f'http://localhost:8000/pdf_status/{task_id}')
    status = status_response.json()
    
    if status['status'] == 'completed':
        print("Processing complete!")
        print(f"Total chunks: {status['result']['total_chunks']}")
        break
    elif status['status'] == 'failed':
        print(f"Processing failed: {status['error']}")
        break
    
    time.sleep(2)  # Check every 2 seconds
```

### cURL Examples

```bash
# Upload PDF synchronously
curl -X POST "http://localhost:8000/upload_pdf_sync" \
  -F "file=@document.pdf" \
  -F "max_workers=4"

# Upload PDF asynchronously
curl -X POST "http://localhost:8000/upload_pdf" \
  -F "file=@document.pdf"

# Check status
curl "http://localhost:8000/pdf_status/{task_id}"

# Get PDF info
curl "http://localhost:8000/pdf_info"
```

## Architecture

### Processing Pipeline

1. **PDF Upload**: File validation and temporary storage
2. **PDF to Images**: High-quality conversion (300 DPI)
3. **OCR Processing**: Parallel processing of page images
4. **Content Analysis**: Text, formulas, tables, diagrams
5. **Chunking**: Intelligent content segmentation
6. **Embedding Generation**: 384-dimensional vectors
7. **Vector Storage**: PostgreSQL with pgvector
8. **Cleanup**: Temporary file removal

### Chunk Types

- **text**: Regular paragraphs and sentences
- **formula**: Mathematical expressions (LaTeX format)
- **table**: Structured tabular data
- **figure**: Images, diagrams, and graphics

### Metadata Structure

```json
{
  "pdf_path": "/path/to/document.pdf",
  "page_number": 1,
  "chunk_type": "formula",
  "chunk_id": "uuid-string",
  "bbox": [100, 200, 300, 250],
  "raw_content": "E = mc^2"
}
```

## Configuration

### Environment Variables

```bash
# File upload settings
MAX_FILE_SIZE=10485760  # 10MB

# Upload directory
UPLOAD_DIR=./uploads
```

### Docker Configuration

The module is fully integrated with the existing Docker setup:

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - MAX_FILE_SIZE=10485760
    volumes:
      - ./uploads:/app/uploads
```

## Testing

### Run Test Suite

```bash
# Test PDF processing module
python test_pdf_processing.py

# Test with Docker
docker-compose exec backend python test_pdf_processing.py
```

### Test Features

- ✅ PDF Processor initialization
- ✅ Embedding service integration
- ✅ PDF to image conversion
- ✅ OCR processing
- ✅ Chunk parsing and classification
- ✅ Embedding generation
- ✅ Dependency verification

## Performance Optimization

### Multiprocessing

- **Default**: Uses all CPU cores (max 4)
- **Custom**: Specify `max_workers` parameter
- **Large PDFs**: Recommended 2-4 workers for optimal performance

### Memory Management

- **Temporary Files**: Automatic cleanup after processing
- **Image Processing**: Efficient memory usage with PIL/OpenCV
- **Vector Storage**: Optimized PostgreSQL queries

## Error Handling

### Common Issues

1. **File Size**: 10MB limit (configurable)
2. **PDF Format**: Must be valid PDF file
3. **OCR Quality**: Depends on image quality and text clarity
4. **Memory**: Large PDFs may require more RAM

### Error Responses

```json
{
  "success": false,
  "error": "File too large. Maximum size: 10485760 bytes",
  "pdf_path": "document.pdf"
}
```

## License Compatibility

All dependencies use compatible open-source licenses:

- **Apache 2.0**: pdf2image, pix2text, opencv-python
- **PIL License**: Pillow
- **MIT**: sentence-transformers, numpy

## Troubleshooting

### Installation Issues

```bash
# Install system dependencies for pdf2image
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download poppler binaries and add to PATH
```

### OCR Quality Issues

1. **Increase DPI**: Modify `dpi=300` in `_pdf_to_images()`
2. **Image Preprocessing**: Add OpenCV preprocessing filters
3. **Model Selection**: Configure pix2text model parameters

### Performance Issues

1. **Reduce Workers**: Lower `max_workers` parameter
2. **Batch Processing**: Process smaller PDFs
3. **Memory Monitoring**: Check system memory usage

## Future Enhancements

- **Language Support**: Multi-language OCR
- **Advanced Layout**: Complex document structures
- **Real-time Processing**: WebSocket updates
- **Batch Processing**: Multiple PDF processing
- **Cloud Storage**: S3/GCS integration
- **API Rate Limiting**: Request throttling

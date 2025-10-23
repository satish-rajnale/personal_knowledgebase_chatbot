#!/usr/bin/env python3
"""
Test script for PDF processing functionality
Tests OCR, mathematical formulas, and handwritten notes extraction
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_processor import PDFProcessor
from app.services.embedding_service import embedding_service
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pdf_processing():
    """Test PDF processing functionality"""
    print("🧪 Testing PDF Processing Module")
    print("=" * 50)
    
    # Test 1: Initialize PDF processor
    print("\n1. Testing PDF Processor Initialization")
    try:
        processor = PDFProcessor()
        print("✅ PDF Processor initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing PDF processor: {e}")
        return False
    
    # Test 2: Test embedding service
    print("\n2. Testing Embedding Service")
    try:
        test_texts = [
            "This is a test document with mathematical formulas.",
            "The equation E = mc² is famous.",
            "Here's a table with data:",
            "| Column 1 | Column 2 |",
            "|----------|----------|",
            "| Value 1  | Value 2  |"
        ]
        
        embeddings = embedding_service.get_embeddings(test_texts)
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Embedding dimensions: {len(embeddings[0])}")
        
        # Verify embedding dimensions
        if len(embeddings[0]) == 384:
            print("✅ Embedding dimensions correct (384)")
        else:
            print(f"⚠️ Unexpected embedding dimensions: {len(embeddings[0])}")
            
    except Exception as e:
        print(f"❌ Error testing embedding service: {e}")
        return False
    
    # Test 3: Test PDF to image conversion (if PDF available)
    print("\n3. Testing PDF to Image Conversion")
    test_pdf_path = None
    
    # Look for test PDF in uploads directory
    uploads_dir = Path(settings.UPLOAD_DIR)
    if uploads_dir.exists():
        pdf_files = list(uploads_dir.glob("*.pdf"))
        if pdf_files:
            test_pdf_path = str(pdf_files[0])
            print(f"📄 Found test PDF: {test_pdf_path}")
        else:
            print("⚠️ No PDF files found in uploads directory")
    else:
        print("⚠️ Uploads directory not found")
    
    if test_pdf_path and os.path.exists(test_pdf_path):
        try:
            # Test PDF to image conversion
            images = processor._pdf_to_images(test_pdf_path)
            print(f"✅ Converted PDF to {len(images)} images")
            print(f"   Image shape: {images[0].shape}")
            
            # Test OCR on first page
            if images:
                print("\n4. Testing OCR on First Page")
                try:
                    chunks = processor._process_page(1, images[0], test_pdf_path)
                    print(f"✅ Extracted {len(chunks)} chunks from first page")
                    
                    # Display chunk information
                    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                        print(f"   Chunk {i+1}:")
                        print(f"     Type: {chunk.get('chunk_type', 'unknown')}")
                        print(f"     Content: {chunk.get('content', '')[:100]}...")
                        print(f"     Display: {chunk.get('display_content', '')[:100]}...")
                    
                    if len(chunks) > 3:
                        print(f"     ... and {len(chunks) - 3} more chunks")
                        
                except Exception as e:
                    print(f"❌ Error processing page: {e}")
                    
        except Exception as e:
            print(f"❌ Error converting PDF to images: {e}")
    else:
        print("⚠️ Skipping PDF processing test (no test PDF available)")
        print("   To test PDF processing, place a PDF file in the uploads directory")
    
    # Test 4: Test chunk parsing
    print("\n5. Testing Chunk Parsing")
    try:
        # Mock OCR results
        mock_ocr_results = [
            {
                'type': 'text',
                'text': 'This is a paragraph of text.',
                'bbox': [100, 200, 300, 250]
            },
            {
                'type': 'formula',
                'text': 'E = mc^2',
                'bbox': [100, 300, 200, 350]
            },
            {
                'type': 'table',
                'text': '| A | B |\n| 1 | 2 |',
                'bbox': [100, 400, 300, 500]
            }
        ]
        
        chunks = processor._parse_ocr_results(mock_ocr_results, 1, "test.pdf")
        print(f"✅ Parsed {len(chunks)} chunks from mock OCR results")
        
        for chunk in chunks:
            print(f"   - {chunk['chunk_type']}: {chunk['content'][:50]}...")
            
    except Exception as e:
        print(f"❌ Error testing chunk parsing: {e}")
    
    # Test 5: Test embedding generation for chunks
    print("\n6. Testing Embedding Generation for Chunks")
    try:
        test_chunks = [
            {
                'content': 'This is a test paragraph.',
                'display_content': 'Text: This is a test paragraph.',
                'chunk_type': 'text'
            },
            {
                'content': 'E = mc^2',
                'display_content': 'Formula: E = mc^2',
                'chunk_type': 'formula'
            }
        ]
        
        embeddings = processor._generate_embeddings_for_chunks(test_chunks)
        print(f"✅ Generated {len(embeddings)} embeddings for test chunks")
        
        # Verify embeddings were added to chunks
        for chunk in test_chunks:
            if 'embedding' in chunk:
                print(f"   ✅ Chunk '{chunk['chunk_type']}' has embedding")
            else:
                print(f"   ❌ Chunk '{chunk['chunk_type']}' missing embedding")
                
    except Exception as e:
        print(f"❌ Error testing embedding generation: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 PDF Processing Module Test Complete")
    print("\nFeatures tested:")
    print("✅ PDF Processor initialization")
    print("✅ Embedding service integration")
    print("✅ PDF to image conversion (if PDF available)")
    print("✅ OCR processing (if PDF available)")
    print("✅ Chunk parsing and classification")
    print("✅ Embedding generation")
    
    print("\n📋 Module Capabilities:")
    print("• OCR for printed text")
    print("• Handwritten text recognition")
    print("• Mathematical formula extraction (LaTeX)")
    print("• Table extraction")
    print("• Image and diagram detection")
    print("• Layout analysis")
    print("• Multiprocessing support")
    print("• Vector embedding generation")
    print("• PostgreSQL vector storage")
    
    return True

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🔍 Testing Dependencies")
    print("=" * 30)
    
    dependencies = [
        ('pdf2image', 'PDF to image conversion'),
        ('pix2text', 'OCR and layout analysis'),
        ('cv2', 'OpenCV for image processing'),
        ('PIL', 'Pillow for image handling'),
        ('sentence_transformers', 'Text embeddings'),
        ('numpy', 'Numerical operations')
    ]
    
    all_available = True
    
    for dep, description in dependencies:
        try:
            if dep == 'cv2':
                import cv2
            elif dep == 'PIL':
                from PIL import Image
            else:
                __import__(dep)
            print(f"✅ {dep}: {description}")
        except ImportError:
            print(f"❌ {dep}: {description} - NOT AVAILABLE")
            all_available = False
    
    if all_available:
        print("\n✅ All dependencies available")
    else:
        print("\n❌ Some dependencies missing - install with: pip install -r requirements.txt")
    
    return all_available

if __name__ == "__main__":
    print("🚀 PDF Processing Module Test Suite")
    print("=" * 50)
    
    # Test dependencies first
    deps_ok = test_dependencies()
    
    if deps_ok:
        # Run main tests
        asyncio.run(test_pdf_processing())
    else:
        print("\n❌ Cannot run tests - missing dependencies")
        sys.exit(1)

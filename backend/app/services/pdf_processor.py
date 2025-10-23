"""
PDF Processing Service for OCR, Mathematical Formulas, and Handwritten Notes
Uses only free and open-source tools with compatible licenses.
"""

import os
import tempfile
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# PDF to image conversion
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError, PDFSyntaxError

# OCR and layout analysis
import numpy as np
from PIL import Image

# Try to import Pix2Text with fallback
try:
    from pix2text import Pix2Text
    PIX2TEXT_AVAILABLE = True
    print("✅ Pix2Text imported successfully")
except ImportError as e:
    print(f"⚠️ Pix2Text import failed: {e}")
    print("🔄 PDF processing will use fallback methods")
    PIX2TEXT_AVAILABLE = False
    # Create a dummy Pix2Text class for compatibility
    class DummyPix2Text:
        def recognize(self, image):
            return [{'text': f'OCR not available for image', 'type': 'text'}]
    Pix2Text = DummyPix2Text

# Try to import OpenCV with fallback
try:
    import cv2
    CV2_AVAILABLE = True
    print("✅ OpenCV imported successfully")
except ImportError as e:
    print(f"⚠️ OpenCV import failed: {e}")
    print("🔄 PDF processing will use fallback methods")
    CV2_AVAILABLE = False
    # Create a dummy cv2 module for compatibility
    class DummyCV2:
        @staticmethod
        def cvtColor(img, code):
            return img
        @staticmethod
        def COLOR_RGB2BGR():
            return 4
    cv2 = DummyCV2()

# Existing services
from app.services.embedding_service import embedding_service
from app.services.postgres_vector_store import add_documents_to_store
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    PDF processing service that handles:
    - PDF to image conversion
    - OCR for text and handwritten notes
    - Mathematical formula extraction (LaTeX)
    - Layout analysis (tables, images)
    - Chunking and embedding generation
    """
    
    def __init__(self):
        """Initialize the PDF processor"""
        if PIX2TEXT_AVAILABLE:
            try:
                self.pix2text = Pix2Text()
                self.pix2text_available = True
                logger.info("✅ Pix2Text initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Pix2Text initialization failed: {e}")
                logger.warning("🔄 PDF processing will use fallback OCR methods")
                self.pix2text = None
                self.pix2text_available = False
        else:
            logger.warning("⚠️ Pix2Text not available, using fallback methods")
            self.pix2text = Pix2Text()  # This will be the dummy class
            self.pix2text_available = False
        
        self.temp_dir = Path(tempfile.gettempdir()) / "pdf_processing"
        self.temp_dir.mkdir(exist_ok=True)
        
        # OCR configuration
        self.ocr_config = {
            'text': {
                'model': 'mfd',  # Multi-modal formula detection
                'formula': 'mfd',  # Mathematical formula detection
            }
        }
        
        logger.info("PDF Processor initialized")
    
    async def process_pdf(self, pdf_path: str, user_id: str, max_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a PDF file and extract all content with embeddings
        
        Args:
            pdf_path: Path to the PDF file
            user_id: User ID for storing embeddings
            max_workers: Maximum number of worker processes (default: CPU count)
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Convert PDF to images
            images = self._pdf_to_images(pdf_path)
            logger.info(f"Converted PDF to {len(images)} images")
            
            # Process pages in parallel
            if max_workers is None:
                max_workers = min(mp.cpu_count(), 4)  # Limit to 4 workers max
            
            all_chunks = []
            processed_pages = 0
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all pages for processing
                future_to_page = {
                    executor.submit(self._process_page, page_num, image, pdf_path): page_num
                    for page_num, image in enumerate(images, 1)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_page):
                    page_num = future_to_page[future]
                    try:
                        page_chunks = future.result()
                        all_chunks.extend(page_chunks)
                        processed_pages += 1
                        logger.info(f"Processed page {page_num}/{len(images)}")
                    except Exception as e:
                        logger.error(f"Error processing page {page_num}: {e}")
            
            # Generate embeddings for all chunks
            if all_chunks:
                logger.info(f"Generating embeddings for {len(all_chunks)} chunks")
                embeddings = self._generate_embeddings_for_chunks(all_chunks)
                
                # Store in vector database
                logger.info("Storing chunks in vector database")
                stored_chunks = await self._store_chunks_in_db(all_chunks, embeddings, user_id)
                
                result = {
                    "success": True,
                    "pdf_path": pdf_path,
                    "total_pages": len(images),
                    "processed_pages": processed_pages,
                    "total_chunks": len(all_chunks),
                    "stored_chunks": len(stored_chunks),
                    "chunk_types": self._get_chunk_type_summary(all_chunks)
                }
            else:
                result = {
                    "success": False,
                    "error": "No content extracted from PDF",
                    "pdf_path": pdf_path,
                    "total_pages": len(images),
                    "processed_pages": processed_pages
                }
            
            logger.info(f"PDF processing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "pdf_path": pdf_path
            }
    
    def _pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """
        Convert PDF to high-quality images
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of images as numpy arrays
        """
        try:
            # Convert PDF to images with high quality
            images = convert_from_path(
                pdf_path,
                dpi=300,  # High DPI for better OCR
                fmt='RGB',
                thread_count=2
            )
            
            # Convert PIL images to numpy arrays
            np_images = []
            for img in images:
                np_img = np.array(img)
                np_images.append(np_img)
            
            return np_images
            
        except (PDFPageCountError, PDFSyntaxError) as e:
            logger.error(f"PDF conversion error: {e}")
            raise ValueError(f"Invalid PDF file: {e}")
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise
    
    def _process_page(self, page_num: int, image: np.ndarray, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Process a single page image to extract content
        
        Args:
            page_num: Page number
            image: Page image as numpy array
            pdf_path: Original PDF path
            
        Returns:
            List of content chunks
        """
        try:
            # Convert numpy array to PIL Image for pix2text
            pil_image = Image.fromarray(image)
            
            if self.pix2text_available and self.pix2text:
                # Run OCR and layout analysis with Pix2Text
                ocr_results = self.pix2text.recognize(pil_image)
                
                # Parse OCR results into chunks
                chunks = self._parse_ocr_results(ocr_results, page_num, pdf_path)
            else:
                # Fallback: Create a simple text chunk from the image
                logger.warning(f"Pix2Text not available, using fallback for page {page_num}")
                chunks = self._create_fallback_chunk(pil_image, page_num, pdf_path)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {e}")
            return []
    
    def _create_fallback_chunk(self, pil_image: Image.Image, page_num: int, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Create a fallback chunk when OCR is not available
        
        Args:
            pil_image: PIL Image object
            page_num: Page number
            pdf_path: Original PDF path
            
        Returns:
            List with a single fallback chunk
        """
        try:
            # Create a simple text representation
            fallback_text = f"Page {page_num} content (OCR not available)"
            
            chunk = {
                'content': fallback_text,
                'chunk_type': 'text',
                'page_number': page_num,
                'pdf_name': os.path.basename(pdf_path),
                'chunk_index': 0
            }
            
            return [chunk]
            
        except Exception as e:
            logger.error(f"Error creating fallback chunk for page {page_num}: {e}")
            return []
    
    def _parse_ocr_results(self, ocr_results: List[Dict], page_num: int, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Parse OCR results into structured chunks
        
        Args:
            ocr_results: Results from pix2text
            page_num: Page number
            pdf_path: Original PDF path
            
        Returns:
            List of content chunks
        """
        chunks = []
        
        for result in ocr_results:
            chunk_type = result.get('type', 'text')
            content = result.get('text', '')
            bbox = result.get('bbox', None)
            
            if not content.strip():
                continue
            
            # Determine chunk type
            if chunk_type == 'formula':
                chunk_type = 'formula'
                # Keep LaTeX format for formulas
                display_content = f"Formula: {content}"
            elif chunk_type == 'table':
                chunk_type = 'table'
                display_content = f"Table: {content}"
            elif chunk_type == 'figure':
                chunk_type = 'figure'
                display_content = f"Figure: {content}"
            else:
                chunk_type = 'text'
                display_content = content
            
            chunk = {
                'content': content,
                'display_content': display_content,
                'chunk_type': chunk_type,
                'page_number': page_num,
                'pdf_path': pdf_path,
                'bbox': bbox,
                'chunk_id': str(uuid.uuid4())
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def _generate_embeddings_for_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Generate embeddings for all chunks
        
        Args:
            chunks: List of content chunks
            
        Returns:
            List of embedding vectors
        """
        try:
            # Prepare texts for embedding
            texts = []
            for chunk in chunks:
                # Use display content for embedding (includes type information)
                texts.append(chunk['display_content'])
            
            # Generate embeddings
            embeddings = embedding_service.get_embeddings(texts)
            
            # Add embeddings to chunks
            for i, chunk in enumerate(chunks):
                chunk['embedding'] = embeddings[i]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    async def _store_chunks_in_db(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]], user_id: str) -> List[Dict[str, Any]]:
        """
        Store chunks in the vector database
        
        Args:
            chunks: List of content chunks
            embeddings: List of embedding vectors
            user_id: User ID
            
        Returns:
            List of stored chunks
        """
        try:
            # Prepare documents for storage
            documents = []
            for chunk in chunks:
                doc = {
                    'page_content': chunk['display_content'],
                    'metadata': {
                        'pdf_path': chunk['pdf_path'],
                        'page_number': chunk['page_number'],
                        'chunk_type': chunk['chunk_type'],
                        'chunk_id': chunk['chunk_id'],
                        'bbox': chunk.get('bbox'),
                        'raw_content': chunk['content']
                    }
                }
                documents.append(doc)
            
                # Store in vector database
                stored_chunks = await add_documents_to_store(
                    documents=documents,
                    source_type="pdf_ocr",
                    user_id=user_id
                )
            
            return stored_chunks
            
        except Exception as e:
            logger.error(f"Error storing chunks in database: {e}")
            return []
    
    def _get_chunk_type_summary(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get summary of chunk types
        
        Args:
            chunks: List of chunks
            
        Returns:
            Dictionary with chunk type counts
        """
        type_counts = {}
        for chunk in chunks:
            chunk_type = chunk.get('chunk_type', 'unknown')
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
        return type_counts
    
    def cleanup_temp_files(self, pdf_path: str):
        """Clean up temporary files"""
        try:
            # Remove temporary files if they exist
            temp_files = list(self.temp_dir.glob(f"*{Path(pdf_path).stem}*"))
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")

# Global PDF processor instance
pdf_processor = PDFProcessor()

async def process_pdf_file(pdf_path: str, user_id: str, max_workers: Optional[int] = None) -> Dict[str, Any]:
    """
    Convenience function to process a PDF file
    
    Args:
        pdf_path: Path to PDF file
        user_id: User ID
        max_workers: Maximum worker processes
        
    Returns:
        Processing results
    """
    return pdf_processor.process_pdf(pdf_path, user_id, max_workers)

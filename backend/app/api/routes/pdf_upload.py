"""
PDF Upload API endpoints for processing PDFs with OCR, mathematical formulas, and handwritten notes
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.user import User, get_db
from app.services.auth import get_current_user_optional
from app.services.pdf_processor import process_pdf_file
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class PDFUploadResponse(BaseModel):
    """Response model for PDF upload"""
    success: bool
    message: str
    task_id: Optional[str] = None
    pdf_name: Optional[str] = None
    total_pages: Optional[int] = None
    processed_pages: Optional[int] = None
    total_chunks: Optional[int] = None
    stored_chunks: Optional[int] = None
    chunk_types: Optional[dict] = None
    error: Optional[str] = None

class PDFProcessingStatus(BaseModel):
    """Status model for PDF processing"""
    task_id: str
    status: str  # "processing", "completed", "failed"
    progress: Optional[dict] = None
    result: Optional[dict] = None
    error: Optional[str] = None

# In-memory storage for processing status (use Redis in production)
processing_status = {}

@router.post("/upload_pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    max_workers: Optional[int] = Form(None),
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Upload and process a PDF file with OCR, mathematical formulas, and handwritten notes
    
    Args:
        file: PDF file to upload
        max_workers: Maximum number of worker processes (optional)
        user: Current user (optional for anonymous users)
        db: Database session
        
    Returns:
        PDFUploadResponse with processing results
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Check file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Create user ID if not authenticated
        if not user:
            user_id = str(uuid.uuid4())
            logger.info(f"Processing PDF for anonymous user: {user_id}")
        else:
            user_id = user.user_id
            logger.info(f"Processing PDF for user: {user_id}")
        
        # Save file temporarily
        temp_dir = Path(settings.UPLOAD_DIR) / "temp_pdfs"
        temp_dir.mkdir(exist_ok=True)
        
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_path = temp_dir / temp_filename
        
        with open(temp_path, "wb") as temp_file:
            temp_file.write(file_content)
        
        logger.info(f"Saved PDF temporarily: {temp_path}")
        
        # Generate task ID for tracking
        task_id = str(uuid.uuid4())
        
        # Initialize processing status
        processing_status[task_id] = {
            "status": "processing",
            "progress": {"current_page": 0, "total_pages": 0},
            "result": None,
            "error": None
        }
        
        # Process PDF in background
        background_tasks.add_task(
            process_pdf_background,
            task_id,
            str(temp_path),
            user_id,
            max_workers
        )
        
        return PDFUploadResponse(
            success=True,
            message="PDF upload successful. Processing started.",
            task_id=task_id,
            pdf_name=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

async def process_pdf_background(
    task_id: str,
    pdf_path: str,
    user_id: str,
    max_workers: Optional[int] = None
):
    """
    Background task to process PDF
    
    Args:
        task_id: Task ID for tracking
        pdf_path: Path to PDF file
        user_id: User ID
        max_workers: Maximum worker processes
    """
    try:
        logger.info(f"Starting background processing for task {task_id}")
        
        # Update status
        processing_status[task_id]["status"] = "processing"
        
        # Process PDF
        result = await process_pdf_file(pdf_path, user_id, max_workers)
        
        # Update status with results
        processing_status[task_id].update({
            "status": "completed" if result.get("success", False) else "failed",
            "result": result,
            "error": result.get("error")
        })
        
        logger.info(f"Completed background processing for task {task_id}")
        
        # Clean up temporary file
        try:
            os.unlink(pdf_path)
            logger.info(f"Cleaned up temporary file: {pdf_path}")
        except Exception as e:
            logger.warning(f"Error cleaning up temp file: {e}")
            
    except Exception as e:
        logger.error(f"Error in background processing for task {task_id}: {e}")
        processing_status[task_id].update({
            "status": "failed",
            "error": str(e)
        })

@router.get("/pdf_status/{task_id}", response_model=PDFProcessingStatus)
async def get_pdf_processing_status(task_id: str):
    """
    Get the processing status of a PDF upload
    
    Args:
        task_id: Task ID returned from upload
        
    Returns:
        PDFProcessingStatus with current status
    """
    if task_id not in processing_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status_data = processing_status[task_id]
    
    return PDFProcessingStatus(
        task_id=task_id,
        status=status_data["status"],
        progress=status_data.get("progress"),
        result=status_data.get("result"),
        error=status_data.get("error")
    )

@router.post("/upload_pdf_sync", response_model=PDFUploadResponse)
async def upload_pdf_sync(
    file: UploadFile = File(...),
    max_workers: Optional[int] = Form(None),
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Upload and process a PDF file synchronously (for smaller files)
    
    Args:
        file: PDF file to upload
        max_workers: Maximum number of worker processes (optional)
        user: Current user (optional for anonymous users)
        db: Database session
        
    Returns:
        PDFUploadResponse with processing results
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Check file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Create user ID if not authenticated
        if not user:
            user_id = str(uuid.uuid4())
        else:
            user_id = user.user_id
        
        # Save file temporarily
        temp_dir = Path(settings.UPLOAD_DIR) / "temp_pdfs"
        temp_dir.mkdir(exist_ok=True)
        
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_path = temp_dir / temp_filename
        
        with open(temp_path, "wb") as temp_file:
            temp_file.write(file_content)
        
        try:
            # Process PDF synchronously
            result = await process_pdf_file(str(temp_path), user_id, max_workers)
            
            if result.get("success", False):
                return PDFUploadResponse(
                    success=True,
                    message="PDF processed successfully",
                    pdf_name=file.filename,
                    total_pages=result.get("total_pages", 0),
                    processed_pages=result.get("processed_pages", 0),
                    total_chunks=result.get("total_chunks", 0),
                    stored_chunks=result.get("stored_chunks", 0),
                    chunk_types=result.get("chunk_types", {})
                )
            else:
                return PDFUploadResponse(
                    success=False,
                    message="PDF processing failed",
                    error=result.get("error", "Unknown error"),
                    pdf_name=file.filename
                )
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Error cleaning up temp file: {e}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.get("/pdf_info")
async def get_pdf_info():
    """
    Get information about PDF processing capabilities
    
    Returns:
        Dictionary with PDF processing information
    """
    return {
        "supported_formats": ["PDF"],
        "max_file_size": settings.MAX_FILE_SIZE,
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

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import aiofiles
from typing import List

from app.models.chat import get_db
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import add_documents_to_store
from app.core.config import settings

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    try:
        # Validate file type
        if not DocumentProcessor.validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: .pdf, .txt, .md"
            )
        
        # Validate file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if not DocumentProcessor.validate_file_size(file_size):
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Save file to uploads directory
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Process document
        documents = await DocumentProcessor.process_file(file_path, file.filename)
        
        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the file"
            )
        
        # Add to vector store
        await add_documents_to_store(documents, source_type="upload")
        
        return {
            "message": f"File '{file.filename}' uploaded and processed successfully",
            "filename": file.filename,
            "documents_processed": len(documents),
            "file_size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process multiple documents"""
    try:
        results = []
        
        for file in files:
            try:
                # Validate file type
                if not DocumentProcessor.validate_file_type(file.filename):
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "message": "Unsupported file type"
                    })
                    continue
                
                # Read file content
                content = await file.read()
                file_size = len(content)
                
                # Validate file size
                if not DocumentProcessor.validate_file_size(file_size):
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "message": f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
                    })
                    continue
                
                # Save file
                file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(content)
                
                # Process document
                documents = await DocumentProcessor.process_file(file_path, file.filename)
                
                if documents:
                    # Add to vector store
                    await add_documents_to_store(documents, source_type="upload")
                    
                    results.append({
                        "filename": file.filename,
                        "status": "success",
                        "documents_processed": len(documents),
                        "file_size": file_size
                    })
                else:
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "message": "No content could be extracted"
                    })
                    
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": str(e)
                })
        
        return {
            "message": "Multiple files processed",
            "results": results,
            "total_files": len(files),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        ) 
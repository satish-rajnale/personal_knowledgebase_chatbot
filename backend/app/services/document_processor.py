import os
import aiofiles
from typing import List
# Using simple dictionaries instead of LangChain Document objects
from pypdf import PdfReader
import markdown
from app.core.config import settings

class DocumentProcessor:
    """Service for processing different document types"""
    
    @staticmethod
    async def process_file(file_path: str, filename: str) -> List[dict]:
        """Process a file and return Document objects"""
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == '.pdf':
                return await DocumentProcessor._process_pdf(file_path, filename)
            elif file_extension == '.txt':
                return await DocumentProcessor._process_txt(file_path, filename)
            elif file_extension == '.md':
                return await DocumentProcessor._process_markdown(file_path, filename)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            print(f"❌ Error processing file {filename}: {e}")
            raise
    
    @staticmethod
    async def _process_pdf(file_path: str, filename: str) -> List[dict]:
        """Process PDF file"""
        try:
            reader = PdfReader(file_path)
            documents = []
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    doc = {
                        "page_content": text,
                        "metadata": {
                            "source": filename,
                            "page": page_num + 1,
                            "file_type": "pdf",
                            "total_pages": len(reader.pages)
                        }
                    }
                    documents.append(doc)
            
            print(f"✅ Processed PDF: {filename} ({len(documents)} pages)")
            return documents
            
        except Exception as e:
            print(f"❌ Error processing PDF {filename}: {e}")
            raise
    
    @staticmethod
    async def _process_txt(file_path: str, filename: str) -> List[dict]:
        """Process text file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
            
            doc = {
                "page_content": content,
                "metadata": {
                    "source": filename,
                    "file_type": "txt",
                    "page": 1
                }
            }
            
            print(f"✅ Processed text file: {filename}")
            return [doc]
            
        except Exception as e:
            print(f"❌ Error processing text file {filename}: {e}")
            raise
    
    @staticmethod
    async def _process_markdown(file_path: str, filename: str) -> List[dict]:
        """Process markdown file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
            
            # Convert markdown to plain text (remove formatting)
            # We'll keep the raw markdown for better context
            doc = {
                "page_content": content,
                "metadata": {
                    "source": filename,
                    "file_type": "markdown",
                    "page": 1
                }
            }
            
            print(f"✅ Processed markdown file: {filename}")
            return [doc]
            
        except Exception as e:
            print(f"❌ Error processing markdown file {filename}: {e}")
            raise
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size"""
        return file_size <= settings.MAX_FILE_SIZE
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Validate file type"""
        allowed_extensions = ['.pdf', '.txt', '.md']
        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in allowed_extensions 
from notion_client import Client
from typing import List, Dict, Any
import json
from app.core.config import settings

class NotionService:
    """Service for interacting with Notion API"""
    
    def __init__(self):
        if not settings.NOTION_TOKEN:
            raise ValueError("Notion token not configured")
        
        self.client = Client(auth=settings.NOTION_TOKEN)
        self.database_id = settings.NOTION_DATABASE_ID
    
    async def sync_database(self) -> List[Dict]:
        """Sync all pages from the configured Notion database"""
        try:
            if not self.database_id:
                raise ValueError("Notion database ID not configured")
            
            documents = []
            
            # Query all pages in the database
            response = self.client.databases.query(
                database_id=self.database_id
            )
            
            # Process each page
            for page in response["results"]:
                page_docs = await self._process_page(page)
                documents.extend(page_docs)
            
            # Handle pagination
            while response.get("has_more"):
                response = self.client.databases.query(
                    database_id=self.database_id,
                    start_cursor=response["next_cursor"]
                )
                
                for page in response["results"]:
                    page_docs = await self._process_page(page)
                    documents.extend(page_docs)
            
            print(f"✅ Synced {len(documents)} documents from Notion")
            return documents
            
        except Exception as e:
            print(f"❌ Error syncing Notion database: {e}")
            raise
    
    async def _process_page(self, page: Dict[str, Any]) -> List[Dict]:
        """Process a single Notion page"""
        try:
            page_id = page["id"]
            page_title = self._extract_page_title(page)
            
            # Get page content (blocks)
            blocks = await self._get_page_blocks(page_id)
            
            documents = []
            
            # Create document from page properties
            if page_title:
                doc = {
                    "page_content": f"Title: {page_title}\n\nContent: {self._extract_page_content(page)}",
                    "metadata": {
                        "source": f"Notion Page: {page_title}",
                        "page_id": page_id,
                        "source_type": "notion",
                        "url": f"https://notion.so/{page_id.replace('-', '')}"
                    }
                }
                documents.append(doc)
            
            # Create documents from blocks
            for block in blocks:
                if block.get("type") in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
                    content = self._extract_block_content(block)
                    if content.strip():
                        doc = {
                            "page_content": content,
                            "metadata": {
                                "source": f"Notion Page: {page_title}",
                                "page_id": page_id,
                                "block_id": block["id"],
                                "block_type": block["type"],
                                "source_type": "notion",
                                "url": f"https://notion.so/{page_id.replace('-', '')}"
                            }
                        }
                        documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"❌ Error processing Notion page {page.get('id', 'unknown')}: {e}")
            return []
    
    async def _get_page_blocks(self, page_id: str) -> List[Dict[str, Any]]:
        """Get all blocks from a Notion page"""
        try:
            blocks = []
            response = self.client.blocks.children.list(block_id=page_id)
            blocks.extend(response["results"])
            
            # Handle pagination
            while response.get("has_more"):
                response = self.client.blocks.children.list(
                    block_id=page_id,
                    start_cursor=response["next_cursor"]
                )
                blocks.extend(response["results"])
            
            return blocks
            
        except Exception as e:
            print(f"❌ Error getting blocks for page {page_id}: {e}")
            return []
    
    def _extract_page_title(self, page: Dict[str, Any]) -> str:
        """Extract page title from page properties"""
        try:
            properties = page.get("properties", {})
            
            # Try different title properties
            title_props = ["title", "Name", "Page", "Subject"]
            
            for prop_name in title_props:
                if prop_name in properties:
                    prop = properties[prop_name]
                    if prop["type"] == "title" and prop["title"]:
                        return " ".join([text["plain_text"] for text in prop["title"]])
            
            # Fallback to page ID
            return f"Page {page['id'][:8]}"
            
        except Exception as e:
            print(f"❌ Error extracting page title: {e}")
            return "Untitled Page"
    
    def _extract_page_content(self, page: Dict[str, Any]) -> str:
        """Extract content from page properties"""
        try:
            properties = page.get("properties", {})
            content_parts = []
            
            for prop_name, prop in properties.items():
                if prop["type"] in ["rich_text", "text"]:
                    if prop.get("rich_text"):
                        text = " ".join([text["plain_text"] for text in prop["rich_text"]])
                        if text.strip():
                            content_parts.append(f"{prop_name}: {text}")
                    elif prop.get("text"):
                        text = " ".join([text["plain_text"] for text in prop["text"]])
                        if text.strip():
                            content_parts.append(f"{prop_name}: {text}")
            
            return " | ".join(content_parts)
            
        except Exception as e:
            print(f"❌ Error extracting page content: {e}")
            return ""
    
    def _extract_block_content(self, block: Dict[str, Any]) -> str:
        """Extract content from a Notion block"""
        try:
            block_type = block["type"]
            block_data = block.get(block_type, {})
            
            if block_type.startswith("heading"):
                if block_data.get("rich_text"):
                    return " ".join([text["plain_text"] for text in block_data["rich_text"]])
            elif block_type in ["paragraph", "bulleted_list_item", "numbered_list_item"]:
                if block_data.get("rich_text"):
                    return " ".join([text["plain_text"] for text in block_data["rich_text"]])
            
            return ""
            
        except Exception as e:
            print(f"❌ Error extracting block content: {e}")
            return ""

# Global Notion service instance
notion_service = None

def get_notion_service() -> NotionService:
    """Get Notion service instance"""
    global notion_service
    if notion_service is None:
        notion_service = NotionService()
    return notion_service

async def sync_notion_database() -> List[Dict]:
    """Sync Notion database and return documents"""
    service = get_notion_service()
    return await service.sync_database() 
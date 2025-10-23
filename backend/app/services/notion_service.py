from notion_client import Client
from typing import List, Dict, Any, Optional
import json
import re
import httpx
from app.core.config import settings

class NotionService:
    """Service for interacting with Notion API"""
    
    def __init__(self, user_token: str):
        # Only user-specific tokens are supported - no global fallback
        if not user_token:
            raise ValueError("User Notion token is required")
        self.token = user_token
        
        self.client = Client(auth=self.token)
        self.synced_pages = set()  # Track synced pages to avoid duplicates
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.notion.com/v1/oauth/token",
                    auth=(settings.NOTION_CLIENT_ID, settings.NOTION_CLIENT_SECRET),
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": settings.NOTION_REDIRECT_URI
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"OAuth token exchange failed: {response.text}")
                
                token_data = response.json()
                return {
                    "access_token": token_data["access_token"],
                    "workspace_id": token_data.get("workspace_id"),
                    "workspace_name": token_data.get("workspace_name"),
                    "bot_id": token_data.get("bot_id")
                }
                
        except Exception as e:
            raise Exception(f"Failed to exchange code for token: {str(e)}")
    
    async def get_user_pages(self) -> List[Dict[str, Any]]:
        """Get all pages accessible to the user"""
        try:
            print("🔍 Starting get_user_pages...")
            import asyncio
            import concurrent.futures
            
            pages = []
            loop = asyncio.get_event_loop()
            
            def search_pages(start_cursor=None):
                print(f"🔍 Executing Notion search API call (cursor: {start_cursor})")
                if start_cursor:
                    return self.client.search(
                        filter={"property": "object", "value": "page"},
                        start_cursor=start_cursor,
                        page_size=100
                    )
                else:
                    return self.client.search(
                        filter={"property": "object", "value": "page"},
                        page_size=100
                    )
            
            print("🔍 Running first search in thread pool...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(executor, search_pages)
            
            print(f"✅ First search completed, got {len(response['results'])} pages")
            pages.extend(response["results"])
            
            # Handle pagination
            page_count = 1
            while response.get("has_more"):
                print(f"🔍 Running pagination search {page_count + 1}...")
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    response = await loop.run_in_executor(
                        executor,
                        search_pages,
                        response["next_cursor"]
                    )
                print(f"✅ Pagination search {page_count + 1} completed, got {len(response['results'])} pages")
                pages.extend(response["results"])
                page_count += 1
            
            print(f"✅ get_user_pages completed, total pages: {len(pages)}")
            return pages
            
        except Exception as e:
            print(f"Error getting user pages: {e}")
            return []
    
    async def get_user_databases(self) -> List[Dict[str, Any]]:
        """Get all databases accessible to the user"""
        try:
            import asyncio
            import concurrent.futures
            
            databases = []
            loop = asyncio.get_event_loop()
            
            def search_databases(start_cursor=None):
                if start_cursor:
                    return self.client.search(
                        filter={"property": "object", "value": "database"},
                        start_cursor=start_cursor,
                        page_size=100
                    )
                else:
                    return self.client.search(
                        filter={"property": "object", "value": "database"},
                        page_size=100
                    )
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(executor, search_databases)
            
            databases.extend(response["results"])
            
            # Handle pagination
            while response.get("has_more"):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    response = await loop.run_in_executor(
                        executor,
                        search_databases,
                        response["next_cursor"]
                    )
                databases.extend(response["results"])
            
            return databases
            
        except Exception as e:
            print(f"Error getting user databases: {e}")
            return []
    
    def _format_page_id(self, page_id: str) -> str:
        """Format page ID to proper Notion format with hyphens"""
        if not page_id:
            raise ValueError("Notion page ID not configured")
        
        # Remove any existing hyphens and format properly
        clean_id = re.sub(r'[^a-zA-Z0-9]', '', page_id)
        
        if len(clean_id) != 32:
            raise ValueError(f"Invalid page ID format. Expected 32 characters, got {len(clean_id)}")
        
        # Format as: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        formatted_id = f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"
        
        print(f"📝 Formatted page ID: {formatted_id}")
        return formatted_id
    
    async def sync_page(self, page_id: str) -> List[Dict]:
        """Sync content from a single Notion page and all its sub-pages"""
        try:
            if not page_id:
                raise ValueError("Page ID is required")
            
            # Format the page ID
            formatted_page_id = self._format_page_id(page_id)
            
            print(f"🔄 Syncing Notion page: {formatted_page_id}")
            
            # First, verify the page exists and is accessible
            try:
                import asyncio
                import concurrent.futures
                
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    page = await loop.run_in_executor(
                        executor,
                        self.client.pages.retrieve,
                        formatted_page_id
                    )
                print(f"✅ Page found: {self._extract_page_title(page)}")
            except Exception as e:
                raise ValueError(f"Could not access page {formatted_page_id}. Make sure the page is shared with your integration. Error: {str(e)}")
            
            # Reset synced pages tracking
            self.synced_pages = set()
            
            # Process the page and all its sub-pages recursively
            documents = await self._process_page_recursive(page)
            
            print(f"✅ Synced {len(documents)} documents from Notion page and sub-pages")
            return documents
            
        except Exception as e:
            print(f"❌ Error syncing Notion page: {e}")
            raise
    
    async def sync_user_pages(self, page_ids: List[str]) -> List[Dict]:
        """Sync multiple pages for a user"""
        print(f"🔍 Starting sync_user_pages for {len(page_ids)} pages")
        all_documents = []
        
        for i, page_id in enumerate(page_ids):
            try:
                print(f"🔍 Syncing page {i+1}/{len(page_ids)}: {page_id}")
                documents = await self.sync_page(page_id)
                print(f"✅ Page {page_id} synced, got {len(documents)} documents")
                all_documents.extend(documents)
            except Exception as e:
                print(f"❌ Error syncing page {page_id}: {e}")
                continue
        
        print(f"✅ sync_user_pages completed, total documents: {len(all_documents)}")
        return all_documents
    
    async def sync_database(self, database_id: str) -> List[Dict]:
        """Sync all pages from a specific Notion database"""
        try:
            if not database_id:
                raise ValueError("Database ID is required")
            
            print(f"🔄 Syncing Notion database: {database_id}")
            
            # Query all pages in the database
            response = self.client.databases.query(database_id=database_id)
            
            documents = []
            for page in response["results"]:
                page_docs = await self._process_page_recursive(page)
                documents.extend(page_docs)
            
            # Handle pagination
            while response.get("has_more"):
                response = self.client.databases.query(
                    database_id=database_id,
                    start_cursor=response["next_cursor"]
                )
                
                for page in response["results"]:
                    page_docs = await self._process_page_recursive(page)
                    documents.extend(page_docs)
            
            print(f"✅ Synced {len(documents)} documents from Notion database")
            return documents
            
        except Exception as e:
            print(f"❌ Error syncing Notion database: {e}")
            raise
    
    async def _process_page_recursive(self, page: Dict[str, Any]) -> List[Dict]:
        """Process a single Notion page and all its sub-pages recursively"""
        try:
            page_id = page["id"]
            
            # Avoid processing the same page twice
            if page_id in self.synced_pages:
                return []
            
            self.synced_pages.add(page_id)
            page_title = self._extract_page_title(page)
            
            print(f"📄 Processing page: {page_title} ({page_id})")
            
            documents = []
            
            # Get page content (blocks)
            blocks = await self._get_page_blocks(page_id)
            
            # Create document from page properties
            if page_title:
                page_content = self._extract_page_content(page)
                doc = {
                    "page_content": f"Title: {page_title}\n\nContent: {page_content}",
                    "metadata": {
                        "source": f"Notion: {page_title}",
                        "title": page_title,
                        "page_id": page_id,
                        "source_type": "notion",
                        "url": f"https://notion.so/{page_id.replace('-', '')}",
                        "last_edited_time": page.get("last_edited_time"),
                        "created_time": page.get("created_time")
                    }
                }
                documents.append(doc)
                print(f"  📄 Created document from page properties: {page_title}")
                print(f"     Content length: {len(page_content)} characters")
                print(f"     Content preview: {page_content[:100]}...")
            
            # Combine all blocks into a single document for better chunking
            all_block_content = []
            for block in blocks:
                # Process regular content blocks
                if block.get("type") in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
                    content = self._extract_block_content(block)
                    if content.strip():
                        all_block_content.append(content)
                        print(f"  📝 Extracted block content: {block['type']} - {content[:50]}...")
            
            # Create a single document with all block content combined
            if all_block_content:
                combined_content = "\n\n".join(all_block_content)
                doc = {
                    "page_content": f"Title: {page_title}\n\nContent: {combined_content}",
                    "metadata": {
                        "source": f"Notion: {page_title}",
                        "title": page_title,
                        "page_id": page_id,
                        "source_type": "notion",
                        "url": f"https://notion.so/{page_id.replace('-', '')}",
                        "last_edited_time": page.get("last_edited_time"),
                        "created_time": page.get("created_time"),
                        "block_count": len(all_block_content)
                    }
                }
                documents.append(doc)
                print(f"  📄 Created combined document with {len(all_block_content)} blocks")
                print(f"     Total content length: {len(combined_content)} characters")
            
            # Process sub-pages (child pages) separately
            for block in blocks:
                if block.get("type") == "child_page":
                    try:
                        child_page_data = block.get("child_page", {})
                        if not child_page_data:
                            print(f"⚠️  Empty child_page block: {block.get('id', 'unknown')}")
                            continue
                            
                        child_page_id = child_page_data.get("id")
                        if not child_page_id:
                            print(f"⚠️  No page ID found in child_page block: {block.get('id', 'unknown')}")
                            continue
                            
                        child_page_title = child_page_data.get("title", "Untitled")
                        print(f"🔍 Found sub-page: {child_page_title} ({child_page_id})")
                        
                        # Retrieve and process the child page
                        child_page = self.client.pages.retrieve(page_id=child_page_id)
                        child_docs = await self._process_page_recursive(child_page)
                        documents.extend(child_docs)
                        
                    except Exception as e:
                        print(f"❌ Error processing sub-page {block.get('id', 'unknown')}: {e}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                
                # Check for table blocks (which are databases in Notion)
                elif block.get("type") == "table":
                    try:
                        print(f"🔍 Debug: Found table block: {block.get('id', 'unknown')}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                        
                        table_data = block.get("table", {})
                        if not table_data:
                            print(f"⚠️  Empty table block: {block.get('id', 'unknown')}")
                            continue
                            
                        # Tables in Notion are actually databases, so we need to get the database ID
                        # This might be stored in the table properties or we need to query it differently
                        print(f"📊 Found table with {len(table_data.get('table_width', 0))} columns")
                        
                        # For tables, we need to get the database ID from the parent page or context
                        # This is a bit tricky as tables don't directly expose their database ID
                        print(f"⚠️  Table block found - may need manual database ID configuration")
                        
                    except Exception as e:
                        print(f"❌ Error processing table {block.get('id', 'unknown')}: {e}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                
                # Check for database blocks that might contain pages
                elif block.get("type") == "child_database":
                    try:
                        print(f"🔍 Debug: Found child_database block: {block.get('id', 'unknown')}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                        
                        child_database = block.get("child_database", {})
                        if not child_database:
                            print(f"⚠️  Empty child_database block: {block.get('id', 'unknown')}")
                            continue
                            
                        # Try different possible keys for database ID
                        database_id = (
                            child_database.get("id") or 
                            child_database.get("database_id") or
                            child_database.get("page_id")
                        )
                        
                        if not database_id:
                            print(f"⚠️  No database ID found in child_database block: {block.get('id', 'unknown')}")
                            print(f"   Available keys in child_database: {list(child_database.keys())}")
                            print(f"   Full child_database content: {json.dumps(child_database, indent=2)}")
                            
                            # Try using the block ID as the database ID
                            block_id = block.get("id")
                            if block_id:
                                print(f"🔄 Trying to use block ID as database ID: {block_id}")
                                try:
                                    # Test if the block ID works as a database ID
                                    test_response = self.client.databases.query(database_id=block_id, page_size=1)
                                    database_id = block_id
                                    print(f"✅ Block ID works as database ID: {database_id}")
                                except Exception as e:
                                    print(f"❌ Block ID doesn't work as database ID: {e}")
                                    
                                    # Try searching for the database by title
                                    database_title = child_database.get("title", "")
                                    if database_title:
                                        print(f"🔍 Searching for database by title: '{database_title}'")
                                        try:
                                            # Search for the database
                                            search_response = self.client.search(
                                                query=database_title,
                                                filter={"property": "object", "value": "database"}
                                            )
                                            
                                            for result in search_response.get("results", []):
                                                if result.get("object") == "database":
                                                    result_title = result.get("title", [{}])[0].get("plain_text", "")
                                                    if result_title.lower() == database_title.lower():
                                                        database_id = result["id"]
                                                        print(f"✅ Found database by title: {database_id}")
                                                        break
                                            
                                            if not database_id:
                                                print(f"❌ Could not find database with title: '{database_title}'")
                                                
                                        except Exception as search_error:
                                            print(f"❌ Error searching for database: {search_error}")
                            
                            if not database_id:
                                print(f"⚠️  Skipping block - could not determine database ID")
                                continue
                            
                        database_title = child_database.get("title", "Untitled")
                        print(f"🔍 Found table/database: {database_title} ({database_id})")
                        
                        # Query all pages in the database (table rows)
                        print(f"📋 Querying pages from table: {database_title}")
                        response = self.client.databases.query(database_id=database_id)
                        
                        print(f"📄 Found {len(response['results'])} pages/rows in table")
                        
                        for db_page in response["results"]:
                            page_title = self._extract_page_title(db_page)
                            print(f"   📝 Processing table row: {page_title}")
                            db_docs = await self._process_page_recursive(db_page)
                            documents.extend(db_docs)
                        
                        # Handle pagination for sub-database
                        while response.get("has_more"):
                            response = self.client.databases.query(
                                database_id=database_id,
                                start_cursor=response["next_cursor"]
                            )
                            
                            print(f"📄 Found {len(response['results'])} more pages/rows in table")
                            
                            for db_page in response["results"]:
                                page_title = self._extract_page_title(db_page)
                                print(f"   📝 Processing table row: {page_title}")
                                db_docs = await self._process_page_recursive(db_page)
                                documents.extend(db_docs)
                        
                    except Exception as e:
                        print(f"❌ Error processing sub-database {block.get('id', 'unknown')}: {e}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                
                # Check for database view blocks
                elif block.get("type") == "database_view":
                    try:
                        print(f"🔍 Debug: Found database_view block: {block.get('id', 'unknown')}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                        
                        database_view = block.get("database_view", {})
                        if not database_view:
                            print(f"⚠️  Empty database_view block: {block.get('id', 'unknown')}")
                            continue
                            
                        database_id = database_view.get("database_id")
                        if not database_id:
                            print(f"⚠️  No database ID found in database_view block: {block.get('id', 'unknown')}")
                            print(f"   Available keys in database_view: {list(database_view.keys())}")
                            continue
                            
                        print(f"🔍 Found database view for database: {database_id}")
                        
                        # Query all pages in the database
                        response = self.client.databases.query(database_id=database_id)
                        
                        for db_page in response["results"]:
                            db_docs = await self._process_page_recursive(db_page)
                            documents.extend(db_docs)
                        
                        # Handle pagination for database
                        while response.get("has_more"):
                            response = self.client.databases.query(
                                database_id=database_id,
                                start_cursor=response["next_cursor"]
                            )
                            
                            for db_page in response["results"]:
                                db_docs = await self._process_page_recursive(db_page)
                                documents.extend(db_docs)
                        
                    except Exception as e:
                        print(f"❌ Error processing database_view {block.get('id', 'unknown')}: {e}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                
                # Check for linked database blocks
                elif block.get("type") == "linked_database":
                    try:
                        print(f"🔍 Debug: Found linked_database block: {block.get('id', 'unknown')}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
                        
                        linked_database = block.get("linked_database", {})
                        if not linked_database:
                            print(f"⚠️  Empty linked_database block: {block.get('id', 'unknown')}")
                            continue
                            
                        database_id = linked_database.get("database_id")
                        if not database_id:
                            print(f"⚠️  No database ID found in linked_database block: {block.get('id', 'unknown')}")
                            print(f"   Available keys in linked_database: {list(linked_database.keys())}")
                            continue
                            
                        print(f"🔍 Found linked database: {database_id}")
                        
                        # Query all pages in the linked database
                        response = self.client.databases.query(database_id=database_id)
                        
                        for db_page in response["results"]:
                            db_docs = await self._process_page_recursive(db_page)
                            documents.extend(db_docs)
                        
                        # Handle pagination for linked database
                        while response.get("has_more"):
                            response = self.client.databases.query(
                                database_id=database_id,
                                start_cursor=response["next_cursor"]
                            )
                            
                            for db_page in response["results"]:
                                db_docs = await self._process_page_recursive(db_page)
                                documents.extend(db_docs)
                        
                    except Exception as e:
                        print(f"❌ Error processing linked_database {block.get('id', 'unknown')}: {e}")
                        print(f"   Block structure: {json.dumps(block, indent=2)}")
            
            return documents
            
        except Exception as e:
            print(f"❌ Error processing Notion page {page.get('id', 'unknown')}: {e}")
            return []
    
    async def _get_page_blocks(self, page_id: str) -> List[Dict[str, Any]]:
        """Get all blocks from a Notion page"""
        try:
            import asyncio
            import concurrent.futures
            
            blocks = []
            
            # Run the first API call in a thread pool
            loop = asyncio.get_event_loop()
            
            def get_blocks(block_id, start_cursor=None):
                if start_cursor:
                    return self.client.blocks.children.list(
                        block_id=block_id,
                        start_cursor=start_cursor
                    )
                else:
                    return self.client.blocks.children.list(block_id=block_id)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(executor, get_blocks, page_id)
            
            blocks.extend(response["results"])
            
            # Handle pagination
            while response.get("has_more"):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    response = await loop.run_in_executor(
                        executor,
                        get_blocks,
                        page_id,
                        response["next_cursor"]
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

# Helper function to create Notion service for a user
def create_notion_service(user_token: str) -> NotionService:
    """Create Notion service instance for a specific user"""
    return NotionService(user_token=user_token) 
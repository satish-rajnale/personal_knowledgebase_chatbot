import httpx
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model_name = settings.MODEL_NAME
        
        if self.provider == "openrouter":
            self.api_key = settings.OPENROUTER_API_KEY
            self.base_url = "https://openrouter.ai/api/v1"
        elif self.provider == "ollama":
            self.base_url = settings.OLLAMA_BASE_URL
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using RAG approach"""
        try:
            # Prepare context
            context_text = self._prepare_context(context)
            
            # Create prompt
            prompt = self._create_prompt(query, context_text)
            
            # Generate response
            if self.provider == "openrouter":
                response = await self._call_openrouter(prompt)
            elif self.provider == "ollama":
                response = await self._call_ollama(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error generating LLM response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _prepare_context(self, context: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved documents"""
        if not context:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(context, 1):
            source_info = doc.get("metadata", {}).get("source", "Unknown source")
            content = doc.get("text", "")
            context_parts.append(f"Document {i} (Source: {source_info}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create RAG prompt with context and query"""
        return f"""You are a helpful AI assistant that answers questions based on the provided context. 
Please use only the information from the context to answer the user's question. 
If the context doesn't contain enough information to answer the question, please say so.

Context:
{context}

User Question: {query}

Please provide a helpful and accurate response based on the context above. 
If possible, cite the specific documents you used to form your answer."""

    async def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API"""
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Personal Knowledgebase Chatbot"
                },
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1000
                    }
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["response"]

# Global LLM service instance
llm_service = LLMService()

async def generate_chat_response(query: str, context: List[Dict[str, Any]]) -> str:
    """Generate chat response using LLM service"""
    return await llm_service.generate_response(query, context) 
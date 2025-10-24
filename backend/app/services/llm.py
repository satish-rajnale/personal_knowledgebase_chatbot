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
        """Generate response using enhanced RAG approach with general knowledge when needed"""
        try:
            # Determine if this is a question that needs general knowledge
            needs_general_knowledge = self._needs_general_knowledge(query)
            
            if needs_general_knowledge:
                # Use hybrid approach: RAG + general knowledge
                return await self._generate_hybrid_response(query, context)
            else:
                # Use pure RAG approach
                return await self._generate_rag_response(query, context)
            
        except Exception as e:
            print(f"❌ Error generating LLM response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _needs_general_knowledge(self, query: str) -> bool:
        """Determine if the query needs general knowledge beyond the provided context"""
        general_keywords = [
            "should i", "consider", "recommend", "advice", "suggestion", "missing",
            "better", "compare", "options", "alternatives", "improve", "enhance",
            "what if", "how to", "tips", "best practices", "general", "typically",
            "usually", "common", "standard", "industry", "market", "trends"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in general_keywords)
    
    async def _generate_hybrid_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using both RAG context and general knowledge"""
        context_text = self._prepare_context(context)
        
        prompt = f"""You are a knowledgeable AI assistant with expertise in insurance, financial planning, and general advice. 
You have access to the user's personal information from their documents, and you can also provide general advice and recommendations.

**IMPORTANT: Format your response to be visually appealing and well-structured like ChatGPT:**

1. **Use clear headings** with markdown formatting (##, ###)
2. **Use bullet points** (• or -) for lists and suggestions
3. **Use checkmarks** (✅) for positive points and (⚠️) for warnings
4. **Use bold text** (**text**) for emphasis
5. **Use code blocks** for policy numbers or technical details
6. **Structure your response** with clear sections
7. **Use emojis** sparingly but effectively (📋, 💡, 🔍, etc.)
8. **Make it scannable** with proper spacing and formatting
9. **AVOID raw markdown tables** - use bullet points and sections instead
10. **For checklists and summaries**, use structured bullet points with status indicators

When answering:
1. First, summarize the user's current situation from their documents
2. Then provide structured advice, suggestions, or recommendations
3. Be clear about what information comes from their documents vs. general knowledge
4. If making recommendations, explain your reasoning
5. Use a conversational but professional tone
6. **For checklists and summaries**, format like this:
   - ✅ **Task Name**: Description of what to do
   - ⚠️ **Important Note**: Any warnings or considerations
   - 📋 **Next Steps**: Clear action items

Context from user's documents:
{context_text if context_text != "No relevant documents found." else "No specific documents provided."}

User Question: {query}

Please provide a comprehensive, well-formatted response that combines information from their documents (if available) with general advice and recommendations. Make it visually appealing and easy to read."""

        if self.provider == "openrouter":
            return await self._call_openrouter(prompt)
        elif self.provider == "ollama":
            return await self._call_ollama(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _generate_rag_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using pure RAG approach"""
        context_text = self._prepare_context(context)
        
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context. 
Use the following context to answer the question. If the answer isn't in the context, say you don't know.

**Context:**
{context_text}

**Question:** {query}

**Instructions:**
- Answer based only on the provided context
- If the context doesn't contain enough information, say so clearly
- Use clear, well-structured formatting with headings, bullet points, and emphasis
- Cite specific sources when possible
- Keep your response concise but comprehensive
- If the question is about a specific topic, focus on that topic in your answer
- **AVOID raw markdown tables** - use bullet points and sections instead
- **For checklists and summaries**, use structured bullet points with status indicators like:
  - ✅ **Task Name**: Description
  - ⚠️ **Important Note**: Warnings
  - 📋 **Next Steps**: Action items

Please provide a helpful and accurate response."""

        if self.provider == "openrouter":
            return await self._call_openrouter(prompt)
        elif self.provider == "ollama":
            return await self._call_ollama(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _prepare_context(self, context: List[Dict[str, Any]]) -> str:
        """Prepare structured context from retrieved documents"""
        if not context:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(context, 1):
            # Extract metadata
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown source")
            section = metadata.get("section", "")
            page_number = metadata.get("page_number", "")
            chunk_type = metadata.get("chunk_type", "text")
            
            # Get content
            content = doc.get("text", "")
            
            # Build source description
            source_desc = source
            if section:
                source_desc += f" - {section}"
            if page_number:
                source_desc += f" (Page {page_number})"
            if chunk_type != "text":
                source_desc += f" [{chunk_type}]"
            
            # Add relevance score if available
            score = doc.get("score", 0.0)
            if score > 0:
                source_desc += f" (Relevance: {score:.2f})"
            
            # Format the context entry
            context_entry = f"Source {i}: {source_desc}\n{content}\n"
            context_parts.append(context_entry)
        
        return "\n".join(context_parts)

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
                    "max_tokens": 1500
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
                        "num_predict": 1500
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
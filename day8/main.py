import logging
import os
from groq import Groq
from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
from starlette.requests import Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMSummarizerAIM(SimpleServer):
    manifest = {
        "name": "LLMSummarizerAIM",
        "short_name": "llm-summarizer",
        "version": "1.0.0",
        "author": "Raijin - HyperPG Intern",
        "license": "MIT",
        "documentation_url": "",
        "terms_of_service": ""
    }
    
    def __init__(self):
        super().__init__()
        # Initialize Groq client
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            logger.error("GROQ_API_KEY environment variable not set!")
            raise ValueError("GROQ_API_KEY is required")
        
        self.groq_client = Groq(api_key=api_key)
        logger.info("Groq client initialized successfully")

    @aim_uri(
        uri="/health",
        methods=["GET"],
        endpoint_manifest={
            "input_query": {},
            "input_headers": {},
            "input_body": {},
            "output": {"status": "<string>", "aim": "<string>", "version": "<string>"},
            "documentation": "Health check endpoint",
            "example_calls": [{
                "method": "GET",
                "query": "",
                "output": {"status": "healthy", "aim": "LLMSummarizerAIM", "version": "1.0.0"}
            }],
            "is_public": True
        }
    )
    async def health_endpoint(self, request):
        logger.info("Health check requested")
        return JSONResponseCORS({
            "status": "healthy",
            "aim": "LLMSummarizerAIM",
            "version": "1.0.0"
        })

    @aim_uri(
        uri="/summarize",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_headers": {},
            "input_body": {"text": "<string>"},
            "output": {
                "original_length": "<number>",
                "summary": "<string>",
                "model": "<string>",
                "fallback_used": "<boolean>"
            },
            "documentation": "Summarizes text using Groq LLM (llama-3.1-8b-instant)",
            "example_calls": [{
                "method": "POST",
                "body": {"text": "Long text to summarize..."},
                "output": {
                    "original_length": 500,
                    "summary": "Brief summary...",
                    "model": "llama-3.1-8b-instant",
                    "fallback_used": False
                }
            }],
            "is_public": True
        }
    )
    async def summarize_endpoint(self, request: Request):
        logger.info("=" * 80)
        logger.info("NEW SUMMARIZATION REQUEST")
        logger.info("=" * 80)
        
        try:
            # Parse JSON body
            body = await request.json()
            text = body.get("text", "")
            
            if not text:
                logger.error("No text provided in request")
                return JSONResponseCORS({"error": "No text provided"}, status_code=400)
            
            original_length = len(text)
            logger.info(f"Received text with {original_length} characters")
            
            # Try LLM summarization
            try:
                logger.info("-" * 80)
                logger.info("CALLING GROQ LLM API")
                logger.info("-" * 80)
                
                prompt = f"""Provide a concise summary of the following text in 2-3 sentences. Focus on the main ideas and key points.

Text to summarize:
{text}

Summary:"""
                
                logger.info(f"Using model: llama-3.1-8b-instant")
                
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.5,
                    max_tokens=200,
                )
                
                summary = chat_completion.choices[0].message.content.strip()
                
                logger.info(f"LLM Response received: {len(summary)} characters")
                logger.info(f"Summary: {summary[:100]}...")
                
                result = {
                    "original_length": original_length,
                    "summary": summary,
                    "model": "llama-3.1-8b-instant",
                    "fallback_used": False
                }
                
                logger.info("=" * 80)
                logger.info("SUMMARIZATION COMPLETE (LLM)")
                logger.info("=" * 80)
                
                return JSONResponseCORS(result)
                
            except Exception as llm_error:
                # Fallback behavior if LLM fails
                logger.error(f"LLM API failed: {str(llm_error)}")
                logger.info("Using fallback summarization")
                
                # Simple fallback: return first 200 chars + "..."
                if original_length <= 200:
                    fallback_summary = text
                else:
                    fallback_summary = text[:200] + "..."
                
                result = {
                    "original_length": original_length,
                    "summary": fallback_summary,
                    "model": "fallback",
                    "fallback_used": True,
                    "error": str(llm_error)
                }
                
                logger.info("=" * 80)
                logger.info("SUMMARIZATION COMPLETE (FALLBACK)")
                logger.info("=" * 80)
                
                return JSONResponseCORS(result)
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return JSONResponseCORS({
                "error": "Internal server error",
                "details": str(e)
            }, status_code=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    server = LLMSummarizerAIM()
    server.run(uvicorn_kwargs={"host": "0.0.0.0", "port": port})

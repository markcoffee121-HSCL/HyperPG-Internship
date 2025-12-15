"""
Research Agent AIM - Web research and source evaluation service
Port: 9060
"""

from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
from research_engine import ResearchEngine
import os
from dotenv import load_dotenv

load_dotenv()


class ResearchAIM(SimpleServer):
    """
    Research Agent that performs intelligent web research
    """
    
    manifest = {
        "name": "Research Agent",
        "short_name": "research",
        "version": "1.0.0",
        "documentation_url": "https://github.com/markcoffee121-HSCL/HyperPG-Internship",
        "license": "MIT",
        "terms_of_service": "",
        "author": "Raijin - HyperPG Capstone"
    }
    
    def __init__(self):
        super().__init__()
        
        groq_key = os.getenv('GROQ_API_KEY')
        serp_key = os.getenv('SERPAPI_KEY')
        
        if not groq_key or not serp_key:
            print("WARNING: API keys not configured. Research will fail.")
            self.engine = None
        else:
            self.engine = ResearchEngine(groq_key, serp_key)
            print("[Research AIM] Initialized with API keys")
    
    @aim_uri(
        uri="/health",
        methods=["GET"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {},
            "output": {"status": "string", "aim": "string", "version": "string"},
            "documentation": "Health check endpoint",
            "example_calls": [{
                "method": "GET",
                "output": {"status": "healthy", "aim": "ResearchAIM", "version": "1.0.0"}
            }],
            "is_public": True
        }
    )
    async def health(self, request):
        """Health check endpoint"""
        return JSONResponseCORS({
            "status": "healthy",
            "aim": "ResearchAIM",
            "version": "1.0.0",
            "engine_status": "ready" if self.engine else "not_configured"
        })
    
    @aim_uri(
        uri="/research",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {
                "topic": "<string>",
                "max_sources": "<integer, optional, default=10>"
            },
            "output": {
                "topic": "string",
                "sub_queries": ["string"],
                "sources": [{"link": "string", "title": "string", "snippet": "string", "credibility_score": "float"}],
                "key_findings": ["string"],
                "confidence_score": "float",
                "total_sources_analyzed": "integer"
            },
            "documentation": "Performs comprehensive web research on a topic. Returns ranked sources, key findings, and confidence score.",
            "example_calls": [{
                "method": "POST",
                "body": {"topic": "blockchain scalability solutions", "max_sources": 5},
                "output": {
                    "topic": "blockchain scalability solutions",
                    "sub_queries": ["Layer 2 solutions", "Sharding techniques"],
                    "sources": [],
                    "key_findings": ["Layer 2 solutions show promise"],
                    "confidence_score": 0.85,
                    "total_sources_analyzed": 20
                }
            }],
            "is_public": True
        }
    )
    async def research_endpoint(self, request):
        """
        Main research endpoint
        
        Accepts JSON: {"topic": "string", "max_sources": int}
        Returns research results with sources and findings
        """
        try:
            if not self.engine:
                return JSONResponseCORS({
                    "error": "Research engine not configured. Missing API keys."
                }, status_code=500)
            
            try:
                body = await request.json()
            except Exception as e:
                return JSONResponseCORS({
                    "error": "Invalid JSON in request body",
                    "details": str(e)
                }, status_code=400)
            
            topic = body.get('topic')
            if not topic or not isinstance(topic, str) or len(topic.strip()) == 0:
                return JSONResponseCORS({
                    "error": "Missing or invalid 'topic' field. Must be non-empty string."
                }, status_code=400)
            
            max_sources = body.get('max_sources', 10)
            if not isinstance(max_sources, int) or max_sources < 1 or max_sources > 20:
                max_sources = 10  
            
            print(f"[Research AIM] Processing research request: {topic}")
            
            result = self.engine.research(topic, max_sources=max_sources)
            
            print(f"[Research AIM] Research complete. Found {len(result['sources'])} sources")
            
            return JSONResponseCORS(result)
            
        except Exception as e:
            print(f"[Research AIM] Error: {e}")
            return JSONResponseCORS({
                "error": "Research processing failed",
                "details": str(e)
            }, status_code=500)


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 4000))
    
    print(f"[Research AIM] Starting on port {port}")
    
    server = ResearchAIM()
    server.run(uvicorn_kwargs={"host": "0.0.0.0", "port": port})
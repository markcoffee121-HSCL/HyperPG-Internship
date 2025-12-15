"""
Content Analyzer AIM - Combines document and research for report planning
Port: 9070
"""

from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
from analyzer_engine import AnalyzerEngine
import os
from dotenv import load_dotenv

load_dotenv()


class AnalyzerAIM(SimpleServer):
    """
    Content Analyzer that combines document and research data
    """
    
    manifest = {
        "name": "Content Analyzer",
        "short_name": "analyzer",
        "version": "1.0.0",
        "documentation_url": "https://github.com/markcoffee121-HSCL/HyperPG-Internship",
        "license": "MIT",
        "terms_of_service": "",
        "author": "Raijin - HyperPG Capstone"
    }
    
    def __init__(self):
        super().__init__()
        
        groq_key = os.getenv('GROQ_API_KEY')
        
        if not groq_key:
            print("WARNING: GROQ_API_KEY not configured")
            self.engine = None
        else:
            self.engine = AnalyzerEngine(groq_key)
            print("[Analyzer AIM] Initialized successfully")
    
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
                "output": {"status": "healthy", "aim": "AnalyzerAIM", "version": "1.0.0"}
            }],
            "is_public": True
        }
    )
    async def health(self, request):
        """Health check endpoint"""
        return JSONResponseCORS({
            "status": "healthy",
            "aim": "AnalyzerAIM",
            "version": "1.0.0",
            "engine_status": "ready" if self.engine else "not_configured"
        })
    
    @aim_uri(
        uri="/analyze",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {
                "topic": "<string>",
                "document_text": "<string>",
                "research_data": "<object with sources and key_findings>"
            },
            "output": {
                "topic": "string",
                "document_themes": ["string"],
                "research_themes": ["string"],
                "gaps": ["string"],
                "overlaps": ["string"],
                "recommended_outline": {
                    "sections": [
                        {
                            "title": "string",
                            "topics": ["string"],
                            "priority": "string"
                        }
                    ]
                }
            },
            "documentation": "Analyzes document and research data to create report outline. Identifies themes, gaps, and generates structured outline.",
            "example_calls": [{
                "method": "POST",
                "body": {
                    "topic": "blockchain scalability",
                    "document_text": "Sample document about blockchain...",
                    "research_data": {
                        "sources": [{"title": "...", "snippet": "..."}],
                        "key_findings": ["finding 1"]
                    }
                },
                "output": {
                    "topic": "blockchain scalability",
                    "document_themes": ["layer 2", "consensus"],
                    "research_themes": ["sharding", "rollups"],
                    "gaps": ["zero-knowledge proofs"],
                    "overlaps": ["layer 2"],
                    "recommended_outline": {"sections": []}
                }
            }],
            "is_public": True
        }
    )
    async def analyze_endpoint(self, request):
        """
        Main analysis endpoint
        
        Accepts:
        {
            "topic": "string",
            "document_text": "string",
            "research_data": {
                "sources": [...],
                "key_findings": [...]
            }
        }
        """
        try:
            if not self.engine:
                return JSONResponseCORS({
                    "error": "Analyzer engine not configured. Missing API key."
                }, status_code=500)
            
            # Parse request
            try:
                body = await request.json()
            except Exception as e:
                return JSONResponseCORS({
                    "error": "Invalid JSON in request body",
                    "details": str(e)
                }, status_code=400)
            
            # Validate required fields
            topic = body.get('topic')
            document_text = body.get('document_text')
            research_data = body.get('research_data')
            
            if not topic or not isinstance(topic, str):
                return JSONResponseCORS({
                    "error": "Missing or invalid 'topic' field"
                }, status_code=400)
            
            if not document_text or not isinstance(document_text, str):
                return JSONResponseCORS({
                    "error": "Missing or invalid 'document_text' field"
                }, status_code=400)
            
            if not research_data or not isinstance(research_data, dict):
                return JSONResponseCORS({
                    "error": "Missing or invalid 'research_data' field"
                }, status_code=400)
            
            print(f"[Analyzer AIM] Processing analysis for: {topic}")
            
            # Perform analysis
            result = self.engine.analyze(
                topic=topic,
                document_text=document_text,
                research_data=research_data
            )
            
            print(f"[Analyzer AIM] Analysis complete. Generated {len(result['recommended_outline']['sections'])} sections")
            
            return JSONResponseCORS(result)
            
        except Exception as e:
            print(f"[Analyzer AIM] Error: {e}")
            return JSONResponseCORS({
                "error": "Analysis failed",
                "details": str(e)
            }, status_code=500)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 4000))
    
    print(f"[Analyzer AIM] Starting on port {port}")
    
    server = AnalyzerAIM()
    server.run(uvicorn_kwargs={"host": "0.0.0.0", "port": port})
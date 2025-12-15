"""
Report Writer AIM - Generates comprehensive professional reports
Port: 9080
"""

from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
from writer_engine import WriterEngine
import os
from dotenv import load_dotenv

load_dotenv()


class WriterAIM(SimpleServer):
    """
    Report Writer that generates professional reports from outlines
    """
    
    manifest = {
        "name": "Report Writer",
        "short_name": "writer",
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
            self.engine = WriterEngine(groq_key)
            print("[Writer AIM] Initialized successfully")
    
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
                "output": {"status": "healthy", "aim": "WriterAIM", "version": "1.0.0"}
            }],
            "is_public": True
        }
    )
    async def health(self, request):
        """Health check endpoint"""
        return JSONResponseCORS({
            "status": "healthy",
            "aim": "WriterAIM",
            "version": "1.0.0",
            "engine_status": "ready" if self.engine else "not_configured"
        })
    
    @aim_uri(
        uri="/write",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {
                "topic": "<string>",
                "outline": "<object with sections array>",
                "research_data": "<object with sources and key_findings>",
                "document_text": "<string, optional>"
            },
            "output": {
                "topic": "string",
                "executive_summary": "string",
                "sections": ["string"],
                "references": "string",
                "markdown": "string",
                "html": "string",
                "metadata": {
                    "word_count": "integer",
                    "section_count": "integer",
                    "source_count": "integer"
                }
            },
            "documentation": "Generates comprehensive professional report from outline and research data. Returns report in markdown and HTML formats with citations.",
            "example_calls": [{
                "method": "POST",
                "body": {
                    "topic": "blockchain scalability",
                    "outline": {"sections": [{"title": "Introduction", "topics": ["background"], "priority": "high"}]},
                    "research_data": {"sources": [], "key_findings": []},
                    "document_text": ""
                },
                "output": {
                    "topic": "blockchain scalability",
                    "markdown": "# Report...",
                    "metadata": {"word_count": 1200}
                }
            }],
            "is_public": True
        }
    )
    async def write_endpoint(self, request):
        """
        Main report writing endpoint
        
        Accepts:
        {
            "topic": "string",
            "outline": {
                "sections": [
                    {"title": "...", "topics": [...], "priority": "..."}
                ]
            },
            "research_data": {
                "sources": [...],
                "key_findings": [...]
            },
            "document_text": "optional string"
        }
        """
        try:
            if not self.engine:
                return JSONResponseCORS({
                    "error": "Writer engine not configured. Missing API key."
                }, status_code=500)
            
            try:
                body = await request.json()
            except Exception as e:
                return JSONResponseCORS({
                    "error": "Invalid JSON in request body",
                    "details": str(e)
                }, status_code=400)
            
            topic = body.get('topic')
            outline = body.get('outline')
            research_data = body.get('research_data')
            document_text = body.get('document_text', '')
            
            if not topic or not isinstance(topic, str):
                return JSONResponseCORS({
                    "error": "Missing or invalid 'topic' field"
                }, status_code=400)
            
            if not outline or not isinstance(outline, dict):
                return JSONResponseCORS({
                    "error": "Missing or invalid 'outline' field"
                }, status_code=400)
            
            if not research_data or not isinstance(research_data, dict):
                return JSONResponseCORS({
                    "error": "Missing or invalid 'research_data' field"
                }, status_code=400)
            
            if 'sections' not in outline or not isinstance(outline['sections'], list):
                return JSONResponseCORS({
                    "error": "Outline must contain 'sections' array"
                }, status_code=400)
            
            print(f"[Writer AIM] Generating report for: {topic}")
            print(f"[Writer AIM] Sections to write: {len(outline['sections'])}")
            
            report = self.engine.write_report(
                topic=topic,
                outline=outline,
                research_data=research_data,
                document_text=document_text
            )
            
            print(f"[Writer AIM] Report complete: {report['metadata']['word_count']} words")
            
            return JSONResponseCORS(report)
            
        except Exception as e:
            print(f"[Writer AIM] Error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponseCORS({
                "error": "Report generation failed",
                "details": str(e)
            }, status_code=500)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 4000))
    
    print(f"[Writer AIM] Starting on port {port}")
    
    server = WriterAIM()
    server.run(uvicorn_kwargs={"host": "0.0.0.0", "port": port})
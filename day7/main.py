import logging
import httpx
from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
from starlette.requests import Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SummarizerAIM(SimpleServer):
    manifest = {
        "name": "SummarizerAIM",
        "short_name": "summarizer",
        "version": "1.0.0",
        "author": "Raijin - HyperPG Intern",
        "license": "MIT",
        "documentation_url": "",
        "terms_of_service": ""
    }

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
                "output": {"status": "healthy", "aim": "SummarizerAIM", "version": "1.0.0"}
            }],
            "is_public": True
        }
    )
    async def health_endpoint(self, request):
        logger.info("Health check requested")
        return JSONResponseCORS({
            "status": "healthy",
            "aim": "SummarizerAIM",
            "version": "1.0.0"
        })

    @aim_uri(
        uri="/summarize",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_headers": {},
            "input_body": {"file": "<multipart file>"},
            "output": {
                "file_analysis": "<object>",
                "summary": "<string>",
                "aim_chain": "<array>"
            },
            "documentation": "Accepts a file, sends to File Processor AIM, returns combined analysis",
            "example_calls": [{
                "method": "POST",
                "body": "multipart file upload",
                "output": {
                    "file_analysis": {"line_count": 10, "word_count": 50},
                    "summary": "File processed successfully",
                    "aim_chain": ["SummarizerAIM", "FileProcessorAIM"]
                }
            }],
            "is_public": True
        }
    )
    async def summarize_endpoint(self, request: Request):
        logger.info("=" * 80)
        logger.info("NEW REQUEST TO SUMMARIZER AIM")
        logger.info("=" * 80)
        
        try:
            # Parse multipart form data
            form = await request.form()
            file = form.get("file")
            
            if not file:
                logger.error("No file provided in request")
                return JSONResponseCORS({"error": "No file provided"}, status_code=400)
            
            filename = file.filename
            file_content = await file.read()
            
            logger.info(f"Received file: {filename}")
            logger.info(f"File size: {len(file_content)} bytes")
            
            # Call File Processor AIM
            logger.info("-" * 80)
            logger.info("CALLING FILE PROCESSOR AIM (localhost:9030/process)")
            logger.info("-" * 80)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": (filename, file_content, "text/plain")}
                
                logger.info(f"Sending request to http://172.17.0.1:8000/aim/30/process")
                response = await client.post(
                    "http://172.17.0.1:8000/aim/30/process",
                    files=files
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response body: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"File Processor returned error: {response.text}")
                return JSONResponseCORS({
                    "error": "File Processor AIM failed",
                    "details": response.text
                }, status_code=500)
            
            file_analysis = response.json()
            
            # Generate summary based on analysis
            line_count = file_analysis.get("line_count", 0)
            word_count = file_analysis.get("word_count", 0)
            
            if line_count == 0:
                summary = "Empty file received"
            elif line_count < 10:
                summary = f"Short file with {line_count} lines and {word_count} words"
            elif line_count < 100:
                summary = f"Medium file with {line_count} lines and {word_count} words"
            else:
                summary = f"Large file with {line_count} lines and {word_count} words"
            
            logger.info("-" * 80)
            logger.info("GENERATING RESPONSE")
            logger.info("-" * 80)
            logger.info(f"Summary: {summary}")
            
            result = {
                "file_analysis": file_analysis,
                "summary": summary,
                "aim_chain": ["SummarizerAIM", "FileProcessorAIM"]
            }
            
            logger.info("=" * 80)
            logger.info("REQUEST COMPLETE")
            logger.info("=" * 80)
            
            return JSONResponseCORS(result)
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return JSONResponseCORS({
                "error": "Internal server error",
                "details": str(e)
            }, status_code=500)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 4000))
    server = SummarizerAIM()
    server.run(uvicorn_kwargs={"host": "0.0.0.0", "port": port})

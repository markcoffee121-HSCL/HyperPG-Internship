from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
from starlette.requests import Request
from starlette.responses import Response
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


class FileProcessorAIM(SimpleServer):
    """
    File Processor AIM - Day 6
    Accepts text file uploads and returns analysis (line count, word count)
    """
    
    manifest = {
        "name": "FileProcessorAIM",
        "short_name": "fileprocessor",
        "version": "1.0.0",
        "author": "Raijin - HyperPG Internship Day 6",
        "license": "MIT",
        "documentation_url": "https://github.com/markcoffee121-HSCL/HyperPG-Internship",
        "terms_of_service": "",
    }

    @aim_uri(
        uri="/health",
        methods=["GET"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {},
            "output": {"status": "<string>", "aim": "<string>"},
            "documentation": "Health check endpoint for monitoring AIM status.",
            "example_calls": [{
                "method": "GET",
                "output": {"status": "healthy", "aim": "FileProcessorAIM"}
            }],
            "is_public": True
        }
    )
    async def health_endpoint(self, request: Request):
        """Health check endpoint"""
        logger.info("Health check requested")
        return JSONResponseCORS({
            "status": "healthy",
            "aim": "FileProcessorAIM",
            "version": "1.0.0"
        })

    @aim_uri(
        uri="/process",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {"file": "<file>"},
            "output": {
                "filename": "<string>",
                "line_count": "<int>",
                "word_count": "<int>",
                "file_size_bytes": "<int>"
            },
            "documentation": "Accepts a text file upload and returns analysis including line count and word count.",
            "example_calls": [{
                "method": "POST",
                "body": "multipart/form-data with 'file' field",
                "output": {
                    "filename": "example.txt",
                    "line_count": 42,
                    "word_count": 284,
                    "file_size_bytes": 1458
                }
            }],
            "is_public": True
        }
    )
    async def process_endpoint(self, request: Request):
        """
        Process uploaded text file and return analysis
        Phase 3: Complete text analysis implementation
        """
        try:
            logger.info("File processing request received")
            
            # Parse multipart form data
            form = await request.form()
            
            # Check if file exists in request
            if "file" not in form:
                logger.warning("No file provided in request")
                return JSONResponseCORS({
                    "error": "No file provided",
                    "details": "Request must include a 'file' field with multipart/form-data"
                }, status_code=400)
            
            # Extract file from form
            uploaded_file = form["file"]
            
            # Get filename
            filename = uploaded_file.filename
            logger.info(f"Processing file: {filename}")
            
            # Read file content
            file_content = await uploaded_file.read()
            file_size = len(file_content)
            
            # Check file size
            if file_size > MAX_FILE_SIZE:
                logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
                return JSONResponseCORS({
                    "error": "File too large",
                    "details": f"Maximum file size is {MAX_FILE_SIZE / (1024*1024)}MB"
                }, status_code=413)
            
            # Check for empty file
            if file_size == 0:
                logger.info(f"Empty file received: {filename}")
                return JSONResponseCORS({
                    "filename": filename,
                    "line_count": 0,
                    "word_count": 0,
                    "file_size_bytes": 0
                })
            
            # Attempt to decode as UTF-8 text
            try:
                text_content = file_content.decode('utf-8')
                logger.info(f"File decoded as UTF-8 successfully")
            except UnicodeDecodeError:
                logger.warning(f"File is not valid UTF-8 text: {filename}")
                return JSONResponseCORS({
                    "error": "Invalid text file",
                    "details": "File must be valid UTF-8 encoded text. Binary files are not supported."
                }, status_code=400)
            
            # Analyze text content
            line_count = self._count_lines(text_content)
            word_count = self._count_words(text_content)
            
            logger.info(f"Analysis complete: {filename} - {line_count} lines, {word_count} words")
            
            # Return complete analysis
            return JSONResponseCORS({
                "filename": filename,
                "line_count": line_count,
                "word_count": word_count,
                "file_size_bytes": file_size
            })
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return JSONResponseCORS({
                "error": "Internal server error",
                "details": str(e)
            }, status_code=500)
    
    def _count_lines(self, text: str) -> int:
        """
        Count lines in text content.
        Handles different line endings: \n, \r\n, \r
        """
        if not text:
            return 0
        
        # Normalize line endings to \n
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split by newline and count non-empty result
        lines = text.split('\n')
        
        # Count lines (including last line if it doesn't end with newline)
        # If text ends with newline, don't count the empty string after it
        if text.endswith('\n'):
            return len(lines) - 1 if lines[-1] == '' else len(lines)
        else:
            return len(lines)
    
    def _count_words(self, text: str) -> int:
        """
        Count words in text content.
        Words are defined as sequences of non-whitespace characters.
        """
        if not text:
            return 0
        
        # Split by whitespace and filter out empty strings
        words = text.split()
        
        return len(words)


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8000))  # Use PORT env var, default to 8000
    server = FileProcessorAIM()
    logger.info(f"Starting FileProcessorAIM server on port {port}...")
    server.run(uvicorn_kwargs={"port": port, "host": "0.0.0.0"})
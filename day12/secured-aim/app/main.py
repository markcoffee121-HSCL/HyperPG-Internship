import os
import logging
from typing import Optional
from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security Configuration
VALID_API_KEYS = {
    os.getenv("API_KEY_1", "test-key-123"),
    os.getenv("API_KEY_2", "test-key-456"),
    os.getenv("API_KEY_3", "test-key-789")
}

# Simple rate limiting tracker (in-memory)
request_counts = {}
MAX_REQUESTS_PER_MINUTE = 10

class SecuredAIMServer(SimpleServer):
    """
    Secured AIM with:
    - API key authentication
    - Basic rate limiting
    - Request validation
    """
    
    manifest = {
        "name": "SecuredAIM",
        "short_name": "securedaim",
        "version": "1.0.0",
        "documentation_url": "https://example.com/docs",
        "license": "MIT",
        "terms_of_service": "",
        "author": "HyperPG Intern"
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("SecuredAIM initialized with authentication")
    
    def validate_api_key(self, request) -> Optional[str]:
        """
        Validate API key from request headers
        Returns the API key if valid, None if invalid
        """
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            logger.warning(f"Missing API key from {request.client.host}")
            return None
        
        if api_key not in VALID_API_KEYS:
            logger.warning(f"Invalid API key attempted from {request.client.host}")
            return None
        
        logger.info(f"Valid API key from {request.client.host}")
        return api_key
    
    def check_rate_limit(self, ip_address: str) -> bool:
        """Simple rate limiting check"""
        import time
        current_time = int(time.time() / 60)  # Current minute
        
        key = f"{ip_address}:{current_time}"
        request_counts[key] = request_counts.get(key, 0) + 1
        
        # Clean old entries
        old_keys = [k for k in request_counts.keys() if not k.endswith(str(current_time))]
        for k in old_keys:
            del request_counts[k]
        
        return request_counts[key] <= MAX_REQUESTS_PER_MINUTE
    
    @aim_uri(
        uri="/public/info",
        methods=["GET"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {},
            "output": {"message": "<string>", "version": "<string>"},
            "documentation": "Public endpoint - no authentication required",
            "example_calls": [{
                "method": "GET",
                "query": "",
                "output": {"message": "SecuredAIM v1.0.0", "version": "1.0.0"}
            }],
            "is_public": True
        }
    )
    async def public_info(self, request):
        """Public endpoint - no auth required"""
        logger.info("Public info endpoint accessed")
        return JSONResponseCORS({
            "message": "SecuredAIM v1.0.0 - Authentication and rate limiting enabled",
            "version": "1.0.0",
            "security": {
                "authentication": "API key required for protected endpoints",
                "rate_limiting": "10 requests per minute per IP"
            }
        })
    
    @aim_uri(
        uri="/protected/greet",
        methods=["GET"],
        endpoint_manifest={
            "input_query": {"name": "<string>"},
            "input_body": {},
            "output": {"message": "<string>", "authenticated": "<boolean>"},
            "documentation": "Protected endpoint - requires valid API key in X-API-Key header",
            "example_calls": [{
                "method": "GET",
                "query": "?name=User",
                "headers": {"X-API-Key": "your-api-key"},
                "output": {"message": "Hello, User!", "authenticated": True}
            }],
            "is_public": False
        }
    )
    async def protected_greet(self, request):
        """Protected endpoint with authentication and rate limiting"""
        # Check rate limit
        if not self.check_rate_limit(request.client.host):
            logger.warning(f"Rate limit exceeded for {request.client.host}")
            return JSONResponseCORS({
                "error": "Rate limit exceeded. Maximum 10 requests per minute."
            }, status_code=429)
        
        # Validate API key
        api_key = self.validate_api_key(request)
        if not api_key:
            return JSONResponseCORS({
                "error": "Missing or invalid API key. Please provide X-API-Key header."
            }, status_code=401)
        
        # Get name parameter
        name = request.query_params.get("name", "stranger")
        
        logger.info(f"Protected greet endpoint accessed for name: {name}")
        
        return JSONResponseCORS({
            "message": f"Hello, {name}! You are authenticated.",
            "authenticated": True,
            "rate_limit_info": "10 requests per minute"
        })
    
    @aim_uri(
        uri="/protected/process",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {"data": "<string>"},
            "output": {
                "processed_data": "<string>",
                "length": "<int>",
                "authenticated": "<boolean>"
            },
            "documentation": "Protected POST endpoint - requires valid API key and processes input data",
            "example_calls": [{
                "method": "POST",
                "body": {"data": "test input"},
                "headers": {"X-API-Key": "your-api-key"},
                "output": {
                    "processed_data": "PROCESSED: test input",
                    "length": 10,
                    "authenticated": True
                }
            }],
            "is_public": False
        }
    )
    async def protected_process(self, request):
        """Protected POST endpoint with data validation"""
        # Check rate limit
        if not self.check_rate_limit(request.client.host):
            logger.warning(f"Rate limit exceeded for {request.client.host}")
            return JSONResponseCORS({
                "error": "Rate limit exceeded. Maximum 10 requests per minute."
            }, status_code=429)
        
        # Validate API key
        api_key = self.validate_api_key(request)
        if not api_key:
            return JSONResponseCORS({
                "error": "Missing or invalid API key. Please provide X-API-Key header."
            }, status_code=401)
        
        # Parse and validate request body
        try:
            body = await request.json()
        except Exception as e:
            logger.error(f"Invalid JSON in request body: {e}")
            return JSONResponseCORS({
                "error": "Invalid JSON in request body"
            }, status_code=400)
        
        # Validate required fields
        if "data" not in body:
            logger.error("Missing 'data' field in request body")
            return JSONResponseCORS({
                "error": "Missing required field: 'data'"
            }, status_code=400)
        
        data = body["data"]
        
        # Validate data type
        if not isinstance(data, str):
            logger.error(f"Invalid data type: {type(data)}")
            return JSONResponseCORS({
                "error": "Field 'data' must be a string"
            }, status_code=400)
        
        # Process the data
        processed = f"PROCESSED: {data}"
        
        logger.info(f"Protected process endpoint: processed {len(data)} characters")
        
        return JSONResponseCORS({
            "processed_data": processed,
            "length": len(data),
            "authenticated": True
        })


if __name__ == '__main__':
    port = int(os.getenv("PORT", "4000"))
    server = SecuredAIMServer()
    logger.info(f"Starting SecuredAIM on port {port}")
    logger.info(f"Valid API keys configured: {len(VALID_API_KEYS)}")
    server.run(uvicorn_kwargs={"host": "0.0.0.0", "port": port})
from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
import hashlib
import time

class FileProcessorAIM(SimpleServer):
    """
    File Processor AIM with Response Caching
    Analyzes text files and returns statistics
    """
    
    manifest = {
        "name": "FileProcessorAIM",
        "short_name": "fileprocessor",
        "version": "1.0.1",
        "author": "HyperPG Intern",
        "license": "MIT",
        "documentation_url": "",
        "terms_of_service": ""
    }
    
    def __init__(self):
        super().__init__()
        # In-memory cache with TTL
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes in seconds
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _get_cache_key(self, content: bytes) -> str:
        """Generate a hash key for cache lookup"""
        return hashlib.sha256(content).hexdigest()
    
    def _get_from_cache(self, cache_key: str):
        """Get result from cache if not expired"""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                self.cache_hits += 1
                print(f"[CACHE HIT] Hits: {self.cache_hits}, Misses: {self.cache_misses}")
                return result
            else:
                del self.cache[cache_key]
        
        self.cache_misses += 1
        print(f"[CACHE MISS] Hits: {self.cache_hits}, Misses: {self.cache_misses}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: dict):
        """Save result to cache with timestamp"""
        self.cache[cache_key] = (result, time.time())
        print(f"[CACHE SAVED] Cache size: {len(self.cache)}")
    
    @aim_uri(
        uri="/health",
        methods=["GET"],
        endpoint_manifest={
            "input_query": {},
            "input_headers": {},
            "input_body": {},
            "output": {"status": "<string>"},
            "documentation": "Health check with cache stats",
            "example_calls": [{}],
            "is_public": True
        }
    )
    async def health_check(self, request):
        return JSONResponseCORS({
            "status": "healthy",
            "aim": "FileProcessorAIM",
            "version": "1.0.1",
            "cache_stats": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "size": len(self.cache)
            }
        })
    
    @aim_uri(
        uri="/process",
        methods=["POST"],
        endpoint_manifest={
            "input_body": {"file": "<file>"},
            "output": {
                "filename": "<string>",
                "line_count": "<int>",
                "word_count": "<int>",
                "file_size_bytes": "<int>",
                "cached": "<boolean>"
            },
            "documentation": "Process text file with caching",
            "example_calls": [{}],
            "is_public": True
        }
    )
    async def process_file(self, request):
        form = await request.form()
        file = form.get('file')
        
        if not file:
            return JSONResponseCORS({"error": "No file provided"}, status_code=400)
        
        content = await file.read()
        
        if len(content) == 0:
            return JSONResponseCORS({"error": "File is empty"}, status_code=400)
        
        # Check cache
        cache_key = self._get_cache_key(content)
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result:
            cached_result['filename'] = file.filename
            cached_result['cached'] = True
            return JSONResponseCORS(cached_result)
        
        # Process file
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            return JSONResponseCORS({"error": "Invalid UTF-8"}, status_code=400)
        
        lines = text.split('\n')
        words = text.split()
        
        result = {
            "filename": file.filename,
            "line_count": len(lines),
            "word_count": len(words),
            "file_size_bytes": len(content),
            "cached": False
        }
        
        self._save_to_cache(cache_key, result)
        return JSONResponseCORS(result)

if __name__ == '__main__':
    server = FileProcessorAIM()
    server.run()

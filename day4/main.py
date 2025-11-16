from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS

class MyHelloAIM(SimpleServer):
    """
    A simple AIM that responds with 'Hello Node!' on POST /run endpoint.
    """
    
    manifest = {
        "name": "MyHelloAIM",
        "short_name": "hello-aim",
        "version": "1.0.0",
        "documentation_url": "https://github.com/markcoffee121-HSCL/HyperPG-Internship",
        "license": "MIT",
        "terms_of_service": "",
        "author": "Raijin - HyperPG Intern"
    }
    
    @aim_uri(
        uri="/run",
        methods=["POST"],
        endpoint_manifest={
            "input_query": {},
            "input_body": {},
            "output": {"message": "<string>"},
            "documentation": "Returns 'Hello Node!' message",
            "example_calls": [{
                "method": "POST",
                "body": {},
                "output": {"message": "Hello Node!"}
            }],
            "is_public": True
        }
    )
    async def run_endpoint(self, request):
        """POST /run endpoint that returns Hello Node!"""
        return JSONResponseCORS({"message": "Hello Node!"})

if __name__ == '__main__':
    server = MyHelloAIM()
    # Port 4000 is expected by Node Manager (set via PORT env var in Docker)
    server.run(uvicorn_kwargs={"port": 4000, "host": "0.0.0.0"})

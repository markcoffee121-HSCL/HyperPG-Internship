"""
Query Decomposer - Breaks complex topics into focused sub-queries
Uses Groq LLM for intelligent query generation
"""

from groq import Groq
import json
from typing import List


class QueryDecomposer:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        
    def decompose(self, topic: str, max_queries: int = 3) -> List[str]:
        """
        Break a complex topic into focused sub-queries
        
        Args:
            topic: The main research topic
            max_queries: Maximum number of sub-queries to generate
            
        Returns:
            List of focused search queries
        """
        try:
            prompt = f"""You are a research assistant. Break down this research topic into {max_queries} focused, specific search queries that will help gather comprehensive information.

Topic: {topic}

Requirements:
- Each query should be specific and searchable
- Queries should cover different aspects of the topic
- Use clear, concise language
- Return ONLY a JSON array of strings, no explanation

Example format: ["query 1", "query 2", "query 3"]

Your response:"""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                queries = json.loads(result)
                if isinstance(queries, list) and len(queries) > 0:
                    return queries[:max_queries]
            except json.JSONDecodeError:
                # Fallback: extract queries from text
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                queries = []
                for line in lines:
                    # Remove numbers, bullets, quotes
                    clean = line.strip('0123456789.-"\'[] ')
                    if clean:
                        queries.append(clean)
                
                if queries:
                    return queries[:max_queries]
            
            # Ultimate fallback: use original topic
            return [topic]
            
        except Exception as e:
            print(f"Query decomposition error: {e}")
            # Fallback to original topic
            return [topic]


if __name__ == "__main__":
    # Test the decomposer
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment")
        exit(1)
    
    decomposer = QueryDecomposer(api_key)
    
    # Test cases
    test_topics = [
        "blockchain scalability solutions",
        "artificial intelligence ethics",
        "climate change mitigation strategies"
    ]
    
    for topic in test_topics:
        print(f"\nTopic: {topic}")
        queries = decomposer.decompose(topic)
        print(f"Sub-queries ({len(queries)}):")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
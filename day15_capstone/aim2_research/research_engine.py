"""
Research Engine - Core orchestration of research workflow
Coordinates query decomposition, web search, and source evaluation
"""

from serpapi import GoogleSearch
from groq import Groq
from typing import Dict, List, Optional
from query_decomposer import QueryDecomposer
from source_evaluator import SourceEvaluator
import json


class ResearchEngine:
    def __init__(self, groq_api_key: str, serpapi_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        self.serpapi_key = serpapi_key
        self.decomposer = QueryDecomposer(groq_api_key)
        self.evaluator = SourceEvaluator()
        
    def research(self, topic: str, max_sources: int = 10) -> Dict:
        """
        Perform comprehensive research on a topic
        
        Args:
            topic: The research topic
            max_sources: Maximum sources to return
            
        Returns:
            {
                "topic": str,
                "sub_queries": [str],
                "sources": [{url, title, snippet, credibility_score}],
                "key_findings": [str],
                "confidence_score": float,
                "total_sources_analyzed": int
            }
        """
        print(f"[Research Engine] Starting research on: {topic}")
        
        sub_queries = self.decomposer.decompose(topic, max_queries=3)
        print(f"[Research Engine] Generated {len(sub_queries)} sub-queries")
        
        all_sources = []
        for query in sub_queries:
            sources = self._search_web(query, num_results=10)
            all_sources.extend(sources)
            print(f"[Research Engine] Found {len(sources)} sources for: {query}")
        
        ranked_sources = self.evaluator.rank_sources(all_sources)
        top_sources = ranked_sources[:max_sources]
        print(f"[Research Engine] Ranked sources, returning top {len(top_sources)}")
        
        key_findings = self._extract_findings(topic, top_sources)
        
        confidence = self._calculate_confidence(top_sources)
        
        return {
            "topic": topic,
            "sub_queries": sub_queries,
            "sources": top_sources,
            "key_findings": key_findings,
            "confidence_score": confidence,
            "total_sources_analyzed": len(all_sources)
        }
    
    def _search_web(self, query: str, num_results: int = 10) -> List[Dict]:
        """Perform web search using SerpAPI"""
        try:
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            sources = []
            for result in results.get("organic_results", [])[:num_results]:
                sources.append({
                    "link": result.get("link", ""),
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", "")
                })
            
            return sources
            
        except Exception as e:
            print(f"[Research Engine] Search error for '{query}': {e}")
            return []
    
    def _extract_findings(self, topic: str, sources: List[Dict]) -> List[str]:
        """Use LLM to extract key findings from sources"""
        try:
            source_text = "\n\n".join([
                f"Source {i+1}: {s['title']}\n{s['snippet']}"
                for i, s in enumerate(sources[:5])  
            ])
            
            prompt = f"""Based on these research sources about "{topic}", identify 3-5 key findings or insights.

Sources:
{source_text}

Requirements:
- Each finding should be a clear, factual statement
- Focus on the most important or recurring themes
- Be concise (1-2 sentences per finding)
- Return ONLY a JSON array of strings, no explanation

Example format: ["Finding 1", "Finding 2", "Finding 3"]

Your response:"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            try:
                findings = json.loads(result)
                if isinstance(findings, list):
                    return findings[:5]
            except json.JSONDecodeError:
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                findings = []
                for line in lines:
                    clean = line.strip('0123456789.-"\'[] ')
                    if clean and len(clean) > 20: 
                        findings.append(clean)
                return findings[:5] if findings else ["Analysis pending"]
            
        except Exception as e:
            print(f"[Research Engine] Findings extraction error: {e}")
            return ["Analysis pending"]
    
    def _calculate_confidence(self, sources: List[Dict]) -> float:
        """Calculate overall confidence score based on source quality"""
        if not sources:
            return 0.0
        
        avg_credibility = sum(s.get('credibility_score', 0.5) for s in sources) / len(sources)
        
        source_bonus = min(0.2, len(sources) * 0.02)
        
        confidence = min(1.0, avg_credibility + source_bonus)
        return round(confidence, 2)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    groq_key = os.getenv('GROQ_API_KEY')
    serp_key = os.getenv('SERPAPI_KEY')
    
    if not groq_key or not serp_key:
        print("Error: API keys not found")
        exit(1)
    
    engine = ResearchEngine(groq_key, serp_key)
    
    result = engine.research("blockchain scalability solutions", max_sources=5)
    
    print("\n=== RESEARCH RESULTS ===")
    print(f"Topic: {result['topic']}")
    print(f"\nSub-queries: {result['sub_queries']}")
    print(f"\nTop Sources ({len(result['sources'])}):")
    for i, source in enumerate(result['sources'], 1):
        print(f"{i}. [{source['credibility_score']}] {source['title']}")
    print(f"\nKey Findings:")
    for i, finding in enumerate(result['key_findings'], 1):
        print(f"{i}. {finding}")
    print(f"\nConfidence Score: {result['confidence_score']}")
    print(f"Total Sources Analyzed: {result['total_sources_analyzed']}")
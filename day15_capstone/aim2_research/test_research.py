"""
Test script for Research Agent AIM
Tests all components before containerization
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("RESEARCH AGENT AIM - COMPONENT TESTS")
print("=" * 60)

print("\n[TEST 1] Query Decomposer")
print("-" * 60)
try:
    from query_decomposer import QueryDecomposer
    
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("FAIL: GROQ_API_KEY not found")
    else:
        decomposer = QueryDecomposer(groq_key)
        topic = "artificial intelligence safety"
        queries = decomposer.decompose(topic, max_queries=3)
        
        print(f"Topic: {topic}")
        print(f"Generated {len(queries)} sub-queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        print("PASS: Query decomposition working")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 2] Source Evaluator")
print("-" * 60)
try:
    from source_evaluator import SourceEvaluator
    
    evaluator = SourceEvaluator()
    
    test_sources = [
        {
            'link': 'https://www.reuters.com/tech-news',
            'title': 'Tech Breakthrough',
            'snippet': 'Research shows...'
        },
        {
            'link': 'https://reddit.com/r/technology',
            'title': 'User Discussion',
            'snippet': 'People are saying...'
        }
    ]
    
    ranked = evaluator.rank_sources(test_sources)
    print("Ranked sources:")
    for i, source in enumerate(ranked, 1):
        print(f"  {i}. Score: {source['credibility_score']} - {source['link']}")
    
    print("PASS: Source evaluation working")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 3] Research Engine (Full Integration)")
print("-" * 60)
try:
    from research_engine import ResearchEngine
    
    groq_key = os.getenv('GROQ_API_KEY')
    serp_key = os.getenv('SERPAPI_KEY')
    
    if not groq_key or not serp_key:
        print("FAIL: API keys not configured")
    else:
        engine = ResearchEngine(groq_key, serp_key)
        
        test_topic = "quantum computing advances"
        print(f"Researching: {test_topic}")
        print("(This may take 15-30 seconds...)")
        
        result = engine.research(test_topic, max_sources=5)
        
        print(f"\nResults:")
        print(f"  Topic: {result['topic']}")
        print(f"  Sub-queries: {result['sub_queries']}")
        print(f"  Sources found: {len(result['sources'])}")
        print(f"  Total analyzed: {result['total_sources_analyzed']}")
        print(f"  Confidence: {result['confidence_score']}")
        
        if result['sources']:
            print(f"\n  Top source:")
            top = result['sources'][0]
            print(f"    [{top['credibility_score']}] {top['title']}")
            print(f"    {top['link']}")
        
        if result['key_findings']:
            print(f"\n  Key findings:")
            for i, finding in enumerate(result['key_findings'][:2], 1):
                print(f"    {i}. {finding[:80]}...")
        
        print("\nPASS: Research engine working")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST 4] API Endpoints (Manual Test)")
print("-" * 60)
print("After deployment, test with:")
print("")
print("  # Health check")
print("  curl http://localhost:9060/health")
print("")
print("  # Research request")
print('  curl -X POST http://localhost:9060/research \\')
print('    -H "Content-Type: application/json" \\')
print('    -d \'{"topic": "blockchain scalability", "max_sources": 5}\'')
print("")

print("\n" + "=" * 60)
print("COMPONENT TESTING COMPLETE")
print("=" * 60)
"""
Test script for Content Analyzer AIM
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("CONTENT ANALYZER AIM - COMPONENT TESTS")
print("=" * 60)

print("\n[TEST 1] Theme Extractor")
print("-" * 60)
try:
    from theme_extractor import ThemeExtractor
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("FAIL: GROQ_API_KEY not found")
    else:
        extractor = ThemeExtractor(api_key)
        
        test_text = """
        Blockchain technology enables decentralized transactions. Smart contracts
        automate processes. Scalability remains a challenge with current consensus
        mechanisms like proof of work.
        """
        
        themes = extractor.extract_themes(test_text, max_themes=3)
        print(f"Extracted {len(themes)} themes:")
        for i, theme in enumerate(themes, 1):
            print(f"  {i}. {theme}")
        
        print("PASS: Theme extraction working")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 2] Outline Generator")
print("-" * 60)
try:
    from outline_generator import OutlineGenerator
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("FAIL: GROQ_API_KEY not found")
    else:
        generator = OutlineGenerator(api_key)
        
        outline = generator.generate_outline(
            topic="blockchain scalability",
            document_themes=["consensus mechanisms", "transaction speed"],
            research_themes=["layer 2 solutions", "sharding", "rollups"],
            gaps=["sharding", "rollups"],
            overlaps=[]
        )
        
        print(f"Generated outline with {len(outline['sections'])} sections:")
        for i, section in enumerate(outline['sections'], 1):
            print(f"  {i}. {section['title']} (priority: {section['priority']})")
        
        print("PASS: Outline generation working")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 3] Analyzer Engine (Full Integration)")
print("-" * 60)
try:
    from analyzer_engine import AnalyzerEngine
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("FAIL: GROQ_API_KEY not found")
    else:
        engine = AnalyzerEngine(api_key)
        
        doc_text = """
        Blockchain scalability is a critical issue. Current networks process 
        7-15 transactions per second. Layer 2 solutions like Lightning Network 
        show promise. Consensus mechanisms need improvement.
        """
        
        research_data = {
            "sources": [
                {
                    "title": "Ethereum Sharding Explained",
                    "snippet": "Sharding divides the blockchain into smaller pieces..."
                },
                {
                    "title": "Rollup Technologies Overview",
                    "snippet": "ZK and optimistic rollups batch transactions..."
                },
                {
                    "title": "Layer 2 Scaling Solutions",
                    "snippet": "Plasma, state channels, and sidechains..."
                }
            ],
            "key_findings": [
                "Layer 2 solutions can increase throughput 100x",
                "Sharding is coming in Ethereum 2.0"
            ]
        }
        
        print("Analyzing... (10-15 seconds)")
        
        result = engine.analyze(
            topic="blockchain scalability solutions",
            document_text=doc_text,
            research_data=research_data
        )
        
        print(f"\nResults:")
        print(f"  Document themes ({len(result['document_themes'])}): {result['document_themes'][:3]}")
        print(f"  Research themes ({len(result['research_themes'])}): {result['research_themes'][:3]}")
        print(f"  Gaps found: {len(result['gaps'])}")
        print(f"  Overlaps found: {len(result['overlaps'])}")
        print(f"  Outline sections: {len(result['recommended_outline']['sections'])}")
        
        if result['recommended_outline']['sections']:
            print(f"\n  Sample section:")
            section = result['recommended_outline']['sections'][0]
            print(f"    Title: {section['title']}")
            print(f"    Priority: {section['priority']}")
            print(f"    Topics: {len(section.get('topics', []))}")
        
        print("\nPASS: Analyzer engine working")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("COMPONENT TESTING COMPLETE")
print("=" * 60)
print("\nNext: Build Docker image and deploy to cloud")
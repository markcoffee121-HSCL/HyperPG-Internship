"""
Test script for Report Writer AIM
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("REPORT WRITER AIM - COMPONENT TESTS")
print("=" * 60)

print("\n[TEST 1] Section Generator")
print("-" * 60)
try:
    from section_generator import SectionGenerator
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("FAIL: GROQ_API_KEY not found")
    else:
        generator = SectionGenerator(api_key)
        
        context = {
            'topic': 'blockchain scalability',
            'research_sources': [
                {'title': 'Layer 2 Overview', 'snippet': 'Layer 2 solutions...'}
            ],
            'document_text': 'Blockchain faces scalability challenges.'
        }
        
        print("Generating section... (5-10 seconds)")
        section = generator.generate_section(
            section_title="Introduction",
            section_topics=["background", "scope"],
            context_data=context,
            word_target=150
        )
        
        print(f"Generated section ({len(section.split())} words):")
        print(section[:200] + "...")
        print("PASS: Section generation working")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST 2] Citation Manager")
print("-" * 60)
try:
    from citation_manager import CitationManager
    
    manager = CitationManager()
    test_sources = [
        {'title': 'Source 1', 'link': 'https://example.com/1'},
        {'title': 'Source 2', 'link': 'https://example.com/2'}
    ]
    
    manager.add_sources(test_sources)
    refs = manager.generate_references_section()
    
    print(f"Generated {manager.get_source_count()} references:")
    print(refs)
    print("PASS: Citation management working")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 3] Formatter")
print("-" * 60)
try:
    from formatter import Formatter
    
    formatter = Formatter()
    
    test_md = "# Title\n\n## Section\n\nSome content."
    
    html = formatter.to_html(test_md)
    print(f"Markdown → HTML: {len(html)} chars")
    print("HTML preview:", html[:100] + "...")
    
    test_data = {
        'topic': 'Test',
        'word_count': 500,
        'sections': ['Sec 1']
    }
    json_output = formatter.to_json(test_data)
    print(f"JSON structure: {list(json_output.keys())}")
    
    print("PASS: Formatting working")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 4] Writer Engine (Full Integration)")
print("-" * 60)
try:
    from writer_engine import WriterEngine
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("FAIL: GROQ_API_KEY not found")
    else:
        engine = WriterEngine(api_key)
        
        test_outline = {
            'sections': [
                {
                    'title': 'Introduction',
                    'topics': ['background', 'scope'],
                    'priority': 'high'
                },
                {
                    'title': 'Analysis',
                    'topics': ['current state', 'challenges'],
                    'priority': 'high'
                }
            ]
        }
        
        test_research = {
            'sources': [
                {
                    'title': 'Blockchain Scalability Report',
                    'link': 'https://example.com/report',
                    'snippet': 'Current blockchain networks face significant scalability challenges...'
                },
                {
                    'title': 'Layer 2 Solutions Guide',
                    'link': 'https://example.com/layer2',
                    'snippet': 'Layer 2 protocols offer promising improvements...'
                }
            ],
            'key_findings': [
                'Layer 2 solutions can increase throughput significantly',
                'Sharding is under active development',
                'Trade-offs exist between decentralization and scalability'
            ]
        }
        
        print("Generating full report... (30-45 seconds)")
        print("This may take a moment as multiple LLM calls are needed...\n")
        
        report = engine.write_report(
            topic="Blockchain Scalability Solutions",
            outline=test_outline,
            research_data=test_research,
            document_text="Blockchain technology faces scalability challenges. Current networks process limited transactions per second."
        )
        
        print(f"\nResults:")
        print(f"  Word count: {report['metadata']['word_count']}")
        print(f"  Sections: {report['metadata']['section_count']}")
        print(f"  Sources: {report['metadata']['source_count']}")
        
        print(f"\n  Executive Summary preview:")
        print(f"  {report['executive_summary'][:150]}...")
        
        print(f"\n  Report structure:")
        for i, section in enumerate(report['sections'][:2], 1):
            title = section.split('\n')[0].replace('#', '').strip()
            print(f"    {i}. {title}")
        
        print(f"\n  Formats available: markdown, html")
        print(f"  Markdown length: {len(report['markdown'])} chars")
        print(f"  HTML length: {len(report['html'])} chars")
        
        print("\nPASS: Writer engine working")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("COMPONENT TESTING COMPLETE")
print("=" * 60)
print("\nNext: Build Docker image and deploy to cloud")
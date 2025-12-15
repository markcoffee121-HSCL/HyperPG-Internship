"""
Test script for Pipeline Orchestrator
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("PIPELINE ORCHESTRATOR - COMPONENT TESTS")
print("=" * 60)

print("\n[TEST 1] Environment Configuration")
print("-" * 60)
try:
    required_vars = [
        'FILE_PROCESSOR_URL',
        'RESEARCH_AGENT_URL',
        'ANALYZER_URL',
        'WRITER_URL'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            print(f"✓ {var}: {value}")
    
    if missing:
        print(f"\nFAIL: Missing variables: {', '.join(missing)}")
    else:
        print("\nPASS: All environment variables configured")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 2] Orchestrator Initialization")
print("-" * 60)
try:
    from orchestrator import PipelineOrchestrator
    
    orchestrator = PipelineOrchestrator(
        file_processor_url=os.getenv('FILE_PROCESSOR_URL'),
        research_url=os.getenv('RESEARCH_AGENT_URL'),
        analyzer_url=os.getenv('ANALYZER_URL'),
        writer_url=os.getenv('WRITER_URL')
    )
    
    print("✓ Orchestrator created successfully")
    print(f"  File Processor: {orchestrator.file_processor_url}")
    print(f"  Research Agent: {orchestrator.research_url}")
    print(f"  Analyzer: {orchestrator.analyzer_url}")
    print(f"  Writer: {orchestrator.writer_url}")
    
    print("\nPASS: Orchestrator initialization working")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST 3] AIM Health Checks")
print("-" * 60)
try:
    import requests
    
    aims = [
        ('File Processor', f"{os.getenv('FILE_PROCESSOR_URL')}/health"),
        ('Research Agent', f"{os.getenv('RESEARCH_AGENT_URL')}/health"),
        ('Analyzer', f"{os.getenv('ANALYZER_URL')}/health"),
        ('Writer', f"{os.getenv('WRITER_URL')}/health")
    ]
    
    all_healthy = True
    for name, url in aims:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {name}: {data.get('status', 'unknown')}")
            else:
                print(f"✗ {name}: HTTP {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"✗ {name}: {str(e)}")
            all_healthy = False
    
    if all_healthy:
        print("\nPASS: All AIMs healthy and reachable")
    else:
        print("\nWARN: Some AIMs not reachable (may need cloud deployment)")
except Exception as e:
    print(f"FAIL: {e}")

print("\n[TEST 4] Full Pipeline Integration Test")
print("-" * 60)
print("This test requires all AIMs to be deployed and takes 60-90 seconds.")
run_full_test = input("Run full pipeline test? (y/n): ").lower().strip()

if run_full_test == 'y':
    try:
        from orchestrator import PipelineOrchestrator
        
        orchestrator = PipelineOrchestrator(
            file_processor_url=os.getenv('FILE_PROCESSOR_URL'),
            research_url=os.getenv('RESEARCH_AGENT_URL'),
            analyzer_url=os.getenv('ANALYZER_URL'),
            writer_url=os.getenv('WRITER_URL')
        )
        
        test_content = b"""
        Blockchain technology enables decentralized digital transactions without
        intermediaries. However, scalability remains a critical challenge for
        widespread adoption. Current networks like Bitcoin and Ethereum can only
        process 7-15 transactions per second, far below traditional payment systems
        like Visa which handles thousands of transactions per second.
        
        Layer 2 solutions such as Lightning Network and Plasma aim to address these
        limitations by processing transactions off-chain. Sharding is another proposed
        solution that divides the blockchain into smaller partitions.
        """
        
        print("\nRunning full pipeline...")
        print("This will call all 4 AIMs in sequence:\n")
        
        def progress_callback(msg, step, total):
            print(f"[{step}/{total}] {msg}")
        
        result = orchestrator.run_pipeline(
            file_content=test_content,
            filename="test_blockchain.txt",
            topic="blockchain scalability solutions",
            progress_callback=progress_callback
        )
        
        print("\n=== PIPELINE RESULTS ===")
        print(f"✓ Success: {result['success']}")
        print(f"✓ Document themes: {len(result['document_analysis']['themes'])}")
        print(f"✓ Research sources: {result['research_summary']['sources_found']}")
        print(f"✓ Research confidence: {result['research_summary']['confidence']}")
        print(f"✓ Report word count: {result['report']['metadata']['word_count']}")
        print(f"✓ Report sections: {result['report']['metadata']['section_count']}")
        
        print("\nExecutive Summary preview:")
        summary = result['report']['executive_summary']
        print(f"  {summary[:200]}...")
        
        print("\nPASS: Full pipeline integration working!")
        
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Skipped (run after cloud deployment)")

print("\n" + "=" * 60)
print("ORCHESTRATOR TESTING COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Build Docker image: docker build -t orchestrator:1.0 .")
print("2. Deploy to cloud")
print("3. Access web UI at http://46.101.166.187:9050")
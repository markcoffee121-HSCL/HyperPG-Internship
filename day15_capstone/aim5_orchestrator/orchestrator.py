"""
Pipeline Orchestrator - Coordinates all AIMs in sequence
Chains: File Processor → Research → Analyzer → Writer
"""

import requests
import time
from typing import Dict, Optional


class PipelineOrchestrator:
    def __init__(
        self,
        file_processor_url: str,
        research_url: str,
        analyzer_url: str,
        writer_url: str
    ):
        self.file_processor_url = file_processor_url
        self.research_url = research_url
        self.analyzer_url = analyzer_url
        self.writer_url = writer_url
        
    def run_pipeline(
        self,
        file_content: bytes,
        filename: str,
        topic: str,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Execute complete research report pipeline
        
        Args:
            file_content: Uploaded file bytes
            filename: Name of file
            topic: Research topic
            progress_callback: Function to call with progress updates
            
        Returns:
            Complete report data
        """
        try:
            if progress_callback:
                progress_callback("Processing document...", 1, 4)
            
            doc_text = self._call_file_processor(file_content, filename)
            print(f"[Orchestrator] Document extracted: {len(doc_text)} chars")
            
            if not doc_text and file_content:
                try:
                    doc_text = file_content.decode('utf-8', errors='ignore')
                    print(f"[Orchestrator] Fallback decode: {len(doc_text)} chars")
                except:
                    doc_text = "Sample document content."
            
            if progress_callback:
                progress_callback("Researching topic...", 2, 4)
            
            research_data = self._call_research_agent(topic)
            print(f"[Orchestrator] Research complete: {len(research_data.get('sources', []))} sources")
            
            if progress_callback:
                progress_callback("Analyzing content...", 3, 4)
            
            analysis = self._call_analyzer(topic, doc_text, research_data)
            print(f"[Orchestrator] Analysis complete: {len(analysis['recommended_outline']['sections'])} sections")
            
            if progress_callback:
                progress_callback("Writing report...", 4, 4)
            
            report = self._call_writer(
                topic=topic,
                outline=analysis['recommended_outline'],
                research_data=research_data,
                document_text=doc_text
            )
            print(f"[Orchestrator] Report complete: {report['metadata']['word_count']} words")
            
            return {
                "success": True,
                "topic": topic,
                "document_analysis": {
                    "text_length": len(doc_text),
                    "themes": analysis.get('document_themes', [])
                },
                "research_summary": {
                    "sources_found": len(research_data.get('sources', [])),
                    "confidence": research_data.get('confidence_score', 0)
                },
                "analysis": {
                    "gaps": analysis.get('gaps', []),
                    "overlaps": analysis.get('overlaps', [])
                },
                "report": report,
                "processing_time": "Complete"
            }
            
        except Exception as e:
            print(f"[Orchestrator] Pipeline error: {e}")
            raise
    
    def _call_file_processor(self, file_content: bytes, filename: str) -> str:
        """Call File Processor AIM to extract text"""
        try:
            files = {'file': (filename, file_content)}
            response = requests.post(
                f'{self.file_processor_url}/process',
                files=files,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"[Orchestrator] File processor returned {response.status_code}")
                try:
                    return file_content.decode('utf-8', errors='ignore')
                except:
                    raise Exception(f"File processor failed: {response.text}")
            
            data = response.json()
            
            text = (
                data.get('content') or 
                data.get('text') or 
                data.get('file_content') or 
                data.get('extracted_text') or
                ''
            )
            
            if not text and file_content:
                try:
                    text = file_content.decode('utf-8', errors='ignore')
                    print(f"[Orchestrator] Using direct decode fallback")
                except Exception as e:
                    print(f"[Orchestrator] Decode failed: {e}")
                    pass
            
            return text
            
        except Exception as e:
            print(f"[Orchestrator] File processor error, using fallback: {e}")
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                raise Exception(f"File processor error: {e}")
    
    def _call_research_agent(self, topic: str) -> Dict:
        """Call Research Agent AIM"""
        try:
            response = requests.post(
                f'{self.research_url}/research',
                json={"topic": topic, "max_sources": 10},
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Research agent failed: {response.text}")
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Research agent error: {e}")
    
    def _call_analyzer(self, topic: str, doc_text: str, research_data: Dict) -> Dict:
        """Call Content Analyzer AIM"""
        try:
            response = requests.post(
                f'{self.analyzer_url}/analyze',
                json={
                    "topic": topic,
                    "document_text": doc_text,
                    "research_data": research_data
                },
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Analyzer failed: {response.text}")
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Analyzer error: {e}")
    
    def _call_writer(
        self,
        topic: str,
        outline: Dict,
        research_data: Dict,
        document_text: str
    ) -> Dict:
        """Call Report Writer AIM"""
        try:
            response = requests.post(
                f'{self.writer_url}/write',
                json={
                    "topic": topic,
                    "outline": outline,
                    "research_data": research_data,
                    "document_text": document_text
                },
                timeout=120  
            )
            
            if response.status_code != 200:
                raise Exception(f"Writer failed: {response.text}")
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Writer error: {e}")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    orchestrator = PipelineOrchestrator(
        file_processor_url=os.getenv('FILE_PROCESSOR_URL'),
        research_url=os.getenv('RESEARCH_AGENT_URL'),
        analyzer_url=os.getenv('ANALYZER_URL'),
        writer_url=os.getenv('WRITER_URL')
    )
    
    test_content = b"""
    Blockchain scalability is a critical challenge for widespread adoption.
    Current networks like Bitcoin and Ethereum process only 7-15 transactions
    per second, far below the requirements for global payment systems.
    Layer 2 solutions and sharding aim to address these limitations.
    """
    
    print("Testing pipeline orchestration...")
    print("This will take 60-90 seconds...\n")
    
    def progress(msg, step, total):
        print(f"[{step}/{total}] {msg}")
    
    result = orchestrator.run_pipeline(
        file_content=test_content,
        filename="test.txt",
        topic="blockchain scalability solutions",
        progress_callback=progress
    )
    
    print("\n=== PIPELINE COMPLETE ===")
    print(f"Report word count: {result['report']['metadata']['word_count']}")
    print(f"Sources researched: {result['research_summary']['sources_found']}")
    print(f"Report sections: {result['report']['metadata']['section_count']}")
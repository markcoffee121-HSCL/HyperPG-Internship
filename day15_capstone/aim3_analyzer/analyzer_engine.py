"""
Analyzer Engine - Core analysis logic combining document and research data
"""

from theme_extractor import ThemeExtractor
from outline_generator import OutlineGenerator
from typing import Dict, List


class AnalyzerEngine:
    def __init__(self, groq_api_key: str):
        self.theme_extractor = ThemeExtractor(groq_api_key)
        self.outline_generator = OutlineGenerator(groq_api_key)
    
    def analyze(
        self,
        topic: str,
        document_text: str,
        research_data: Dict
    ) -> Dict:
        """
        Perform comprehensive analysis combining document and research
        
        Args:
            topic: Main topic/question
            document_text: Content from uploaded document
            research_data: Results from Research Agent
            
        Returns:
            Complete analysis with themes, gaps, and outline
        """
        print(f"[Analyzer Engine] Starting analysis for: {topic}")
        
        doc_themes = self.theme_extractor.extract_themes(document_text, max_themes=5)
        print(f"[Analyzer Engine] Document themes: {len(doc_themes)}")
        
        research_text = self._extract_research_text(research_data)
        research_themes = self.theme_extractor.extract_themes(research_text, max_themes=5)
        print(f"[Analyzer Engine] Research themes: {len(research_themes)}")
        
        gaps = self._find_gaps(doc_themes, research_themes)
        overlaps = self._find_overlaps(doc_themes, research_themes)
        
        print(f"[Analyzer Engine] Gaps: {len(gaps)}, Overlaps: {len(overlaps)}")
        
        outline = self.outline_generator.generate_outline(
            topic=topic,
            document_themes=doc_themes,
            research_themes=research_themes,
            gaps=gaps,
            overlaps=overlaps
        )
        
        print(f"[Analyzer Engine] Generated outline with {len(outline['sections'])} sections")
        
        return {
            "topic": topic,
            "document_themes": doc_themes,
            "research_themes": research_themes,
            "gaps": gaps,
            "overlaps": overlaps,
            "recommended_outline": outline,
            "document_length": len(document_text),
            "research_sources": len(research_data.get('sources', []))
        }
    
    def _extract_research_text(self, research_data: Dict) -> str:
        """Extract text from research data for theme analysis"""
        sources = research_data.get('sources', [])
        
        texts = []
        for source in sources[:10]: 
            texts.append(source.get('title', ''))
            texts.append(source.get('snippet', ''))
        
        findings = research_data.get('key_findings', [])
        texts.extend(findings)
        
        return ' '.join(texts)
    
    def _find_gaps(self, doc_themes: List[str], research_themes: List[str]) -> List[str]:
        """Find themes in research but not in document"""
        doc_lower = [t.lower() for t in doc_themes]
        gaps = []
        
        for theme in research_themes:
            if not any(self._is_similar(theme, dt) for dt in doc_lower):
                gaps.append(theme)
        
        return gaps
    
    def _find_overlaps(self, doc_themes: List[str], research_themes: List[str]) -> List[str]:
        """Find common themes between document and research"""
        overlaps = []
        doc_lower = [t.lower() for t in doc_themes]
        
        for theme in research_themes:
            if any(self._is_similar(theme, dt) for dt in doc_lower):
                overlaps.append(theme)
        
        return overlaps
    
    def _is_similar(self, theme1: str, theme2: str) -> bool:
        """Check if two themes are similar (simple word overlap)"""
        words1 = set(theme1.lower().split())
        words2 = set(theme2.lower().split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        return overlap / min(len(words1), len(words2)) >= 0.5


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found")
        exit(1)
    
    engine = AnalyzerEngine(api_key)
    
    doc_text = """
    Blockchain scalability remains a critical challenge. Current implementations
    face transaction throughput limitations. Layer 2 solutions like Lightning Network
    and Polygon offer potential improvements.
    """
    
    research_data = {
        "sources": [
            {"title": "Sharding in Ethereum 2.0", "snippet": "Sharding divides the network..."},
            {"title": "Rollup Technologies", "snippet": "Optimistic and ZK rollups..."}
        ],
        "key_findings": ["Sharding improves scalability", "Rollups reduce gas fees"]
    }
    
    result = engine.analyze(
        topic="blockchain scalability solutions",
        document_text=doc_text,
        research_data=research_data
    )
    
    print("\n=== ANALYSIS RESULTS ===")
    print(f"Document themes: {result['document_themes']}")
    print(f"Research themes: {result['research_themes']}")
    print(f"Gaps: {result['gaps']}")
    print(f"Overlaps: {result['overlaps']}")
    print(f"Outline sections: {len(result['recommended_outline']['sections'])}")
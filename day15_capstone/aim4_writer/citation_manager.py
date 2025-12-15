"""
Citation Manager - Handles source citations and references
"""

from typing import List, Dict


class CitationManager:
    def __init__(self):
        self.sources = []
    
    def add_sources(self, sources: List[Dict]):
        """Add sources to citation list"""
        self.sources = sources
    
    def generate_references_section(self) -> str:
        """
        Generate a References section in markdown
        
        Returns:
            Formatted references section
        """
        if not self.sources:
            return "## References\n\nNo sources cited."
        
        references = ["## References\n"]
        
        for i, source in enumerate(self.sources, 1):
            title = source.get('title', 'Untitled Source')
            link = source.get('link', '#')
            
            references.append(f"{i}. [{title}]({link})")
        
        return '\n'.join(references)
    
    def get_source_count(self) -> int:
        """Get total number of sources"""
        return len(self.sources)


if __name__ == "__main__":
    manager = CitationManager()
    
    test_sources = [
        {
            'title': 'Blockchain Scalability Solutions',
            'link': 'https://example.com/article1'
        },
        {
            'title': 'Layer 2 Technologies',
            'link': 'https://example.com/article2'
        }
    ]
    
    manager.add_sources(test_sources)
    
    print("Source count:", manager.get_source_count())
    print("\n" + manager.generate_references_section())
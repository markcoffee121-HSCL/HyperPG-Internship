"""
Writer Engine - Core report generation orchestration
FIXED VERSION - Handles all data types correctly
"""

from groq import Groq
from section_generator import SectionGenerator
from citation_manager import CitationManager
from formatter import Formatter
from typing import Dict, List
import time


class WriterEngine:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.section_gen = SectionGenerator(groq_api_key)
        self.citations = CitationManager()
        self.formatter = Formatter()
    
    def write_report(
        self,
        topic: str,
        outline: Dict,
        research_data: Dict,
        document_text: str = ""
    ) -> Dict:
        """
        Generate complete report from outline and data
        
        Args:
            topic: Report topic
            outline: Outline from Analyzer with sections
            research_data: Research results from Research Agent
            document_text: Original document content
            
        Returns:
            Complete report in multiple formats
        """
        print(f"[Writer Engine] Generating report for: {topic}")
        
        try:
            sources = research_data.get('sources', [])
            self.citations.add_sources(sources)
            
            context = {
                'topic': topic,
                'research_sources': sources,
                'document_text': document_text,
                'key_findings': research_data.get('key_findings', [])
            }
            
            exec_summary = self._generate_executive_summary(topic, context)
            print("[Writer Engine] Executive summary generated")
            
            sections = []
            outline_sections = outline.get('sections', [])
            
            if not outline_sections:
                print("[Writer Engine] WARNING: No sections in outline")
                outline_sections = self._create_default_outline()
            
            for i, section_spec in enumerate(outline_sections, 1):
                if not isinstance(section_spec, dict):
                    print(f"[Writer Engine] ERROR: Section {i} is not a dict: {type(section_spec)}")
                    continue
                
                section_title = section_spec.get('title', f'Section {i}')
                section_topics = section_spec.get('topics', [])
                
                print(f"[Writer Engine] Generating section {i}/{len(outline_sections)}: {section_title}")
                
                try:
                    section_content = self.section_gen.generate_section(
                        section_title=section_title,
                        section_topics=section_topics,
                        context_data=context,
                        word_target=250
                    )
                    
                    if isinstance(section_content, dict):
                        print(f"[Writer Engine] ERROR: Section generator returned dict instead of string")
                        section_content = str(section_content)
                    elif not isinstance(section_content, str):
                        print(f"[Writer Engine] ERROR: Section content is {type(section_content)}, converting to string")
                        section_content = str(section_content)
                    
                    sections.append(section_content)
                    
                    if i < len(outline_sections):
                        time.sleep(1.5)
                        
                except Exception as e:
                    print(f"[Writer Engine] ERROR generating section {section_title}: {e}")
                    import traceback
                    traceback.print_exc()
                    sections.append(f"## {section_title}\n\n*Section generation encountered an error.*\n")
            
            references = self.citations.generate_references_section()
            
            markdown_report = self._assemble_markdown(
                topic, exec_summary, sections, references
            )
            
            html_report = self.formatter.to_html(markdown_report)
            
            word_count = len(markdown_report.split())
            
            print(f"[Writer Engine] Report complete: {word_count} words, {len(sections)} sections")
            
            return {
                "topic": topic,
                "executive_summary": exec_summary,
                "sections": sections,
                "references": references,
                "markdown": markdown_report,
                "html": html_report,
                "metadata": {
                    "word_count": word_count,
                    "section_count": len(sections),
                    "source_count": self.citations.get_source_count()
                }
            }
            
        except Exception as e:
            print(f"[Writer Engine] CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _generate_executive_summary(self, topic: str, context: Dict) -> str:
        """Generate executive summary"""
        try:
            findings = context.get('key_findings', [])
            findings_text = '\n'.join(f"- {f}" for f in findings[:5])
            
            prompt = f"""Write a concise executive summary (150-200 words) for a professional report about "{topic}".

Key findings from research:
{findings_text}

Requirements:
- Summarize the main points and conclusions
- Professional tone
- 2-3 paragraphs
- No markdown headers
- Focus on insights and implications

Write the summary:"""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[Writer Engine] Executive summary error: {e}")
            return f"This report examines {topic} based on recent research and analysis. The findings provide important insights into the current state and future directions of this field."
    
    def _create_default_outline(self) -> List[Dict]:
        """Create a default outline if none provided"""
        return [
            {
                'title': 'Introduction',
                'topics': ['background', 'scope'],
                'priority': 'high'
            },
            {
                'title': 'Analysis',
                'topics': ['key findings', 'implications'],
                'priority': 'high'
            },
            {
                'title': 'Recommendations',
                'topics': ['action items', 'next steps'],
                'priority': 'medium'
            }
        ]
    
    def _assemble_markdown(
        self,
        topic: str,
        summary: str,
        sections: List[str],
        references: str
    ) -> str:
        """Assemble all parts into complete markdown document"""
        try:
            clean_sections = []
            for i, section in enumerate(sections):
                if isinstance(section, str):
                    clean_sections.append(section)
                else:
                    print(f"[Writer Engine] WARNING: Section {i} is not a string: {type(section)}")
                    clean_sections.append(str(section))
            
            parts = [
                f"# {topic}\n",
                "## Executive Summary\n",
                summary + "\n",
                '\n'.join(clean_sections),
                "\n" + references
            ]
            
            return '\n'.join(parts)
            
        except Exception as e:
            print(f"[Writer Engine] Error assembling markdown: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found")
        exit(1)
    
    engine = WriterEngine(api_key)
    
    test_outline = {
        'sections': [
            {
                'title': 'Introduction',
                'topics': ['background', 'scope'],
                'priority': 'high'
            },
            {
                'title': 'Current Challenges',
                'topics': ['scalability issues', 'throughput limits'],
                'priority': 'high'
            }
        ]
    }
    
    test_research = {
        'sources': [
            {
                'title': 'Blockchain Scalability',
                'link': 'https://example.com/1',
                'snippet': 'Current networks face limitations...'
            }
        ],
        'key_findings': [
            'Layer 2 solutions improve throughput',
            'Sharding is under development'
        ]
    }
    
    print("Generating test report... (30-45 seconds)\n")
    
    report = engine.write_report(
        topic="Blockchain Scalability Solutions",
        outline=test_outline,
        research_data=test_research,
        document_text="Sample document about blockchain."
    )
    
    print("\n=== REPORT GENERATED ===")
    print(f"Word count: {report['metadata']['word_count']}")
    print(f"Sections: {report['metadata']['section_count']}")
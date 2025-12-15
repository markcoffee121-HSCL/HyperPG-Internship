"""
Outline Generator - Creates structured report outline from analysis
"""

from groq import Groq
import json
from typing import Dict, List


class OutlineGenerator:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
    
    def generate_outline(
        self,
        topic: str,
        document_themes: List[str],
        research_themes: List[str],
        gaps: List[str],
        overlaps: List[str]
    ) -> Dict:
        """
        Generate structured report outline
        
        Returns:
            {
                "sections": [
                    {
                        "title": "Section Name",
                        "topics": ["topic1", "topic2"],
                        "priority": "high/medium/low"
                    }
                ]
            }
        """
        try:
            prompt = f"""Create a structured outline for a comprehensive report on "{topic}".

Analysis Data:
- Document covers: {', '.join(document_themes)}
- Research found: {', '.join(research_themes)}
- Gaps to address: {', '.join(gaps) if gaps else 'None'}
- Overlapping topics: {', '.join(overlaps) if overlaps else 'None'}

Requirements:
- Create 4-6 main sections for the report
- Each section should have a clear title
- Include 2-4 topics to cover in each section
- Mark priority as "high", "medium", or "low"
- Return ONLY valid JSON, no explanation

Format:
{{
  "sections": [
    {{
      "title": "Introduction",
      "topics": ["background", "scope"],
      "priority": "high"
    }}
  ]
}}

Your response:"""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=600
            )
            
            result = response.choices[0].message.content.strip()
            
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            outline = json.loads(result)
            
            if "sections" in outline and isinstance(outline["sections"], list):
                return outline
            else:
                return self._default_outline(topic)
            
        except Exception as e:
            print(f"Outline generation error: {e}")
            return self._default_outline(topic)
    
    def _default_outline(self, topic: str) -> Dict:
        """Fallback outline structure"""
        return {
            "sections": [
                {
                    "title": "Executive Summary",
                    "topics": ["key findings", "main conclusions"],
                    "priority": "high"
                },
                {
                    "title": f"Analysis of {topic}",
                    "topics": ["current state", "key developments"],
                    "priority": "high"
                },
                {
                    "title": "Detailed Findings",
                    "topics": ["research results", "data analysis"],
                    "priority": "medium"
                },
                {
                    "title": "Recommendations",
                    "topics": ["action items", "future directions"],
                    "priority": "medium"
                }
            ]
        }


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found")
        exit(1)
    
    generator = OutlineGenerator(api_key)
    
    outline = generator.generate_outline(
        topic="blockchain scalability",
        document_themes=["layer 2 solutions", "consensus mechanisms"],
        research_themes=["sharding", "proof of stake", "rollups"],
        gaps=["zero-knowledge proofs", "cross-chain bridges"],
        overlaps=["layer 2 solutions"]
    )
    
    print("Generated outline:")
    print(json.dumps(outline, indent=2))
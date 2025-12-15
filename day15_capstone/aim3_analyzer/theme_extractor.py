"""
Theme Extractor - Identifies main themes and topics from text
"""

from groq import Groq
import json
from typing import List


class ThemeExtractor:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
    
    def extract_themes(self, text: str, max_themes: int = 5) -> List[str]:
        """
        Extract main themes/topics from text using LLM
        
        Args:
            text: Input text to analyze
            max_themes: Maximum themes to extract
            
        Returns:
            List of theme strings
        """
        try:
            text_sample = text[:3000] if len(text) > 3000 else text
            
            prompt = f"""Analyze this text and identify the main themes or topics discussed.

Text:
{text_sample}

Requirements:
- Identify {max_themes} main themes or topics
- Each theme should be a short phrase (2-5 words)
- Focus on substantive topics, not writing style
- Return ONLY a JSON array of strings, no explanation

Example format: ["artificial intelligence", "machine learning applications", "ethical considerations"]

Your response:"""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            try:
                themes = json.loads(result)
                if isinstance(themes, list):
                    return [t.lower() for t in themes[:max_themes]]
            except json.JSONDecodeError:
                lines = result.split('\n')
                themes = []
                for line in lines:
                    clean = line.strip('0123456789.-"\'[] ')
                    if clean and 3 < len(clean) < 50:
                        themes.append(clean.lower())
                return themes[:max_themes] if themes else ["general topic"]
            
            return ["general topic"]
            
        except Exception as e:
            print(f"Theme extraction error: {e}")
            return ["general topic"]


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found")
        exit(1)
    
    extractor = ThemeExtractor(api_key)
    
    test_text = """
    Blockchain technology has revolutionized digital transactions through decentralization.
    The main challenge facing blockchain adoption is scalability. Current solutions include
    Layer 2 protocols, sharding, and consensus mechanism improvements. Ethereum's transition
    to proof-of-stake aims to address some of these concerns.
    """
    
    themes = extractor.extract_themes(test_text)
    print("Extracted themes:")
    for i, theme in enumerate(themes, 1):
        print(f"  {i}. {theme}")
from groq import Groq
from typing import List, Dict, Union
import time


class SectionGenerator:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.last_call_time = 0
        self.min_delay = 5  
    def generate_section(
        self,
        section_title: str,
        section_topics: List[Union[str, Dict]],
        context_data: Dict,
        word_target: int = 300
    ) -> str:
        """
        Generate content for a single report section
        
        Args:
            section_title: Title of the section
            section_topics: Topics to cover in this section (can be strings or dicts)
            context_data: Dict with 'research_sources', 'document_text', 'topic'
            word_target: Target word count for section
            
        Returns:
            Generated section content (markdown)
        """
        self._enforce_rate_limit()
        
        cleaned_topics = []
        for topic in section_topics:
            if isinstance(topic, str):
                cleaned_topics.append(topic)
            elif isinstance(topic, dict):
                topic_str = topic.get('topic') or topic.get('name') or topic.get('title') or str(topic)
                cleaned_topics.append(topic_str)
            else:
                cleaned_topics.append(str(topic))
        
        section_topics = cleaned_topics  
        print(f"[Section Generator] Cleaned topics: {section_topics}")
        
        try:
            research_context = self._prepare_research_context(
                context_data.get('research_sources', [])
            )
            
            doc_text = context_data.get('document_text', '')
            doc_context = doc_text[:800] if doc_text else "No document provided"
            
            topic = context_data.get('topic', 'the subject')
            
            topics_list = ', '.join(section_topics)  
            prompt = f"""Write a professional report section about {topic}.

Section: {section_title}
Topics to cover: {topics_list}

Context from research:
{research_context[:1500]}

Document excerpt:
{doc_context}

Write a clear, professional section of approximately {word_target} words. Use markdown formatting. Be specific and informative.

Section content:"""

            print(f"[Section Generator] Generating: {section_title}")
            
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            
            if not content:
                print(f"[Section Generator] Empty response for {section_title}")
                return self._create_fallback_section(section_title, section_topics, context_data)
            
            if not content.startswith('#'):
                content = f"## {section_title}\n\n{content}"
            
            print(f"[Section Generator] Successfully generated {section_title} ({len(content.split())} words)")
            return content
            
        except Exception as e:
            print(f"[Section Generator] Error generating {section_title}: {e}")
            import traceback
            traceback.print_exc()
            
            return self._create_fallback_section(section_title, section_topics, context_data)
    
    def _enforce_rate_limit(self):
        """Ensure minimum delay between API calls to avoid rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            print(f"[Section Generator] Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def _prepare_research_context(self, sources: List[Dict]) -> str:
        """Format research sources for LLM context"""
        if not sources:
            return "No research sources available"
        
        context_parts = []
        for i, source in enumerate(sources[:5], 1):
            title = source.get('title', 'Untitled')
            snippet = source.get('snippet', '')
            context_parts.append(f"{i}. {title}: {snippet}")
        
        return '\n'.join(context_parts)
    
    def _create_fallback_section(
        self,
        section_title: str,
        section_topics: List[str], 
        context_data: Dict
    ) -> str:
        """Create a basic section when LLM generation fails"""
        topic = context_data.get('topic', 'this topic')
        
        topics_text = ', '.join(section_topics) if section_topics else 'these topics'
        first_topic = section_topics[0] if section_topics else 'these topics'
        
        content = f"""## {section_title}

This section examines {section_title.lower()} in relation to {topic}. Key areas of focus include {topics_text}.

Research in this area indicates several important considerations. The available evidence suggests that these factors play a significant role in understanding the broader implications of {topic}.

Further analysis of {first_topic} reveals important insights that contribute to our overall understanding. These findings have practical implications for stakeholders and decision-makers working in this domain.

Additional research would be beneficial to fully explore the relationships between these factors and their long-term impacts."""
        
        print(f"[Section Generator] Using fallback content for {section_title}")
        return content


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not found")
        exit(1)
    
    generator = SectionGenerator(api_key)
    
    context = {
        'topic': 'blockchain scalability',
        'research_sources': [
            {
                'title': 'Layer 2 Solutions Overview',
                'snippet': 'Layer 2 protocols process transactions off-chain...'
            },
            {
                'title': 'Sharding in Ethereum',
                'snippet': 'Sharding divides the network into smaller pieces...'
            }
        ],
        'document_text': 'Blockchain scalability is critical. Current networks are slow.'
    }
    
    section = generator.generate_section(
        section_title="Current Scalability Challenges",
        section_topics=[
            {"topic": "transaction throughput"},
            {"topic": "network congestion"},
            "cost considerations" 
        ],
        context_data=context,
        word_target=200
    )
    
    print("\n" + "="*60)
    print("Generated Section:")
    print("="*60)
    print(section)
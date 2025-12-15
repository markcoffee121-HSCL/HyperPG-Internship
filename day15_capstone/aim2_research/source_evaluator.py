"""
Source Evaluator - Scores source credibility and relevance
"""

from typing import Dict, List
import re


class SourceEvaluator:
    TRUSTED_DOMAINS = {
        'reuters.com', 'bbc.com', 'apnews.com', 'bloomberg.com',
        'wsj.com', 'nytimes.com', 'theguardian.com',
        'techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com',
        'arxiv.org', 'ieee.org', 'acm.org', 'nature.com', 'science.org',
        '.gov', '.edu', '.org'
    }

    MEDIUM_DOMAINS = {
        'medium.com', 'substack.com', 'hackernoon.com',
        'coindesk.com', 'cointelegraph.com', 'decrypt.co'
    }

    LOW_DOMAINS = {
        'reddit.com', 'twitter.com', 'facebook.com',
        'quora.com', 'stackoverflow.com'
    }

    def evaluate(self, source: Dict) -> Dict:
        """
        Evaluate a single source and add credibility score

        Args:
            source: Dictionary with 'link', 'title', 'snippet' keys

        Returns:
            Enhanced source dict with 'credibility_score' (0.0-1.0)
        """
        url = source.get('link', '')
        title = source.get('title', '')
        snippet = source.get('snippet', '')

        score = 0.5
        domain_score = self._score_domain(url)
        score = (score + domain_score) / 2

        content_score = self._score_content(title, snippet)
        score = (score + content_score) / 2

        if self._has_recent_date(snippet):
            score = min(1.0, score + 0.1)

        source['credibility_score'] = round(score, 2)
        return source

    def _score_domain(self, url: str) -> float:
        """Score based on domain reputation"""
        url_lower = url.lower()

        for domain in self.TRUSTED_DOMAINS:
            if domain in url_lower:
                return 0.9

        for domain in self.MEDIUM_DOMAINS:
            if domain in url_lower:
                return 0.6

        for domain in self.LOW_DOMAINS:
            if domain in url_lower:
                return 0.3

        return 0.5

    def _score_content(self, title: str, snippet: str) -> float:
        """Score based on content quality indicators"""
        text = (title + ' ' + snippet).lower()
        score = 0.5

        if any(word in text for word in ['research', 'study', 'analysis', 'report']):
            score += 0.1

        if any(word in text for word in ['expert', 'professor', 'scientist', 'researcher']):
            score += 0.1

        if any(word in text for word in ['data', 'statistics', 'findings', 'results']):
            score += 0.1

        if any(word in text for word in ['opinion', 'rumor', 'allegedly', 'claims']):
            score -= 0.1

        if '?' in title or 'clickbait' in text.lower():
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _has_recent_date(self, text: str) -> bool:
        """Check if text mentions recent dates"""
        recent_keywords = ['2024', '2025', 'today', 'yesterday', 'this week', 'this month']
        return any(keyword in text.lower() for keyword in recent_keywords)

    def rank_sources(self, sources: List[Dict]) -> List[Dict]:
        """
        Evaluate and rank multiple sources by credibility

        Returns:
            Sorted list (highest credibility first)
        """
        evaluated = [self.evaluate(source) for source in sources]
        return sorted(evaluated, key=lambda x: x.get('credibility_score', 0), reverse=True)


if __name__ == "__main__":
    evaluator = SourceEvaluator()

    test_sources = [
        {
            'link': 'https://www.reuters.com/technology/ai-breakthrough',
            'title': 'New AI Research Shows Breakthrough',
            'snippet': 'Study published in 2024 reveals...'
        },
        {
            'link': 'https://medium.com/random-blog/my-opinion',
            'title': 'Why AI Might Be Dangerous (Opinion)',
            'snippet': 'I think AI is scary because...'
        },
        {
            'link': 'https://arxiv.org/abs/2024.12345',
            'title': 'Deep Learning Paper',
            'snippet': 'Research findings indicate...'
        }
    ]

    print("Testing Source Evaluator:\n")
    ranked = evaluator.rank_sources(test_sources)

    for i, source in enumerate(ranked, 1):
        print(f"{i}. Score: {source['credibility_score']}")
        print(f"   {source['title']}")
        print(f"   {source['link']}\n")
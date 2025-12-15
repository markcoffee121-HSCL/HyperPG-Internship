"""
Formatter - Converts markdown reports to different output formats
"""

import markdown
from typing import Dict


class Formatter:
    @staticmethod
    def to_markdown(content: str) -> str:
        """Return content as-is (already markdown)"""
        return content
    
    @staticmethod
    def to_html(content: str) -> str:
        """Convert markdown to HTML"""
        try:
            html = markdown.markdown(
                content,
                extensions=['extra', 'codehilite', 'toc']
            )
            
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #555;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
        except Exception as e:
            print(f"HTML conversion error: {e}")
            return f"<html><body><pre>{content}</pre></body></html>"
    
    @staticmethod
    def to_json(report_data: Dict) -> Dict:
        """Format report data as structured JSON"""
        return {
            "report": {
                "topic": report_data.get('topic', ''),
                "executive_summary": report_data.get('executive_summary', ''),
                "sections": report_data.get('sections', []),
                "references": report_data.get('references', ''),
                "metadata": {
                    "word_count": report_data.get('word_count', 0),
                    "source_count": report_data.get('source_count', 0),
                    "sections_count": len(report_data.get('sections', []))
                }
            }
        }


if __name__ == "__main__":
    formatter = Formatter()
    
    test_markdown = """# Test Report

## Introduction
This is a test.

## Analysis
Some analysis here.

[Link](https://example.com)
"""
    
    print("=== MARKDOWN ===")
    print(formatter.to_markdown(test_markdown))
    
    print("\n=== HTML (truncated) ===")
    html = formatter.to_html(test_markdown)
    print(html[:200] + "...")
    
    print("\n=== JSON ===")
    import json
    test_data = {
        'topic': 'Test Topic',
        'executive_summary': 'Summary here',
        'sections': ['Section 1', 'Section 2'],
        'word_count': 500
    }
    print(json.dumps(formatter.to_json(test_data), indent=2))
"""
Flask Web Application - Main orchestrator interface
Provides web UI for the complete research pipeline
"""

from flask import Flask, render_template, request, jsonify, send_file
from orchestrator import PipelineOrchestrator
import os
from dotenv import load_dotenv
import io

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 

orchestrator = PipelineOrchestrator(
    file_processor_url=os.getenv('FILE_PROCESSOR_URL'),
    research_url=os.getenv('RESEARCH_AGENT_URL'),
    analyzer_url=os.getenv('ANALYZER_URL'),
    writer_url=os.getenv('WRITER_URL')
)


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "HyperPG Pipeline Orchestrator",
        "version": "1.1.0"
    })


@app.route('/process', methods=['POST'])
def process_pipeline():
    """
    Main pipeline endpoint
    
    Expects:
    - file: uploaded document
    - topic: research topic
    
    Returns:
    - Complete report data with auto-generated title
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        if 'topic' not in request.form:
            return jsonify({"error": "No topic provided"}), 400
        
        file = request.files['file']
        topic = request.form['topic']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not topic or len(topic.strip()) == 0:
            return jsonify({"error": "Topic cannot be empty"}), 400
        
        file_content = file.read()
        
        title = generate_title(topic)
        
        print(f"[Web UI] Processing request: {file.filename}, topic: {topic}, title: {title}")
        
        result = orchestrator.run_pipeline(
            file_content=file_content,
            filename=file.filename,
            topic=title  
        )
        
        result['title'] = title
        result['filename_base'] = generate_filename(title)
        
        print(f"[Web UI] Pipeline complete")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[Web UI] Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/download/<format>', methods=['POST'])
def download_report(format):
    """
    Download report in specified format with dynamic filename
    
    Formats: markdown, html
    """
    try:
        data = request.get_json()
        
        filename_base = data.get('filename_base', 'report')
        
        if format == 'markdown':
            content = data.get('markdown', '')
            mimetype = 'text/markdown'
            filename = f'{filename_base}.md'
        elif format == 'html':
            content = data.get('html', '')
            mimetype = 'text/html'
            filename = f'{filename_base}.html'
        else:
            return jsonify({"error": "Invalid format"}), 400
        
        file_obj = io.BytesIO(content.encode('utf-8'))
        file_obj.seek(0)
        
        return send_file(
            file_obj,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_title(topic: str) -> str:
    """
    Generate professional title from topic
    
    Examples:
    - "blockchain scalability" -> "Blockchain Scalability Solutions"
    - "ai ethics" -> "Artificial Intelligence Ethics"
    - "renewable energy" -> "Renewable Energy Technologies"
    """
    title = topic.strip().title()
    
    words = title.split()
    
    if len(words) == 1:
        title = f"{title} Analysis"
    elif len(words) == 2:
        has_context = any(word in title.lower() for word in [
            'solutions', 'analysis', 'overview', 'technologies', 
            'systems', 'applications', 'strategies', 'approaches'
        ])
        
        if not has_context:
            if 'ethics' in title.lower():
                pass  
            elif 'scalability' in title.lower():
                title = f"{title} Solutions"
            elif 'energy' in title.lower():
                title = f"{title} Technologies"
            else:
                title = f"{title} Overview"
    
    return title


def generate_filename(title: str) -> str:
    """
    Generate safe filename from title
    
    Examples:
    - "Blockchain Scalability Solutions" -> "blockchain_scalability_solutions"
    - "Artificial Intelligence Ethics" -> "artificial_intelligence_ethics"
    """
    filename = title.lower().replace(' ', '_')
    
    filename = ''.join(c for c in filename if c.isalnum() or c == '_')
    
    return filename


if __name__ == '__main__':
    port = int(os.getenv('PORT', 4000))
    print(f"[Web UI] Starting orchestrator on port {port}")
    print(f"[Web UI] File Processor: {os.getenv('FILE_PROCESSOR_URL')}")
    print(f"[Web UI] Research Agent: {os.getenv('RESEARCH_AGENT_URL')}")
    print(f"[Web UI] Analyzer: {os.getenv('ANALYZER_URL')}")
    print(f"[Web UI] Writer: {os.getenv('WRITER_URL')}")
    app.run(host='0.0.0.0', port=port, debug=False)
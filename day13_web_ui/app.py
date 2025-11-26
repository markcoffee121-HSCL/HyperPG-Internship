from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_EXTENSIONS'] = ['.txt']

# AIM endpoints from environment
FILE_PROCESSOR_URL = os.getenv('FILE_PROCESSOR_URL', 'http://localhost:9030')
SUMMARIZER_URL = os.getenv('SUMMARIZER_URL', 'http://localhost:9040')

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    # Check if AIMs are accessible
    file_processor_status = check_aim_health(FILE_PROCESSOR_URL)
    summarizer_status = check_aim_health(SUMMARIZER_URL)
    
    return jsonify({
        "status": "healthy",
        "service": "web_ui",
        "aims": {
            "file_processor": {
                "url": FILE_PROCESSOR_URL,
                "status": file_processor_status
            },
            "summarizer": {
                "url": SUMMARIZER_URL,
                "status": summarizer_status
            }
        }
    })

def check_aim_health(aim_url):
    """Check if an AIM is responding"""
    try:
        response = requests.get(f"{aim_url}/health", timeout=2)
        return "online" if response.status_code == 200 else "offline"
    except:
        return "offline"

@app.route('/process', methods=['POST'])
def process_file():
    """Handle file upload and processing"""
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files are allowed'}), 400
        
        # Read file content
        file_content = file.read()
        
        # Check if file is empty
        if len(file_content) == 0:
            return jsonify({'error': 'File is empty'}), 400
        
        # Decode file content for summarizer
        try:
            text_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'error': 'File must be valid UTF-8 text'}), 400
        
        # STEP 1: Call File Processor AIM
        print(f"[1/2] Calling File Processor AIM at {FILE_PROCESSOR_URL}/process")
        files_for_processor = {
            'file': (file.filename, io.BytesIO(file_content), 'text/plain')
        }
        
        processor_response = requests.post(
            f"{FILE_PROCESSOR_URL}/process",
            files=files_for_processor,
            timeout=30
        )
        
        if processor_response.status_code != 200:
            return jsonify({
                'error': f'File Processor AIM returned error: {processor_response.status_code}'
            }), 500
        
        analysis_result = processor_response.json()
        print(f"[1/2] File Processor completed: {analysis_result}")
        
        # STEP 2: Call Summarizer AIM
        print(f"[2/2] Calling Summarizer AIM at {SUMMARIZER_URL}/summarize")
        summarizer_response = requests.post(
            f"{SUMMARIZER_URL}/summarize",
            json={"text": text_content},
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for LLM processing
        )
        
        if summarizer_response.status_code != 200:
            print(f"[2/2] Summarizer AIM error: {summarizer_response.status_code}")
            summary_result = {
                "summary": "Summarizer unavailable",
                "error": f"Status code: {summarizer_response.status_code}"
            }
        else:
            summary_result = summarizer_response.json()
            print(f"[2/2] Summarizer completed successfully")
        
        # Return combined results
        return jsonify({
            'success': True,
            'filename': file.filename,
            'analysis': analysis_result,
            'summary': summary_result
        })
    
    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        if 'File Processor' in error_msg or '9030' in error_msg:
            return jsonify({
                'error': 'Cannot connect to File Processor AIM. Is it running on port 9030?'
            }), 503
        else:
            return jsonify({
                'error': 'Cannot connect to Summarizer AIM. Is it running on port 9040?'
            }), 503
    
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timed out. The file may be too large or AIMs are overloaded.'
        }), 504
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('WEB_UI_PORT', 5000))
    print(f"Starting Web UI on port {port}")
    print(f"File Processor AIM: {FILE_PROCESSOR_URL}")
    print(f"Summarizer AIM: {SUMMARIZER_URL}")
    app.run(host='0.0.0.0', port=port, debug=True)
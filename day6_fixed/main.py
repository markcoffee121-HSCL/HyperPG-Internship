"""
File Processor AIM - FIXED VERSION
Handles TXT, PDF, DOCX with proper text extraction
"""

from pyhypercycle_aim import SimpleServer, aim_uri, JSONResponseCORS
from werkzeug.utils import secure_filename
import os
import hashlib

# Import extraction libraries
import PyPDF2
from docx import Document


class FileProcessorAIM(SimpleServer):
    manifest = {
        "name": "FileProcessorAIM",
        "short_name": "fileprocessor",
        "version": "2.0.0",
        "documentation_url": "",
        "license": "MIT",
        "terms_of_service": "",
        "author": "Raijin - Day 15 Fixed"
    }
    
    def __init__(self):
        super().__init__()
        self.cache = {}
        print("[File Processor] Initialized v2.0.0 with PDF/DOCX support")
    
    @aim_uri(
        uri="/process",
        methods=["POST"],
        endpoint_manifest={
            "input_body": {"file": "<file>"},
            "output": {
                "filename": "<string>",
                "content": "<string>",
                "line_count": "<int>",
                "word_count": "<int>",
                "file_size_bytes": "<int>",
                "file_type": "<string>",
                "cached": "<boolean>"
            },
            "documentation": "Extract text from uploaded file (TXT, PDF, DOCX)",
            "example_calls": [],
            "is_public": True
        }
    )
    async def process_file(self, request):
        """Process uploaded file and extract text content"""
        try:
            form = await request.form()
            
            if 'file' not in form:
                return JSONResponseCORS({"error": "No file uploaded"}, status_code=400)
            
            file = form['file']
            
            if not file or not file.filename:
                return JSONResponseCORS({"error": "Invalid file"}, status_code=400)
            
            # Read file content
            file_content = await file.read()
            filename = secure_filename(file.filename)
            
            # Determine file type
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Generate cache key
            cache_key = hashlib.md5(file_content).hexdigest()
            
            # Check cache
            if cache_key in self.cache:
                print(f"[File Processor] Cache hit for {filename}")
                result = self.cache[cache_key].copy()
                result['cached'] = True
                result['filename'] = filename
                return JSONResponseCORS(result)
            
            print(f"[File Processor] Processing {filename} ({file_ext})")
            
            # Extract text based on file type
            if file_ext == '.txt':
                text_content = self._extract_txt(file_content)
            elif file_ext == '.pdf':
                text_content = self._extract_pdf(file_content)
            elif file_ext == '.docx':
                text_content = self._extract_docx(file_content)
            else:
                return JSONResponseCORS({
                    "error": f"Unsupported file type: {file_ext}. Supported: .txt, .pdf, .docx"
                }, status_code=400)
            
            # Calculate statistics
            lines = text_content.split('\n')
            words = text_content.split()
            
            result = {
                'filename': filename,
                'content': text_content,
                'line_count': len(lines),
                'word_count': len(words),
                'file_size_bytes': len(file_content),
                'file_type': file_ext,
                'cached': False
            }
            
            # Cache result
            self.cache[cache_key] = result.copy()
            
            print(f"[File Processor] Success: {len(words)} words extracted from {filename}")
            
            return JSONResponseCORS(result)
            
        except Exception as e:
            print(f"[File Processor] Error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponseCORS({"error": str(e)}, status_code=500)
    
    def _extract_txt(self, file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except:
                return file_content.decode('utf-8', errors='ignore')
    
    def _extract_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            import io
            
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = '\n'.join(text_parts)
            
            if not full_text.strip():
                return "PDF text extraction failed - file may be image-based"
            
            return full_text
            
        except Exception as e:
            print(f"[File Processor] PDF extraction error: {e}")
            return f"PDF extraction error: {str(e)}"
    
    def _extract_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            import io
            
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            full_text = '\n'.join(text_parts)
            
            if not full_text.strip():
                return "DOCX text extraction failed - document may be empty"
            
            return full_text
            
        except Exception as e:
            print(f"[File Processor] DOCX extraction error: {e}")
            return f"DOCX extraction error: {str(e)}"


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 4000))
    server = FileProcessorAIM()
    print(f"[File Processor] Starting on port {port}")
    server.run(uvicorn_kwargs={"host": "0.0.0.0", "port": port})
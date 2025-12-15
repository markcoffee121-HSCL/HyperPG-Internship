// Global variables
let selectedFile = null;
let reportData = null;
let filenameBase = 'report';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const topicInput = document.getElementById('topicInput');
const generateBtn = document.getElementById('generateBtn');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // File upload
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // Topic input
    topicInput.addEventListener('input', validateInputs);
    
    // Generate button
    generateBtn.addEventListener('click', startPipeline);
    
    // Download buttons
    document.getElementById('downloadMarkdown').addEventListener('click', () => downloadReport('markdown'));
    document.getElementById('downloadHtml').addEventListener('click', () => downloadReport('html'));
    document.getElementById('viewReport').addEventListener('click', showReportModal);
    
    // Modal
    document.getElementById('closeModal').addEventListener('click', closeReportModal);
    
    // Retry button
    document.getElementById('retryBtn').addEventListener('click', resetUI);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file type
    const validTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(txt|pdf|docx)$/i)) {
        alert('Please upload a TXT, PDF, or DOCX file');
        return;
    }
    
    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    uploadArea.querySelector('.upload-content').style.display = 'none';
    fileInfo.style.display = 'flex';
    
    validateInputs();
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    uploadArea.querySelector('.upload-content').style.display = 'block';
    fileInfo.style.display = 'none';
    validateInputs();
}

function validateInputs() {
    const hasFile = selectedFile !== null;
    const hasTopic = topicInput.value.trim().length > 0;
    generateBtn.disabled = !(hasFile && hasTopic);
}

async function startPipeline() {
    if (!selectedFile || !topicInput.value.trim()) {
        return;
    }
    
    // Hide other sections
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Show progress
    progressSection.style.display = 'block';
    generateBtn.disabled = true;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('topic', topicInput.value.trim());
    
    try {
        // Simulate progress updates
        updateProgress(1, 'Processing document...');
        
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Pipeline failed');
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Unknown error');
        }
        
        // Complete progress
        updateProgress(4, 'Report generated!');
        
        // Show results after a brief delay
        setTimeout(() => {
            showResults(data);
        }, 1000);
        
    } catch (error) {
        console.error('Pipeline error:', error);
        showError(error.message);
    }
}

function updateProgress(step, message) {
    // Update step indicators
    for (let i = 1; i <= 4; i++) {
        const stepEl = document.getElementById(`step${i}`);
        if (i < step) {
            stepEl.classList.add('completed');
            stepEl.classList.remove('active');
        } else if (i === step) {
            stepEl.classList.add('active');
            stepEl.classList.remove('completed');
        } else {
            stepEl.classList.remove('active', 'completed');
        }
    }
    
    // Update progress bar
    const progress = (step / 4) * 100;
    document.getElementById('progressFill').style.width = `${progress}%`;
    document.getElementById('progressText').textContent = message;
}

function showResults(data) {
    reportData = data;
    
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Update stats
    const report = data.report;
    const research = data.research_summary;
    
    document.getElementById('wordCount').textContent = report.metadata.word_count;
    document.getElementById('sourceCount').textContent = research.sources_found;
    document.getElementById('sectionCount').textContent = report.metadata.section_count;
    document.getElementById('confidenceScore').textContent = Math.round(research.confidence * 100) + '%';
    
    // Display the generated title
    const titleDisplay = document.createElement('h3');
    titleDisplay.textContent = data.title || report.topic;
    titleDisplay.style.textAlign = 'center';
    titleDisplay.style.color = '#667eea';
    titleDisplay.style.marginBottom = '20px';
    titleDisplay.style.fontSize = '1.5em';
    
    // Insert title before stats if not already present
    const statsGrid = document.querySelector('.stats-grid');
    if (!document.getElementById('reportTitle')) {
        titleDisplay.id = 'reportTitle';
        statsGrid.parentNode.insertBefore(titleDisplay, statsGrid);
    } else {
        document.getElementById('reportTitle').textContent = data.title || report.topic;
    }
    
    // Executive summary
    document.getElementById('execSummary').textContent = report.executive_summary;
    
    // Store filename base for downloads
    filenameBase = data.filename_base || 'report';
}

function downloadReport(format) {
    if (!reportData) return;
    
    const report = reportData.report;
    let content, filename, mimetype;
    
    if (format === 'markdown') {
        content = report.markdown;
        filename = `${filenameBase}.md`;
        mimetype = 'text/markdown';
    } else if (format === 'html') {
        content = report.html;
        filename = `${filenameBase}.html`;
        mimetype = 'text/html';
    }
    
    // Create blob and download
    const blob = new Blob([content], { type: mimetype });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function showReportModal() {
    if (!reportData) return;
    
    const modal = document.getElementById('reportModal');
    const content = document.getElementById('reportContent');
    
    // Display HTML report
    content.innerHTML = reportData.report.html;
    modal.style.display = 'flex';
}

function closeReportModal() {
    document.getElementById('reportModal').style.display = 'none';
}

function showError(message) {
    progressSection.style.display = 'none';
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
    generateBtn.disabled = false;
}

function resetUI() {
    errorSection.style.display = 'none';
    resultsSection.style.display = 'none';
    progressSection.style.display = 'none';
    generateBtn.disabled = false;
}

// Close modal on outside click
window.addEventListener('click', (e) => {
    const modal = document.getElementById('reportModal');
    if (e.target === modal) {
        closeReportModal();
    }
});
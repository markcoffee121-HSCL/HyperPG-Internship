// Global variables
let selectedFile = null;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const processBtn = document.getElementById('processBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingIndicator = document.getElementById('loadingIndicator');
const processingSteps = document.getElementById('processingSteps');
const statusIndicator = document.getElementById('statusIndicator');
const analysisResult = document.getElementById('analysisResult');
const summaryResult = document.getElementById('summaryResult');
const fileInfo = document.getElementById('fileInfo');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
});

function setupEventListeners() {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File selection
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Process button
    processBtn.addEventListener('click', processFile);
    
    // Clear button
    clearBtn.addEventListener('click', clearAndReset);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        updateSelectedFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        fileInput.files = event.dataTransfer.files;
        updateSelectedFile(file);
    }
}

function updateSelectedFile(file) {
    selectedFile = file;
    
    // Update UI
    const uploadText = uploadArea.querySelector('.upload-text');
    uploadText.textContent = `Selected: ${file.name}`;
    
    // Show file info
    const sizeKB = (file.size / 1024).toFixed(2);
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    const sizeDisplay = file.size > 1024 * 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;
    
    fileInfo.style.display = 'block';
    
    // Warn if file is large
    if (file.size > 5 * 1024) { // More than 5KB
        fileInfo.className = 'file-info warning';
        fileInfo.textContent = `⚠️ File size: ${sizeDisplay} - May exceed token limits`;
    } else {
        fileInfo.className = 'file-info';
        fileInfo.textContent = `✓ File size: ${sizeDisplay}`;
    }
    
    // Update upload area styling
    uploadArea.classList.add('file-selected');
    
    // Enable process button
    processBtn.disabled = false;
}

function clearAndReset() {
    // Reset file selection
    selectedFile = null;
    fileInput.value = '';
    
    // Reset UI
    const uploadText = uploadArea.querySelector('.upload-text');
    uploadText.textContent = 'Click to upload or drag and drop';
    fileInfo.style.display = 'none';
    uploadArea.classList.remove('file-selected');
    
    // Hide results and buttons
    resultsSection.style.display = 'none';
    clearBtn.style.display = 'none';
    processingSteps.style.display = 'none';
    
    // Enable process button
    processBtn.disabled = false;
}

async function processFile() {
    if (!selectedFile) return;

    // Hide previous results
    resultsSection.style.display = 'none';
    processBtn.disabled = true;
    
    // Show processing steps
    processingSteps.style.display = 'block';
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    
    step1.classList.remove('completed');
    step2.classList.remove('completed');
    step1.classList.remove('active');
    step2.classList.remove('active');

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Step 1: Activate file processing
        step1.classList.add('active');
        
        // Send to backend
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            // Hide processing steps
            processingSteps.style.display = 'none';
            alert(`Error: ${data.error}`);
            processBtn.disabled = false;
            return;
        }

        // Step 1 complete, activate step 2
        step1.classList.remove('active');
        step1.classList.add('completed');
        step2.classList.add('active');
        
        // Small delay to show the transition
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Step 2 complete
        step2.classList.remove('active');
        step2.classList.add('completed');
        
        // Hide processing steps after a moment
        await new Promise(resolve => setTimeout(resolve, 800));
        processingSteps.style.display = 'none';

        // Display results
        displayResults(data);
        
        // Show clear button
        clearBtn.style.display = 'inline-block';

    } catch (error) {
        processingSteps.style.display = 'none';
        alert(`Network error: ${error.message}`);
        processBtn.disabled = false;
        console.error('Error:', error);
    }
}

function displayResults(data) {
    // Format analysis results
    const analysis = data.analysis;
    
    let analysisHTML = `
        <p><strong>Filename:</strong> ${analysis.filename}</p>
        <p><strong>Lines:</strong> ${analysis.line_count}</p>
        <p><strong>Words:</strong> ${analysis.word_count}</p>
        <p><strong>File Size:</strong> ${formatBytes(analysis.file_size_bytes)}</p>
    `;

    analysisResult.innerHTML = analysisHTML;

    // Format summary results
    const summary = data.summary;
    
    if (summary.error) {
        summaryResult.innerHTML = `
            <div class="warning-message">
                ⚠️ Groq API Limit Exceeded: File is too large for the token limit
            </div>
            <p><strong>Fallback Summary:</strong></p>
            <p>${summary.summary || 'Not available'}</p>
        `;
    } else {
        summaryResult.innerHTML = `
            <p>${summary.summary}</p>
        `;
    }

    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        const fileProcessorStatus = data.aims.file_processor.status;
        const summarizerStatus = data.aims.summarizer.status;
        
        if (fileProcessorStatus === 'online' && summarizerStatus === 'online') {
            statusIndicator.textContent = 'All AIMs Online';
            statusIndicator.className = 'status-ok';
        } else if (fileProcessorStatus === 'online') {
            statusIndicator.textContent = 'File Processor Online (Summarizer Offline)';
            statusIndicator.className = 'status-warning';
        } else {
            statusIndicator.textContent = 'AIMs Offline';
            statusIndicator.className = 'status-error';
        }
    } catch (error) {
        statusIndicator.textContent = 'Connection Error';
        statusIndicator.className = 'status-error';
        console.error('Health check failed:', error);
    }
}

// Refresh health check every 30 seconds
setInterval(checkHealth, 30000);
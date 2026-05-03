const API_URL = "http://localhost:8000";

// Drag and Drop functionality
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('pdfInput');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    fileInput.files = files;
    updateFileLabel(files);
}, false);

fileInput.addEventListener('change', (e) => {
    updateFileLabel(e.target.files);
});

function updateFileLabel(files) {
    const span = dropZone.querySelector('span');
    if (files.length > 0) {
        span.textContent = `${files.length} file(s) selected: ${Array.from(files).map(f => f.name).join(', ')}`;
    } else {
        span.textContent = "Drag & Drop PDF files here or click to browse";
    }
}

async function uploadPaper() {
    const files = fileInput.files;

    if (files.length === 0) {
        alert("Please select at least one PDF");
        return;
    }

    document.getElementById("loading").style.display = "flex";

    try {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i]);
        }

        // Step 1: Upload and extract
        const uploadRes = await fetch(`${API_URL}/upload-paper`, {
            method: "POST",
            body: formData
        });
        
        if (!uploadRes.ok) throw new Error("Upload failed");
        const uploadData = await uploadRes.json();

        // Step 2: Analyze topics
        const analyzeRes = await fetch(`${API_URL}/analyze-topics`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: uploadData.text })
        });
        
        if (!analyzeRes.ok) throw new Error("Analysis failed");
        const analysis = await analyzeRes.json();

        // Check for backend errors
        if (analysis.error) {
            throw new Error(analysis.error);
        }

        // Display results
        document.getElementById("resultsSection").style.display = "block";
        document.getElementById("studyPlanSection").style.display = "block";
        displayResults(analysis);
        
        // Scroll to results
        document.getElementById("resultsSection").scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error("Error:", error);
        alert("Error processing papers: " + error.message);
    } finally {
        document.getElementById("loading").style.display = "none";
    }
}

function displayResults(analysis) {
    const topics = analysis.topics || {};

    // Create chart with modern look
    const ctx = document.getElementById("topicChart").getContext("2d");
    
    // Destroy existing chart if it exists
    if (window.myChart) {
        window.myChart.destroy();
    }

    window.myChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(topics),
            datasets: [{
                label: "Frequency",
                data: Object.values(topics),
                backgroundColor: 'rgba(99, 102, 241, 0.6)',
                borderColor: '#6366f1',
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: 'rgba(99, 102, 241, 0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });

    // List topics
    const topicsList = document.getElementById("topicsList");
    topicsList.innerHTML = Object.entries(topics)
        .sort((a, b) => b[1] - a[1])
        .map(([topic, count]) => `
            <div class="topic-item">
                <span>${topic}</span>
                <span class="topic-badge">${count} Questions</span>
            </div>
        `)
        .join("");

    window.currentAnalysis = analysis;
}

async function generateStudyPlan() {
    if (!window.currentAnalysis) {
        alert("Please analyze papers first");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/generate-study-plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                topics: window.currentAnalysis.topics
            })
        });
        const plan = await res.json();

        // Display study plan
        const planDiv = document.getElementById("studyPlan");
        planDiv.innerHTML = plan.study_plan
            .map(day => `
                <div class="study-day-card priority-${day.priority.toLowerCase()}">
                    <div class="day-header">
                        <span class="day-num">Day ${day.day}</span>
                        <span class="topic-badge">${day.priority}</span>
                    </div>
                    <span class="topic-name">${day.topic}</span>
                    <div class="meta-info">
                        <span><i class="far fa-clock"></i> ${day.hours} Hours</span>
                        <span><i class="fas fa-tasks"></i> Focus Session</span>
                    </div>
                </div>
            `).join("");

        planDiv.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error("Error:", error);
        alert("Error generating study plan: " + error.message);
    }
}
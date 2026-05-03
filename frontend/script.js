const API_URL = "http://localhost:8000";

async function uploadPaper() {
    const fileInput = document.getElementById("pdfInput");
    const files = fileInput.files;

    if (files.length === 0) {
        alert("Please select a PDF");
        return;
    }

    document.getElementById("loading").style.display = "block";

    try {
        const formData = new FormData();
        formData.append("file", files[0]);

        // Step 1: Upload and extract
        const uploadRes = await fetch(`${API_URL}/upload-paper`, {
            method: "POST",
            body: formData
        });
        const uploadData = await uploadRes.json();

        // Step 2: Analyze topics
        const analyzeRes = await fetch(`${API_URL}/analyze-topics`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: uploadData.text })
        });
        const analysis = await analyzeRes.json();

        // Display results
        displayResults(analysis);
        document.getElementById("resultsSection").style.display = "block";
        document.getElementById("studyPlanSection").style.display = "block";

    } catch (error) {
        console.error("Error:", error);
        alert("Error processing paper: " + error.message);
    } finally {
        document.getElementById("loading").style.display = "none";
    }
}

function displayResults(analysis) {
    const topics = analysis.topics || {};

    // Create chart
    const ctx = document.getElementById("topicChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(topics),
            datasets: [{
                label: "Question Frequency",
                data: Object.values(topics),
                backgroundColor: "#667eea"
            }]
        }
    });

    // List topics
    const topicsList = document.getElementById("topicsList");
    topicsList.innerHTML = Object.entries(topics)
        .sort((a, b) => b[1] - a[1])
        .map(([topic, count]) => `<li>${topic}: <strong>${count}</strong> questions</li>`)
        .join("");

    // Store for study plan generation
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
                <div class="study-day">
                    <strong>Day ${day.day}:</strong> ${day.topic} 
                    (${day.hours}h) - <span style="color: #764ba2;">${day.priority}</span>
                </div>
            `).join("");

    } catch (error) {
        console.error("Error:", error);
        alert("Error generating study plan: " + error.message);
    }
}
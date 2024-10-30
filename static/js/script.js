let isRecording = false;
let transcript = "";
const startBtn = document.getElementById('startRecording');
const stopBtn = document.getElementById('stopRecording');
const transcriptDiv = document.getElementById('transcript');
const recordingStatus = document.getElementById('recordingStatus');
let websocket;

// Function to initialize and handle the WebSocket for live transcription
async function handleLiveTranscription() {
    websocket = new WebSocket('ws://localhost:8000/transcribe');

    websocket.onopen = () => {
        isRecording = true;
        updateRecordingStatus("Recording...", "status-recording");
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline';
        transcriptDiv.textContent = ''; // Clear previous transcripts
    };

    websocket.onmessage = (event) => {
        if (event.data === "Recording stopped.") {
            stopRecording();
            return;
        }
        transcript += event.data + ' ';
        transcriptDiv.textContent = transcript;
    };

    websocket.onclose = () => {
        isRecording = false;
        updateRecordingStatus("Recording stopped.", "status-stopped");
        startBtn.style.display = 'inline';
        stopBtn.style.display = 'none';
        websocket = null;
    };

    websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
        stopRecording();
    };
}

// Function to start recording and transcription
startBtn.addEventListener('click', () => {
    if (!isRecording) {
        handleLiveTranscription();
    }
});

// Function to stop recording and close the WebSocket connection
stopBtn.addEventListener('click', async() => {
    await stopRecording();
});

async function stopRecording() {
    if (websocket) {
        await fetch('/stop-recording', { method: 'POST' });
        websocket.close(); // Close WebSocket connection to stop recording
        isRecording = false;
        updateRecordingStatus("Recording stopped.", "status-stopped");
    }
}

// Function to update recording status on the HTML page
function updateRecordingStatus(statusText, statusClass) {
    recordingStatus.textContent = statusText;
    recordingStatus.className = `status ${statusClass}`;
}

// Text-to-Speech functionality
document.getElementById('convertToSpeech').addEventListener('click', async() => {
    const text = document.getElementById('textInput').value;
    if (!text) return;

    try {
        const response = await fetch('/text-to-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        const data = await response.json();
        if (data.audio) {
            const audio = document.getElementById('audioPlayer');
            audio.src = `data:audio/wav;base64,${data.audio}`;
            audio.style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
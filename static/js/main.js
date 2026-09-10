let isStreaming = true;

function toggleStream() {
    const videoElement = document.getElementById('video-stream');
    const toggleBtn = document.getElementById('toggle-btn');
    const liveBadge = document.getElementById('live-badge');

    if (isStreaming) {
        // Stop stream by removing src
        videoElement.src = "";
        toggleBtn.textContent = "Resume Stream";
        liveBadge.textContent = "○ Stream Paused";
        liveBadge.classList.remove('active');
        liveBadge.classList.add('inactive');
        isStreaming = false;
    } else {
        // Restart stream by re-setting Flask route URL
        videoElement.src = "/video_feed";
        toggleBtn.textContent = "Pause Stream";
        liveBadge.textContent = "● Live Stream";
        liveBadge.classList.remove('inactive');
        liveBadge.classList.add('active');
        isStreaming = true;
    }
}

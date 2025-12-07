document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const displayText = document.getElementById('display-text');
    const keys = document.querySelectorAll('.key');

    // Clock
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        const timeSpan = document.querySelector('.status-bar span:first-child');
        if (timeSpan) timeSpan.textContent = timeString;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Call Timer
    const callTimerElement = document.querySelector('.call-info p');
    let callSeconds = 0;
    function updateCallTimer() {
        callSeconds++;
        const mins = Math.floor(callSeconds / 60).toString().padStart(2, '0');
        const secs = (callSeconds % 60).toString().padStart(2, '0');
        if (callTimerElement) callTimerElement.textContent = `${mins}:${secs}`;
    }
    setInterval(updateCallTimer, 1000);

    // Sound interactions (optional but nice)
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    function playTone(freq) {
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.type = 'sine';
        oscillator.frequency.value = freq;

        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);

        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.3);
    }

    function handlePress(digit) {
        // Visual feedback
        const key = document.querySelector(`.key[data-key="${digit}"]`);
        if (key) {
            key.classList.add('active');
            setTimeout(() => key.classList.remove('active'), 200);
        }

        // Update display
        displayText.textContent += digit;

        // Play sound (mock freq)
        let val = parseInt(digit);
        if (isNaN(val)) val = 0; // Treat * and # as 0 for pitch
        playTone(400 + val * 50);
    }

    // Listen for WebSocket events from Server
    socket.on('press', (data) => {
        console.log('Received press:', data);
        handlePress(data.digit);
    });

    socket.on('transcript', (data) => {
        const log = document.getElementById('transcript-log');
        if (!log) return;

        const item = document.createElement('div');
        item.className = `transcript-item ${data.role || 'system'}`;

        let roleLabel = 'System';
        if (data.role === 'bot') roleLabel = 'Agent';
        else if (data.role === 'user') roleLabel = 'You';
        else if (data.role === 'thought') roleLabel = 'Thinking';

        item.textContent = `${roleLabel}: ${data.text}`;
        log.appendChild(item);
        log.scrollTop = log.scrollHeight;
    });

    // Manual clicks (for testing)
    keys.forEach(key => {
        key.addEventListener('click', () => {
            const digit = key.getAttribute('data-key');
            handlePress(digit);
        });
    });
});

let intervalId = null;
let isPaused = false;

function formatCurrency(value, currency) {
    const units = ['', 'thousand', 'million', 'billion', 'trillion'];
    let unitIndex = 0;

    while (value >= 1000 && unitIndex < units.length - 1) {
        value /= 1000;
        unitIndex++;
    }

    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value) + ` ${units[unitIndex]}`;
}

function generateRandomCurrency() {
    const minValue = parseFloat(document.getElementById('minValue').value);
    const maxValue = parseFloat(document.getElementById('maxValue').value);
    const currencyType = document.getElementById('currencyType').value;

    if (isNaN(minValue) || isNaN(maxValue) || minValue < 0 || maxValue < 0 || minValue > maxValue) {
        alert('Please enter valid min and max values.');
        return;
    }

    const randomValue = Math.random() * (maxValue - minValue) + minValue;
    const formattedCurrency = formatCurrency(randomValue, currencyType);

    document.getElementById('currencyOutput').innerText = formattedCurrency;

    // Optional: Use Web Speech API to read the currency
    if (!isPaused) {
        speak(formattedCurrency);
    }
}

function startAutoGenerate() {
    const interval = parseInt(document.getElementById('intervalInput').value) * 1000;

    if (isNaN(interval) || interval < 1000) {
        alert('Please enter a valid interval (at least 1 second).');
        return;
    }

    stopAutoGenerate(); // Clear any existing interval
    intervalId = setInterval(generateRandomCurrency, interval);
    generateRandomCurrency(); // Generate immediately
}

function stopAutoGenerate() {
    clearInterval(intervalId);
    intervalId = null;
}

function togglePause() {
    isPaused = !isPaused;
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();
    utterance.voice = voices.find(voice => voice.lang === 'en-US') || voices[0];
    window.speechSynthesis.speak(utterance);
}
let currentMode = null;
let isPaused = false;
let intervalId = null;
let timerId = null;
let currentText = '';
let intervalSeconds = 0;
let secondsLeft = 0;
let speakRepeatId = null; // interval id cho lặp lại phát âm

const modeOrder = ['number', 'year', 'word'];

function speak(text) {
    if (text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
    }
}

function addWords() {
    const word = document.getElementById('wordInput').value.trim();
    const guide = document.getElementById('guideInput').value.trim();
    const type = document.getElementById('typeInput').value;  // select
    const translation = document.getElementById('translationInput').value.trim();

    if (!word) {
        alert('Hãy nhập từ.');
        return;
    }

    const data = {
        word: word,
        guide: guide,
        type: type,
        translation: translation
    };

    $.ajax({
        url: '/words',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(res) {
            alert(res.message || 'Đã thêm từ!');
            showWordList();
        },
        error: function(err) {
            alert(err.responseJSON?.error || 'Lỗi khi thêm từ!');
        }
    });

    $.ajax({
        url: '/guides',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
                   word: word,
                   guide: guide
        }),
        success: function(res) {
            alert(res.message || 'Đã thêm hướng dẫn!');
            showWordList();
        },
        error: function(err) {
            alert(err.responseJSON?.error || 'Lỗi khi thêm hướng dẫn!');
        }
    });
    const defaultTypeValue= document.getElementById('typeInput').options[0].value;
    document.getElementById('wordInput').value = "";
    document.getElementById('guideInput').value = "";
    document.getElementById('typeInput').value = defaultTypeValue;
    document.getElementById('translationInput').value = "";
}


function getNextMode(mode) {
    const idx = modeOrder.indexOf(mode);
    return modeOrder[(idx + 1) % modeOrder.length];
}

function clearSpeakRepeat() {
    if (speakRepeatId) {
        clearInterval(speakRepeatId);
        speakRepeatId = null;
    }
}

function setupSpeakRepeat() {
    clearSpeakRepeat();
    if (document.getElementById('autoSpeakCheckbox').checked) {
        let repeatSec = parseInt(document.getElementById('repeatSpeakInterval').value) || 2;
        speak(currentText);
        speakRepeatId = setInterval(() => {
            if (isPaused) return;
            speak(currentText);
        }, repeatSec * 1000);
    }
}

function startPractice(mode) {
    if (intervalId) clearInterval(intervalId);
    if (timerId) clearInterval(timerId);
    clearSpeakRepeat();
    currentMode = mode;
    isPaused = false;
    intervalSeconds = parseInt(document.getElementById('intervalInput').value) || 6;
    secondsLeft = intervalSeconds;
    document.getElementById('status').innerText = 'Practicing...';
    updateTimer();
    loadContent(mode, true);

    timerId = setInterval(() => {
        if (!isPaused) {
            intervalSeconds = parseInt(document.getElementById('intervalInput').value) || 6;
            secondsLeft--;
            updateTimer();
            if (secondsLeft <= 0) {
                secondsLeft = intervalSeconds;
                loadContent(currentMode, true);
            }
        }
    }, 1000);
}

function updateTimer() {
    document.getElementById('timer').innerText = `Còn lại: ${secondsLeft}s`;
}

function loadContent(mode, autoSpeak = false) {
    let params = {};
    if (mode === 'number') {
        let minVal = document.getElementById('minNumber').value;
        let maxVal = document.getElementById('maxNumber').value;
        params.min = (minVal !== '' && !isNaN(Number(minVal))) ? Number(minVal) : -1000;
        params.max = (maxVal !== '' && !isNaN(Number(maxVal))) ? Number(maxVal) : 1000000000;
    }
    if (mode === 'year') {
        let minYear = document.getElementById('minYear').value;
        let maxYear = document.getElementById('maxYear').value;
        params.min = (minYear !== '' && !isNaN(Number(minYear))) ? Number(minYear) : 1;
        params.max = (maxYear !== '' && !isNaN(Number(maxYear))) ? Number(maxYear) : 2999;
    }
    if (mode === 'word') {
        params.max_show = parseInt(document.getElementById('maxShowPerDay').value) || 3;
    }
    $.get({
        url: `/get_content/${mode}`,
        data: params,
        success: function(data) {
            document.getElementById('output').innerHTML = `
                <div style="display: flex; align-items: flex-start;">
                    <div style="flex: 1; font-size: 1.3em;">${data.content}</div>
                    <div style="margin-left: 20px;">
                        <button onclick="readCurrent()" style="font-size:1.1em; padding:15px 25px;">Read</button>
                    </div>
                </div>
            `;
            currentText = data.text;
            currentMode = data.next_mode;
            // Lặp lại phát âm nếu checkbox được chọn và autoSpeak=true
            if (autoSpeak && document.getElementById('autoSpeakCheckbox').checked) {
                setupSpeakRepeat();
            } else {
                clearSpeakRepeat();
            }
        }
    });
}

function readCurrent() {
    speak(currentText);
}

function togglePause() {
    isPaused = !isPaused;
    document.getElementById('status').innerText = isPaused ? 'Paused' : 'Practicing...';
}

function updateInterval() {
    const val = parseInt(document.getElementById('intervalInput').value);
    const status = document.getElementById('intervalStatus');
    if (isNaN(val) || val < 1 || val > 60) {
        status.style.color = 'red';
        status.innerText = 'Giá trị không hợp lệ!';
    } else {
        status.style.color = 'green';
        status.innerText = 'Đã cập nhật!';
        // Nếu đang luyện tập thì cập nhật ngay
        intervalSeconds = val;
        secondsLeft = val;
        updateTimer();
    }
    setTimeout(() => { status.innerText = ''; }, 2000);
}

function showWordList() {
    $.get('/words', function(words) {
        if (!words.length) {
            document.getElementById('wordList').innerHTML = '<i>Chưa có từ nào.</i>';
            return;
        }
        let html = '<b>Danh sách từ:</b><ul style="margin-top:5px;">';
        words.forEach(word => {
            html += `<li>${word} <button onclick="deleteWord('${word}')" style="font-size:0.9em;padding:2px 8px;margin-left:8px;">Xoá</button></li>`;
        });
        html += '</ul>';
        document.getElementById('wordList').innerHTML = html;
    });
}

function deleteWord(word) {
    if (!confirm(`Delete "${word}"?`)) return;
    fetch(`/words/${encodeURIComponent(word)}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.words) renderWordList(data.words);
            else alert(data.error || 'Delete failed');
        });
}

// Gọi showWordList khi thêm từ mới


function searchWordList() {
    const q = document.getElementById('searchInput').value.trim();
    if (!q) {
        showWordList();
        return;
    }
    $.get('/words/search?q=' + encodeURIComponent(q), function(words) {
        if (!words.length) {
            document.getElementById('wordList').innerHTML = '<i>Không tìm thấy từ nào.</i>';
            return;
        }
        let html = '<b>Kết quả tìm kiếm:</b><ul style="margin-top:5px;">';
        words.forEach(word => {
            html += `<li>${word} <button onclick="deleteWord('${word}')" style="font-size:0.9em;padding:2px 8px;margin-left:8px;">Xoá</button></li>`;
        });
        html += '</ul>';
        document.getElementById('wordList').innerHTML = html;
    });
}

// Hiển thị danh sách từ khi trang vừa load
window.onload = function() {
    showWordList();
};
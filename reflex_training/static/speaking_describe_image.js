let speakings = [];
let currentSpeaking = null;

function addSpeaking() {
    const title = $('#titleInput').val().trim();
    const script = $('#scriptInput').val().trim();
    const type = $('#typeInput').val();
    const imageFile = $('#imageInput')[0].files[0];

    if (!title || !script || !type || !imageFile) {
        alert('Vui lòng điền đầy đủ thông tin!');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        const imageBase64 = e.target.result;
        const newSpeaking = {
            id: Date.now(),
            title,
            script,
            image: imageBase64,
            type,
            created_at: new Date().toISOString()
        };

        $.ajax({
            url: '/speaking_describe_image',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(newSpeaking),
            success: function() {
                alert('Đã thêm bài nói!');
                loadSpeakings();
                $('#addSpeakingForm')[0].reset();
                $('#previewImage').hide();
            }
        });
    };
    reader.readAsDataURL(imageFile);
}

function loadSpeakings() {
    $.get('/speaking_describe_image', function(data) {
        speakings = data;
        renderSpeakingList(speakings);
    });
}

function renderSpeakingList(list) {
    const container = $('#speakingList');
    container.empty();
    list.forEach(item => {
        container.append(`
            <div style="border:1px solid #ccc; padding:10px; width:200px;">
                <img src="${item.image}" alt="${item.title}" style="width:100%; height:120px; object-fit:cover;">
                <h4>${item.title}</h4>
                <p>Loại: ${item.type}</p>
                <button onclick="viewSpeaking(${item.id})">Xem chi tiết</button>
            </div>
        `);
    });
}

function filterSpeakings() {
    const keyword = $('#searchInput').val().trim().toLowerCase();
    const type = $('#filterType').val();
    const filtered = speakings.filter(item => {
        const matchesKeyword = item.title.toLowerCase().includes(keyword) || item.script.toLowerCase().includes(keyword);
        const matchesType = !type || item.type === type;
        return matchesKeyword && matchesType;
    });
    renderSpeakingList(filtered);
}

$('#imageInput').on('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            $('#previewImage').attr('src', e.target.result).show();
        };
        reader.readAsDataURL(file);
    }
});

$(document).ready(function() {
    loadSpeakings();
});

function loadCurrentSpeaking() {
    $.get('/speaking_describe_image/practice', function(speaking) {
        if (!speaking || !speaking.title) {
            alert('Không có bài học nào để học!');
            return;
        }
        currentSpeaking = speaking;
        renderCurrentSpeaking(speaking);
    });
}

function saveCurrentSpeaking(speaking) {
    $.ajax({
        url: '/speaking_describe_image/practice',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ speaking: speaking }),
        success: function() {
            console.log('Bài học hiện tại đã được lưu.');
        }
    });
}

function renderCurrentSpeaking(speaking) {
    $('#currentSpeaking').html(`
        <h3>${speaking.title}</h3>
        <p><b>Loại:</b> ${speaking.type}</p>
        <p><b>Script:</b> ${speaking.script}</p>
        <img src="${speaking.image}" alt="${speaking.title}" style="max-width:100%; margin-top:10px;">
    `);
}

function nextSpeaking() {
    $.get('/speaking_describe_image', function(speakings) {
        const currentIndex = speakings.findIndex(s => s.id === currentSpeaking.id);
        const nextIndex = (currentIndex + 1) % speakings.length; // Lấy bài tiếp theo (vòng lặp)
        currentSpeaking = speakings[nextIndex];
        renderCurrentSpeaking(currentSpeaking);
        saveCurrentSpeaking(currentSpeaking);
    });
}
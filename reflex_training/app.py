from flask import Flask, render_template, request, jsonify
import random
import json
import os

app = Flask(__name__)

# Đường dẫn tới file lưu trữ hướng dẫn phát âm
GUIDES_FILE = 'pronunciation_guides.json'
WORDS_FILE = 'words.json'

def load_words():
    """Tải danh sách từ từ file"""
    if os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_words(words):
    """Lưu danh sách từ vào file"""
    with open(WORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=4)

def load_guides():
    """Tải hướng dẫn phát âm từ file"""
    if os.path.exists(GUIDES_FILE):
        with open(GUIDES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_guides(guides):
    """Lưu hướng dẫn phát âm vào file"""
    with open(GUIDES_FILE, 'w', encoding='utf-8') as f:
        json.dump(guides, f, ensure_ascii=False, indent=4)

def get_pronunciation_guide(word):
    """Cung cấp hướng dẫn đọc cho từ/cụm từ"""
    pronunciation_guides = {
        "about it": "Pronounce as /əˈbaʊt ɪt/, linking 'about' and 'it' smoothly with a quick transition.",
        "going to": "Pronounce as /ˈɡoʊɪŋ tə/, often reduced to 'gonna' in casual speech.",
        "want to": "Pronounce as /ˈwɑːnt tə/, often reduced to 'wanna' in casual speech."
    }
    return pronunciation_guides.get(word, f"Pronounce '{word}' naturally, linking words smoothly if applicable.")

@app.route('/')
def index():
    """Hiển thị giao diện chính"""
    return render_template('index.html')

@app.route('/words', methods=['GET'])
def get_words():
    """Lấy danh sách từ"""
    return jsonify(load_words())

@app.route('/words', methods=['POST'])
def add_word():
    """Thêm từ mới vào danh sách"""
    data = request.json
    word = data.get('word', '').strip()
    if not word:
        return jsonify({'error': 'Missing word'}), 400
    words = load_words()
    if word in words:
        return jsonify({'error': 'Word already exists'}), 400
    words.append(word)
    save_words(words)
    return jsonify({'message': 'Word added', 'words': words})

@app.route('/words/<word>', methods=['DELETE'])
def delete_word(word):
    """Xóa từ khỏi danh sách"""
    words = load_words()
    if word in words:
        words.remove(word)
        save_words(words)
        return jsonify({'message': f"Deleted word '{word}'", 'words': words})
    return jsonify({'error': 'Word not found'}), 404

@app.route('/words/<word>', methods=['PUT'])
def update_word(word):
    """Cập nhật từ trong danh sách"""
    data = request.json
    new_word = data.get('new_word', '').strip()
    words = load_words()
    if word not in words:
        return jsonify({'error': 'Word not found'}), 404
    if new_word in words:
        return jsonify({'error': 'New word already exists'}), 400
    idx = words.index(word)
    words[idx] = new_word
    save_words(words)
    return jsonify({'message': 'Word updated', 'words': words})

@app.route('/words/search')
def search_word():
    """Tìm kiếm từ trong danh sách"""
    q = request.args.get('q', '').strip().lower()
    words = load_words()
    result = [w for w in words if q in w.lower()]
    return jsonify(result)

@app.route('/guides', methods=['GET'])
def get_guides():
    """Lấy danh sách hướng dẫn phát âm"""
    return jsonify(load_guides())

@app.route('/guides', methods=['POST'])
def add_or_update_guide():
    """Thêm hoặc cập nhật hướng dẫn phát âm cho từ"""
    data = request.json
    word = data.get('word')
    guide = data.get('guide')
    if not word or not guide:
        return jsonify({'error': 'Missing word or guide'}), 400
    guides = load_guides()
    guides[word] = guide
    save_guides(guides)
    return jsonify({'message': 'Guide added/updated', 'guides': guides})

@app.route('/guides/<word>', methods=['DELETE'])
def delete_guide(word):
    """Xóa hướng dẫn phát âm cho từ"""
    guides = load_guides()
    if word in guides:
        del guides[word]
        save_guides(guides)
        return jsonify({'message': f"Deleted guide for '{word}'"})
    return jsonify({'error': 'Word not found'}), 404

@app.route('/get_content/<mode>')
def get_content(mode):
    """Tạo nội dung ngẫu nhiên dựa trên mode"""
    if mode == 'number':
        try:
            min_num = int(request.args.get('min', -1000))
            max_num = int(request.args.get('max', 1000000000))
        except (TypeError, ValueError):
            min_num = -1000
            max_num = 1000000000
        if min_num > max_num:
            min_num, max_num = max_num, min_num
        number = random.randint(min_num, max_num)
        formatted_number = f"{number:,}"
        return jsonify({'content': f"Random Number: {formatted_number}", 'text': str(number), 'next_mode': 'number'})
    elif mode == 'year':
        try:
            min_year = int(request.args.get('min', 1))
            max_year = int(request.args.get('max', 2999))
        except (TypeError, ValueError):
            min_year = 1
            max_year = 2999
        if min_year > max_year:
            min_year, max_year = max_year, min_year
        year = random.randint(min_year, max_year)
        return jsonify({'content': f"Random Year: {year}", 'text': str(year), 'next_mode': 'year'})
    elif mode == 'word':
        words = load_words()
        if not words:
            return jsonify({'content': 'No words in the list. Please add words.', 'text': '', 'next_mode': 'word'})
        word = random.choice(words)
        guide = get_pronunciation_guide(word)
        return jsonify({'content': f"Practice this: {word}<br>Pronunciation Guide: {guide}", 'text': word, 'next_mode': 'word'})
    return jsonify({'content': 'Invalid mode', 'text': '', 'next_mode': mode})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
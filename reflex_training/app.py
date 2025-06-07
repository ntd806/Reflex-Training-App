from flask import Flask, render_template, request, jsonify
import random
import json
import os
from urllib.parse import unquote
import datetime
import pandas as pd
import requests

app = Flask(__name__)

# Đường dẫn tới file lưu trữ hướng dẫn phát âm
GUIDES_FILE = 'pronunciation_guides.json'
WORDS_FILE = 'words.json'
SENTENCES_FILE = 'sentences.json'
REPEAT_SENTENCES_FILE = 'repeat_sentences.json'
YOUTUBE_LINKS_FILE = 'youtube_links.json'

def today_str():
    return datetime.date.today().isoformat()

def load_words():
    """Tải danh sách từ từ file"""
    if os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Nếu là danh sách string cũ thì chuyển sang object
            if data and isinstance(data[0], str):
                data = [{"word": w, "priority": False, "shown_today": 0, "last_shown_date": ""} for w in data]
            return data
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

def load_sentences():
    if os.path.exists(SENTENCES_FILE):
        with open(SENTENCES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_sentences(sentences):
    with open(SENTENCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(sentences, f, ensure_ascii=False, indent=4)

def load_repeat_sentences():
    if os.path.exists(REPEAT_SENTENCES_FILE):
        with open(REPEAT_SENTENCES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_repeat_sentences(sentences):
    with open(REPEAT_SENTENCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(sentences, f, ensure_ascii=False, indent=4)

def load_youtube_links():
    if os.path.exists(YOUTUBE_LINKS_FILE):
        with open(YOUTUBE_LINKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_youtube_links(links):
    with open(YOUTUBE_LINKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=4)

def get_pronunciation_guide(word):
    guides = load_guides()
    for k, v in guides.items():
        if k.strip().lower() == word.strip().lower():
            return v
    return "No guide available."

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
        return jsonify({'error': 'Word is required'}), 400

    words = load_words()
    # Kiểm tra trùng lặp
    for w in words:
        if isinstance(w, dict) and w.get('word', '').strip().lower() == word.lower():
            return jsonify({'error': 'Word already exists'}), 400

    # Đảm bảo chỉ thêm object đúng định dạng
    new_word = {
        "word": word,
        "priority": False,
        "shown_today": 0,
        "last_shown_date": ""
    }
    words.append(new_word)

    # Lọc lại list, chỉ giữ object đúng định dạng
    words = [w for w in words if isinstance(w, dict) and 'word' in w]

    save_words(words)
    return jsonify({'message': 'Word added', 'words': [w['word'] for w in words]})

@app.route('/words/<path:word>', methods=['DELETE'])
def delete_word(word):
    """Xóa từ khỏi danh sách"""
    word = unquote(word).strip()
    words = load_words()
    print(f"Trying to delete: '{word}'")
    print("Current words:", words)
    for w in words:
        if w.strip() == word:
            words.remove(w)
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
        return jsonify({'error': 'Word and guide are required'}), 400
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

@app.route('/sentences', methods=['GET'])
def get_sentences():
    return jsonify(load_sentences())

@app.route('/sentences', methods=['POST'])
def add_sentence():
    data = request.json
    sentence = data.get('sentence', '').strip()
    if not sentence:
        return jsonify({'error': 'Missing sentence'}), 400
    sentences = load_sentences()
    # Kiểm tra trùng
    for item in sentences:
        s = item['sentence'] if isinstance(item, dict) else item
        if s == sentence:
            return jsonify({'error': 'Sentence already exists'}), 400
    # Thêm các trường mới
    sentences.append({
        'sentence': sentence,
        'priority': False,
        'shown_today': 0,
        'last_shown_date': ''
    })
    save_sentences(sentences)
    return jsonify({'message': 'Sentence added', 'sentences': sentences})

@app.route('/sentences/random')
def random_sentence():
    sentences = load_sentences()
    if not sentences:
        return jsonify({'sentence': '', 'message': 'No sentences available'})
    # Chỉ lấy object, nếu là string thì chuyển sang object
    for i, s in enumerate(sentences):
        if isinstance(s, str):
            sentences[i] = {
                'sentence': s,
                'priority': False,
                'shown_today': 0,
                'last_shown_date': ''
            }
    s = random.choice(sentences)
    # Cập nhật shown_today và last_shown_date
    today = datetime.date.today().isoformat()
    s['shown_today'] = s.get('shown_today', 0) + 1
    s['last_shown_date'] = today
    save_sentences(sentences)
    return jsonify({'sentence': s['sentence']})

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
        max_show = int(request.args.get('max_show', 3))
        today = today_str()
        # Reset shown_today nếu sang ngày mới
        for w in words:
            if w['last_shown_date'] != today:
                w['shown_today'] = 0
                w['last_shown_date'] = today
        save_words(words)
        # Ưu tiên lấy từ priority chưa đủ số lần/ngày
        priority_words = [w for w in words if w['priority'] and w['shown_today'] < max_show]
        normal_words = [w for w in words if not w['priority'] and w['shown_today'] < max_show]
        candidates = priority_words if priority_words else normal_words
        if not candidates:
            return jsonify({'content': 'Đã hoàn thành hết các từ ưu tiên/ngày!', 'text': '', 'next_mode': 'word'})
        word_obj = random.choice(candidates)
        word_obj['shown_today'] += 1
        word_obj['last_shown_date'] = today
        save_words(words)
        guide = get_pronunciation_guide(word_obj['word'])
        return jsonify({'content': f"Practice this: {word_obj['word']}<br>Pronunciation Guide: {guide}", 'text': word_obj['word'], 'next_mode': 'word'})
    return jsonify({'content': 'Invalid mode', 'text': '', 'next_mode': mode})

@app.route('/words/priority/<word>', methods=['POST'])
def toggle_priority(word):
    words = load_words()
    for w in words:
        if w['word'] == word:
            w['priority'] = not w.get('priority', False)
            save_words(words)
            return jsonify({'message': 'Updated', 'words': words})
    return jsonify({'error': 'Word not found'}), 404

@app.route('/priority_words')
def get_priority_words():
    words = load_words()
    priority = [w['word'] for w in words if w.get('priority')]
    return jsonify(priority)

@app.route('/sentence_practice')
def sentence_practice():
    return render_template('sentence.html')

@app.route('/repeat_sentence')
def repeat_sentence():
    return render_template('repeat_sentence.html')

@app.route('/sentences/<sentence>', methods=['DELETE'])
def delete_sentence(sentence):
    sentences = load_sentences()
    # Hỗ trợ cả dạng object và string
    new_sentences = []
    for item in sentences:
        s = item['sentence'] if isinstance(item, dict) else item
        if s != sentence:
            new_sentences.append(item)
    save_sentences(new_sentences)
    return jsonify({'message': 'Deleted'})

@app.route('/sentences/priority/<sentence>', methods=['POST'])
def toggle_sentence_priority(sentence):
    sentences = load_sentences()
    found = False
    for i, item in enumerate(sentences):
        if isinstance(item, str):
            if item == sentence:
                sentences[i] = {'sentence': item, 'priority': True}
                found = True
        elif item.get('sentence') == sentence:
            item['priority'] = not item.get('priority', False)
            found = True
    if found:
        save_sentences(sentences)
        return jsonify({'message': 'Updated'})
    return jsonify({'error': 'Sentence not found'}), 404

@app.route('/repeat_sentences', methods=['GET'])
def get_repeat_sentences():
    return jsonify(load_repeat_sentences())

@app.route('/repeat_sentences', methods=['POST'])
def add_repeat_sentence():
    data = request.json
    sentence = data.get('sentence', '').strip()
    if not sentence:
        return jsonify({'error': 'Missing sentence'}), 400
    sentences = load_repeat_sentences()
    # Kiểm tra trùng
    for item in sentences:
        s = item['sentence'] if isinstance(item, dict) else item
        if s == sentence:
            return jsonify({'error': 'Sentence already exists'}), 400
    # Thêm các trường mới
    sentences.append({
        'sentence': sentence,
        'priority': False,
        'shown_today': 0,
        'last_shown_date': ''
    })
    save_repeat_sentences(sentences)
    return jsonify({'message': 'Sentence added', 'sentences': sentences})

@app.route('/repeat_sentences/random')
def random_repeat_sentence():
    sentences = load_repeat_sentences()
    if not sentences:
        return jsonify({'sentence': '', 'message': 'No sentences available'})
    # Chỉ lấy object, nếu là string thì chuyển sang object
    for i, s in enumerate(sentences):
        if isinstance(s, str):
            sentences[i] = {
                'sentence': s,
                'priority': False,
                'shown_today': 0,
                'last_shown_date': ''
            }
    s = random.choice(sentences)
    # Cập nhật shown_today và last_shown_date
    today = datetime.date.today().isoformat()
    s['shown_today'] = s.get('shown_today', 0) + 1
    s['last_shown_date'] = today
    save_repeat_sentences(sentences)
    return jsonify({'sentence': s['sentence']})

@app.route('/repeat_sentences/<sentence>', methods=['DELETE'])
def delete_repeat_sentence(sentence):
    sentences = load_repeat_sentences()
    new_sentences = []
    for item in sentences:
        s = item['sentence'] if isinstance(item, dict) else item
        if s != sentence:
            new_sentences.append(item)
    save_repeat_sentences(new_sentences)
    return jsonify({'message': 'Deleted'})

@app.route('/repeat_sentences/priority/<sentence>', methods=['POST'])
def toggle_repeat_sentence_priority(sentence):
    sentences = load_repeat_sentences()
    found = False
    for i, item in enumerate(sentences):
        if isinstance(item, str):
            if item == sentence:
                sentences[i] = {'sentence': item, 'priority': True}
                found = True
        elif item.get('sentence') == sentence:
            item['priority'] = not item.get('priority', False)
            found = True
    if found:
        save_repeat_sentences(sentences)
        return jsonify({'message': 'Updated'})
    return jsonify({'error': 'Sentence not found'}), 404

@app.route('/upload_sentences', methods=['POST'])
def upload_sentences():
    file = request.files.get('excelFile')
    target = request.form.get('target', 'sentences')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    try:
        df = pd.read_excel(file)
        # Giả sử cột đầu tiên là câu, tên cột là 'sentence' hoặc không có header
        if 'sentence' in df.columns:
            sentences = df['sentence'].dropna().astype(str).tolist()
        else:
            sentences = df.iloc[:,0].dropna().astype(str).tolist()
        if target == 'sentences':
            data = load_sentences()
            for s in sentences:
                if not any((isinstance(item, dict) and item.get('sentence') == s) or item == s for item in data):
                    data.append({
                        'sentence': s,
                        'priority': False,
                        'shown_today': 0,
                        'last_shown_date': ''
                    })
            save_sentences(data)
        elif target == 'repeat_sentences':
            data = load_repeat_sentences()
            for s in sentences:
                if not any((isinstance(item, dict) and item.get('sentence') == s) or item == s for item in data):
                    data.append({
                        'sentence': s,
                        'priority': False,
                        'shown_today': 0,
                        'last_shown_date': ''
                    })
            save_repeat_sentences(data)
        elif target == 'words':
            data = load_words()
            for s in sentences:
                if not any((isinstance(item, dict) and item.get('word') == s) or item == s for item in data):
                    data.append({'word': s, 'priority': False, 'shown_today': 0, 'last_shown_date': ''})
            save_words(data)
        else:
            return jsonify({'error': 'Invalid target'}), 400
        return jsonify({'message': f'Đã thêm {len(sentences)} câu/từ!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/youtube_tracker')
def youtube_tracker():
    return render_template('youtube_tracker.html')

@app.route('/youtube_links', methods=['GET'])
def get_youtube_links():
    return jsonify(load_youtube_links())

@app.route('/youtube_links', methods=['POST'])
def add_youtube_link():
    data = request.json
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'Missing URL'}), 400
    links = load_youtube_links()
    if any(link['url'] == url for link in links):
        return jsonify({'error': 'Link đã tồn tại!'}), 400
    # Lấy tiêu đề video từ noembed
    title = url
    try:
        resp = requests.get('https://noembed.com/embed', params={'url': url}, timeout=5)
        if resp.ok:
            info = resp.json()
            if 'title' in info:
                title = info['title']
    except Exception:
        pass
    links = load_youtube_links()
    links.append({
        'url': url,
        'title': title,
        'added_date': today_str(),
        'watched': False,
        'last_time': 0
    })
    save_youtube_links(links)
    return jsonify({'message': 'Added', 'links': links})

@app.route('/youtube_links/update', methods=['POST'])
def update_youtube_link():
    data = request.json
    url = data.get('url')
    last_time = data.get('last_time', 0)
    watched = data.get('watched', None)
    links = load_youtube_links()
    for link in links:
        if link['url'] == url:
            if last_time is not None:
                link['last_time'] = last_time
            if watched is not None:
                link['watched'] = watched
    save_youtube_links(links)
    return jsonify({'message': 'Updated'})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
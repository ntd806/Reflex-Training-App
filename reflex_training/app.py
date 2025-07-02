from flask import Flask, render_template, request, jsonify
import random
import json
import os
from urllib.parse import unquote
import datetime
import pandas as pd
import requests
import time

app = Flask(__name__)

# Đường dẫn tới file lưu trữ hướng dẫn phát âm
GUIDES_FILE = 'pronunciation_guides.json'
WORDS_FILE = 'words.json'
SENTENCES_FILE = 'sentences.json'
REPEAT_SENTENCES_FILE = 'repeat_sentences.json'
YOUTUBE_LINKS_FILE = 'youtube_links.json'
ENDING_WORDS_FILE = os.path.join(os.path.dirname(__file__), 'ending_words.json')
IRREGULAR_VERBS_FILE = os.path.join(os.path.dirname(__file__), 'irregular_verbs.json')
CURRENT_SPEAKING_FILE = os.path.join(os.path.dirname(__file__), 'current_speaking.json')
LESSON_STATS_FILE = os.path.join(os.path.dirname(__file__), 'lesson_stats.json')

def today_str():
    return datetime.date.today().isoformat()

def load_words():
    """Tải danh sách từ từ file và thêm hướng dẫn phát âm từ pronunciation_guides.json"""
    words = []
    guides = load_guides()  # Tải hướng dẫn phát âm từ pronunciation_guides.json

    if os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Nếu là danh sách string cũ thì chuyển sang object
            if data and isinstance(data[0], str):
                words = [{"word": w, "translation": "", "guide": guides.get(w, ""), "priority": False, "shown_today": 0, "last_shown_date": ""} for w in data]
            else:
                # Thêm hướng dẫn phát âm vào từng từ
                for word_obj in data:
                    word_obj["guide"] = guides.get(word_obj["word"], "")
                    words.append(word_obj)
    return words

def save_words(words):
    """Lưu danh sách từ vào file"""
    with open(WORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=4)

def load_guides():
    """Tải hướng dẫn phát âm từ file pronunciation_guides.json"""
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

def load_ending_words():
    if os.path.exists(ENDING_WORDS_FILE):
        with open(ENDING_WORDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure 'priority' and 'timestamp' fields exist
            for word_list_name in ["sWords", "edWords"]:
                if word_list_name in data:
                    for word_obj in data[word_list_name]:
                        if "priority" not in word_obj:
                            word_obj["priority"] = False
                        if "timestamp" not in word_obj:
                            word_obj["timestamp"] = 0  # Default timestamp for old entries
            return data
    return {"sWords": [], "edWords": []}

def save_ending_words(data):
    with open(ENDING_WORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_irregular_verbs():
    """Load irregular verbs from JSON file"""
    try:
        if os.path.exists(IRREGULAR_VERBS_FILE):
            with open(IRREGULAR_VERBS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded {len(data)} verbs") # Debug log
                return data
        else:
            print(f"File not found: {IRREGULAR_VERBS_FILE}") # Debug log
            return []
    except Exception as e:
        print(f"Error loading irregular verbs: {e}") # Debug log
        return []

def save_irregular_verbs(data):
    with open(IRREGULAR_VERBS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_current_speaking():
    """Tải bài học hiện tại từ file"""
    if os.path.exists(CURRENT_SPEAKING_FILE):
        with open(CURRENT_SPEAKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_current_speaking(speaking):
    """Lưu bài học hiện tại vào file"""
    with open(CURRENT_SPEAKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(speaking, f, ensure_ascii=False, indent=4)

def load_lesson_stats():
    if os.path.exists(LESSON_STATS_FILE):
        with open(LESSON_STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_lesson_stats(stats):
    with open(LESSON_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

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
    """Lấy danh sách từ (mới nhất lên đầu)"""
    words = load_words()
    # Đảo ngược danh sách để từ mới nhất lên đầu
    return jsonify(list(reversed(words)))

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
    words = load_words()
    # If words is a list of dicts with 'word' key:
    for w in words:
        if (w.get('word') if isinstance(w, dict) else w) == word:
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

    # Ensure words is a list of strings or dictionaries with a 'word' key
    result = []
    for w in words:
        if isinstance(w, str) and q in w.lower():
            result.append(w)
        elif isinstance(w, dict) and 'word' in w and q in w['word'].lower():
            result.append(w)

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
    data = request.get_json()
    sentence = data.get('sentence', '').strip()
    transcript = data.get('transcript', '').strip() if 'transcript' in data else ''
    if not sentence:
        return jsonify({'error': 'Sentence is required'}), 400
    sentences = load_sentences()
    if any((s.get('sentence') if isinstance(s, dict) else s) == sentence for s in sentences):
        return jsonify({'error': 'Sentence already exists'}), 400
    sentences.append({
        'sentence': sentence,
        'transcript': transcript,
        'priority': False,
        'shown_today': 0,
        'last_shown_date': ''
    })
    save_sentences(sentences)
    return jsonify({'message': 'Sentence added'})

@app.route('/sentences/random')
def random_sentence():
    sentences = load_sentences()
    if not sentences:
        return jsonify({'sentence': '', 'message': 'No sentences available'})
    today = datetime.date.today().isoformat()
    max_show = int(request.args.get('max_show', 3))
    for i, s in enumerate(sentences):
        if isinstance(s, str):
            sentences[i] = {
                'sentence': s,
                'priority': False,
                'shown_today': 0,
                'last_shown_date': ''
            }
    for s in sentences:
        if s.get('last_shown_date') != today:
            s['shown_today'] = 0
            s['last_shown_date'] = today
    priority_sentences = [s for s in sentences if s.get('priority') and s.get('shown_today', 0) < max_show]
    normal_sentences = [s for s in sentences if not s.get('priority') and s.get('shown_today', 0) < max_show]
    candidates = priority_sentences if priority_sentences else normal_sentences
    if not candidates:
        save_sentences(sentences)
        return jsonify({'sentence': '', 'message': 'Đã hoàn thành hết các câu ưu tiên/ngày!'})
    s = random.choice(candidates)
    s['shown_today'] = s.get('shown_today', 0) + 1
    s['last_shown_date'] = today
    save_sentences(sentences)
    # Trả về cả transcript
    return jsonify({'sentence': s['sentence'], 'transcript': s.get('transcript', '')})

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

@app.route('/ending_practice')
def ending_practice():
    return render_template('ending_practice.html')

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
    data = request.get_json()
    sentence = data.get('sentence', '').strip()
    transcript = data.get('transcript', '').strip()
    if not sentence:
        return jsonify({'error': 'Sentence is required'}), 400
    sentences = load_repeat_sentences()
    if any((s.get('sentence') if isinstance(s, dict) else s) == sentence for s in sentences):
        return jsonify({'error': 'Sentence already exists'}), 400
    sentences.append({
        'sentence': sentence,
        'transcript': transcript,
        'priority': False,
        'shown_today': 0,
        'last_shown_date': ''
    })
    save_repeat_sentences(sentences)
    return jsonify({'message': 'Sentence added'})

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
    # Trả về cả transcript
    return jsonify({'sentence': s['sentence'], 'transcript': s.get('transcript', '')})

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

@app.route('/repeat_sentences/priority/', methods=['POST'])
def toggle_repeat_sentence_priority():
    data = request.get_json()
    sentence = data.get('sentence')
    sentences = load_repeat_sentences()
    for item in sentences:
        if item.get('sentence') == sentence:
            item['priority'] = not item.get('priority', False)
            save_repeat_sentences(sentences)
            return jsonify({'message': 'Priority toggled'})
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
    video_type = data.get('video_type', '').strip()
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
        'last_time': 0,
        'video_type': video_type
    })
    save_youtube_links(links)
    return jsonify({'message': 'Added', 'links': links})

@app.route('/youtube_links/update', methods=['POST'])
def update_youtube_link():
    data = request.json
    url = data.get('url')
    last_time = data.get('last_time', 0)
    watched = data.get('watched', None)
    transcript = data.get('transcript', None)
    links = load_youtube_links()
    for link in links:
        if link['url'] == url:
            if last_time is not None:
                link['last_time'] = last_time
            if watched is not None:
                link['watched'] = watched
            if transcript is not None:
                link['transcript'] = transcript
    save_youtube_links(links)
    return jsonify({'message': 'Updated'})

@app.route('/repeat_sentences/transcript/<sentence>', methods=['POST'])
def update_repeat_sentence_transcript(sentence):
    data = request.get_json()
    transcript = data.get('transcript', '').strip()
    sentences = load_repeat_sentences()
    for s in sentences:
        if s.get('sentence') == sentence:
            s['transcript'] = transcript
            save_repeat_sentences(sentences)
            return jsonify({'message': 'Transcript updated'})
    return jsonify({'error': 'Sentence not found'}), 404

@app.route('/sentences/transcript/<sentence>', methods=['POST'])
def update_sentence_transcript(sentence):
    data = request.get_json()
    transcript = data.get('transcript', '').strip()
    sentences = load_sentences()
    for s in sentences:
        if s.get('sentence') == sentence:
            s['transcript'] = transcript
            save_sentences(sentences)
            return jsonify({'message': 'Transcript updated'})
    return jsonify({'error': 'Sentence not found'}), 404

@app.route('/ending_words', methods=['GET'])
def get_ending_words():
    data = load_ending_words()
    # Reverse the lists to show newest first
    data["sWords"] = list(reversed(data["sWords"]))
    data["edWords"] = list(reversed(data["edWords"]))
    return jsonify(data)

@app.route('/ending_words', methods=['POST'])
def update_ending_words():
    data = request.get_json()
    # Add timestamp to new words
    current_time = int(time.time())
    for word_list in [data["sWords"], data["edWords"]]:
        for word in word_list:
            if "timestamp" not in word:
                word["timestamp"] = current_time
    save_ending_words(data)
    return jsonify({"message": "Updated"})

@app.route('/ending_words/toggle_priority', methods=['POST'])
def toggle_ending_word_priority():
    data = request.get_json()
    word = data.get('word')
    word_type = data.get('word_type')  # "sWords" or "edWords"

    if not word or not word_type:
        return jsonify({"error": "Word and word_type are required"}), 400

    ending_words = load_ending_words()
    word_list = ending_words.get(word_type)

    if not word_list:
        return jsonify({"error": f"Invalid word_type: {word_type}"}), 400

    for word_obj in word_list:
        if word_obj["word"] == word:
            word_obj["priority"] = not word_obj["priority"]
            save_ending_words(ending_words)
            return jsonify({"message": f"Priority toggled for {word}"})

    return jsonify({"error": f"Word not found: {word}"}), 404

@app.route('/irregular_verbs')
def irregular_verbs_page():
    return render_template('irregular_verbs.html')

@app.route('/api/irregular_verbs', methods=['GET'])
def get_irregular_verbs():
    return jsonify(load_irregular_verbs())

@app.route('/api/irregular_verbs', methods=['POST'])
def add_irregular_verb():
    verb = request.get_json()
    verbs = load_irregular_verbs()
    if any(v['v1'] == verb['v1'] for v in verbs):
        return jsonify({"error": "Verb already exists"}), 400
    verbs.append(verb)
    save_irregular_verbs(verbs)
    return jsonify({"message": "Verb added"})

@app.route('/api/irregular_verbs/toggle_priority', methods=['POST'])
def toggle_irregular_verb_priority():
    data = request.get_json()
    v1 = data.get('v1')
    verbs = load_irregular_verbs()
    for verb in verbs:
        if verb['v1'] == v1:
            verb['priority'] = not verb.get('priority', False)
            save_irregular_verbs(verbs)
            return jsonify({"message": "Priority toggled"})
    return jsonify({"error": "Verb not found"}), 404

@app.route('/speaking_describe_image', methods=['GET'])
def get_speaking_list():
    """Trả về danh sách các bài học"""
    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)
        return jsonify(speakings)
    return jsonify([]), 404

@app.route('/speaking_describe_image_page', methods=['GET'])
def speaking_describe_image_page():
    """Render the Speaking Describe Image HTML page"""
    return render_template('speaking_describe_image.html')

@app.route('/speaking_describe_image', methods=['POST'])
def add_speaking():
    data = request.json
    if not data.get('title') or not data.get('script') or not data.get('image') or not data.get('type'):
        return jsonify({'error': 'Missing fields'}), 400

    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)
    else:
        speakings = []

    speakings.append(data)
    with open('speaking_describe_image.json', 'w', encoding='utf-8') as f:
        json.dump(speakings, f, ensure_ascii=False, indent=4)

    return jsonify({'message': 'Speaking added successfully!'})

@app.route('/speaking_describe_image/<int:item_id>', methods=['GET'])
def view_speaking_detail(item_id):
    """Render the detail page for a specific speaking item."""
    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)
        item = next((s for s in speakings if s['id'] == item_id), None)
        if item:
            return render_template('speaking_detail.html', item=item)
    return "Bài học không tồn tại", 404

@app.route('/speaking_describe_image/search', methods=['GET'])
def search_speakings():
    keyword = request.args.get('q', '').lower()

    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)

        # Lọc theo từ khóa
        filtered = [
            s for s in speakings
            if keyword in s['title'].lower() or keyword in s['script'].lower()
        ]
        return jsonify(filtered)

    return jsonify([])

@app.route('/speaking_describe_image/filter', methods=['GET'])
def filter_speakings():
    speaking_type = request.args.get('type', '')

    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)

        # Lọc theo loại bài nói
        filtered = [
            s for s in speakings
            if not speaking_type or s['type'] == speaking_type
        ]
        return jsonify(filtered)

    return jsonify([])

@app.route('/speaking_describe_image/practice', methods=['GET'])
def get_current_speaking():
    """Lấy bài học hiện tại hoặc bài đầu tiên"""
    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)
    else:
        speakings = []

    current_speaking = load_current_speaking()

    if not current_speaking:
        # Nếu chưa có bài học hiện tại, lấy bài đầu tiên
        if speakings:
            current_speaking = speakings[0]
            save_current_speaking(current_speaking)
        else:
            # Nếu danh sách bài học trống, trả về lỗi
            return jsonify({'error': 'No speaking lessons available'}), 404

    return jsonify(current_speaking)

@app.route('/speaking_describe_image/practice', methods=['POST'])
def save_current_speaking_api():
    """Lưu bài học hiện tại"""
    data = request.json
    speaking = data.get('speaking')
    if not speaking:
        return jsonify({'error': 'No speaking provided'}), 400

    save_current_speaking(speaking)
    return jsonify({'message': 'Current speaking saved successfully'})

@app.route('/random_currency', methods=['GET'])
def random_currency_page():
    """Render the Random Currency Generator page"""
    return render_template('random_currency.html')

@app.route('/lesson_stats', methods=['POST'])
def save_lesson_stats_api():
    stats = request.json.get('stats')
    if not isinstance(stats, dict):
        return jsonify({'error': 'Invalid stats'}), 400
    save_lesson_stats(stats)
    return jsonify({'message': 'Saved'})

@app.route('/lesson_stats', methods=['GET'])
def get_lesson_stats_api():
    return jsonify(load_lesson_stats())

@app.route('/speaking_describe_image/<int:item_id>', methods=['GET'])
def get_speaking_item(item_id):
    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)
        for item in speakings:
            if item.get('id') == item_id:
                return jsonify(item)
    return jsonify({'error': 'Item not found'}), 404

@app.route('/speaking_describe_image/<int:item_id>', methods=['PUT'])
def update_speaking(item_id):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)
    else:
        return jsonify({'error': 'No data file'}), 404
    updated = False
    for idx, item in enumerate(speakings):
        if item.get('id') == item_id:
            data['id'] = item_id
            speakings[idx] = data
            updated = True
            break
    if not updated:
        return jsonify({'error': 'Item not found'}), 404
    with open('speaking_describe_image.json', 'w', encoding='utf-8') as f:
        json.dump(speakings, f, ensure_ascii=False, indent=4)
    return jsonify({'message': 'Updated successfully'})

@app.route('/speaking_describe_image/<int:item_id>', methods=['DELETE'])
def delete_speaking(item_id):
    if os.path.exists('speaking_describe_image.json'):
        with open('speaking_describe_image.json', 'r', encoding='utf-8') as f:
            speakings = json.load(f)
    else:
        return jsonify({'error': 'No data file'}), 404

    new_speakings = [item for item in speakings if item.get('id') != item_id]
    if len(new_speakings) == len(speakings):
        return jsonify({'error': 'Item not found'}), 404

    with open('speaking_describe_image.json', 'w', encoding='utf-8') as f:
        json.dump(new_speakings, f, ensure_ascii=False, indent=4)

    return jsonify({'message': 'Deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
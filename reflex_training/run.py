import time
import os
import json

# Define the path to ending_words.json
ENDING_WORDS_FILE = os.path.join(os.path.dirname(__file__), 'ending_words.json')

def save_ending_words(data):
    with open(ENDING_WORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

def update_timestamps():
    # Load current data
    data = load_ending_words()
    
    # Get current timestamp as base
    current_time = int(time.time())
    
    # Update sWords timestamps
    for i, word in enumerate(data["sWords"]):
        word["timestamp"] = current_time + i
        
    # Update edWords timestamps starting from where sWords left off
    start_time = current_time + len(data["sWords"])
    for i, word in enumerate(data["edWords"]):
        word["timestamp"] = start_time + i
    
    # Save updated data
    save_ending_words(data)
    return data

# Run this function once to update all timestamps
if __name__ == "__main__":
    update_timestamps()
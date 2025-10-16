# Reflex-Training-App

A web app for practicing number, year, and linked speech reflexes.

## Features

- Random Number Generator with customizable min/max
- Random Year Generator with customizable min/max
- Linked Speech Practice with editable word list and pronunciation guides
- Adjustable practice interval
- Word list management: add, delete, search
- Responsive UI with two-column layout

## Requirements

- Python 3.7+
- Flask

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/yourusername/Reflex-Training-App.git
    cd Reflex-Training-App
    ```

2. Install dependencies:
    ```sh
    pip install flask
    ```

## Usage

1. Run the app:
    ```sh
    cd reflex_training
    python app.py
    ```

2. Open your browser and go to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
Reflex-Training-App/
    reflex_training/
        app.py
        words.json
        static/
            script.js
            style.css
        templates/
            index.html
    README.md
    .gitignore
```

## Customization

- **Random Number/Year Range:**  
  Set min/max values in the UI before starting practice.

- **Practice Interval:**  
  Adjust "Thời gian mỗi lượt (giây)" and click "Cập nhật".

- **Linked Speech Practice:**  
  Add words/phrases in the input, manage the list on the right panel.

## Uploading Words or Sentences from Excel

You can quickly add multiple words or sentences by uploading an Excel file.

### How to Upload

1. Prepare an Excel file (`.xlsx` or `.xls`) with your words or sentences in the **first column**.
    - For words: Each row should contain a word or phrase.
    - For sentences: Each row should contain a sentence.
    - You may optionally add a header row (e.g., `word` or `sentence`), but it's not required.

2. On the web app, scroll down to the section **"Nhập câu từ file Excel:"**.

3. Click **"Chọn file"** and select your Excel file.

4. Click **"Tải lên"** to upload.  
   - The words or sentences will be added to the corresponding list.

> **Note:**  
> - On the main page, the upload will add words.  
> - On the "Sentence Practice" page, the upload will add sentences.  
> - On the "Repeat Sentence" page, the upload will add repeat sentences.

### File Format Example

| word/sentence         |
|-----------------------|
| get it                |
| need it               |
| pass it               |
| Books are heavy.      |
| Our professor is here |

Or, without a header:

|                       |
|-----------------------|
| get it                |
| need it               |
| pass it               |
| Books are heavy.      |
| Our professor is here |

Only the first column will be used.

## License

MIT License

<!-- 3vlaKhYY -->
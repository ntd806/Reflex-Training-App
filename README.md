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

## License

MIT License
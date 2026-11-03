# Book Price Comparing Scraper

A Python web scraper and Flask application that compares real-time book prices between two major Bangladeshi online bookstores: **Rokomari** and **Wafilife**.

## Features

- **Real-Time Price Comparison:** Fetches live book titles, authors, prices, and direct purchase links from both Rokomari and Wafilife.
- **Fast Concurrent Scraping:** Uses multi-threaded fetching (`ThreadPoolExecutor`) for fast response times.
- **Smart Bengali Text Matching:** Normalizes spelling variants and applies fuzzy similarity scoring to accurately match corresponding book editions across platforms.
- **Dual Interface:**
  - **Web Application:** Interactive Flask UI with search, responsive book cards, and direct buy buttons.
  - **CLI Mode:** Quick console search for terminal users.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gazi-faysal-jubayer/bookprise-comparing-scraper.git
   cd bookprise-comparing-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Web Application (Flask)
Run the Flask server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

### 2. Command Line Interface (CLI)
Search for a book directly in the terminal:
```bash
python main.py "প্যারাডক্সিক্যাল সাজিদ"
```
Or run interactively:
```bash
python main.py
```

## Docker Support

Build and run using Docker:
```bash
docker build -t bookprise-scraper .
docker run -p 5000:5000 bookprise-scraper
```

## License

This project is licensed under the terms of the MIT License.

# 📰 News Aggregator Pipeline

This is a Python-based news scraping pipeline that fetches the latest articles from **Skift** and **PhocusWire**, stores them in a local **SQLite** database and **CSV** file, and prints the top 5 most recent articles in a tabular format.

## 📦 Features

- Scrapes news articles from:
  - [Skift](https://skift.com)
  - [PhocusWire](https://www.phocuswire.com/Latest-News)
- Stores articles in:
  - `SQLite` database (`news.db`)
  - `CSV` file (`articles.csv`)
- Prints the **Top 5 combined latest articles** from Skift and Phocuswire
- Robust **logging system** with console and file logs

---

## 🛠️ Requirements

Make sure you have Python 3.7 or above installed.

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

**requirements.txt**
```txt
requests
beautifulsoup4
tabulate
lxml
```

---

## 🚀 How to Run

1. **Clone the repository (optional):**

```bash
git clone <your-repo-url>
cd <your-folder>
```

2. **Save the script** (e.g., `news_pipeline.py`) and run it using:

```bash
python news_pipeline.py
```

3. On success, you will see:

- A terminal table with the top 5 articles
- A `news.db` SQLite database with saved articles
- A `articles.csv` CSV file
- A `news_pipeline.log` log file

---

## 📂 File Structure

```bash
.
├── news_pipeline.py       # Main script
├── articles.csv           # Output CSV file
├── news.db                # SQLite database
├── news_pipeline.log      # Log file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 📋 Example Output

```text
+-------------------------------------------------------------------+------------+---------------------+------------------------------------------------------------------------------------------------+ 
| Title                                                             | Source     | Published At        | URL                                                                                            | 
+===================================================================+============+=====================+================================================================================================+ 
| Delta encouraged by early results of AI pricing with Fetcherr     | PhocusWire | 2025-07-19 16:35:51 | https://www.phocuswire.com/delta-fetcherr-ai-pricing-deployment                                | 
+-------------------------------------------------------------------+------------+---------------------+------------------------------------------------------------------------------------------------+ 
| Industry leaders on the future of digital identity and AI agents  | PhocusWire | 2025-07-19 16:35:51 | https://www.phocuswire.com/phocuswright-europe-2025-agents-digital-id-future-travel            | 
+-------------------------------------------------------------------+------------+---------------------+------------------------------------------------------------------------------------------------+ 
| State of Travel 2025                                              | Skift      | 2025-07-19 11:05:49 | https://skift.com/insights/state-of-travel/                                                    | 
+-------------------------------------------------------------------+------------+---------------------+------------------------------------------------------------------------------------------------+ 
| Why Jet2’s Jingle Became TikTok’s Surprise Summer Travel Meme     | Skift      | 2025-07-19 11:05:49 | https://skift.com/2025/07/17/why-jet2s-jingle-became-tiktoks-surprise-summer-travel-meme/      | 
+-------------------------------------------------------------------+------------+---------------------+------------------------------------------------------------------------------------------------+ 
| The New Athletic Class: How Lifestyle Sports Are Reshaping Travel | Skift      | 2025-07-19 11:05:49 | https://skift.com/2025/07/16/the-new-athletic-class-how-lifestyle-sports-are-reshaping-travel/ | 
+-------------------------------------------------------------------+------------+---------------------+------------------------------------------------------------------------------------------------+
```

---

## 🧹 Cleanup

To remove the generated files:

```bash
rm articles.csv news.db news_pipeline.log
```



## 👨‍💻 Author

**Kumar Priyanshu** – [GitHub](https://github.com/priyanshu5485), [LinkedIn](https://www.linkedin.com/in/priyanshu0309/)
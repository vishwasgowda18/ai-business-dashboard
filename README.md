# Conversational AI Business Dashboard

An AI-powered Business Intelligence dashboard that allows users to generate interactive data visualizations using natural language queries. The system leverages **Google Gemini AI** to interpret user questions and automatically create charts from uploaded datasets.

---

## Features

* Upload CSV datasets
* Ask questions in natural language
* AI-powered chart generation using Gemini
* Interactive data visualizations with Plotly
* Simple and intuitive dashboard interface

---

## Tech Stack

* **Python**
* **Streamlit**
* **Plotly**
* **Google Gemini AI**
* **Pandas**

---

## How It Works

1. Upload a CSV dataset.
2. Ask a business question in natural language.
3. Gemini AI interprets the query.
4. The system generates the appropriate visualization automatically.

---

## Example Queries

```
Show sales by region
Show sales trend over time
Which product has the highest sales
Show product sales distribution
```

---

## Project Structure

```
app.py
data.csv
requirements.txt
README.md
```

---

## Installation

Install required libraries:

```
pip install -r requirements.txt
```

Run the dashboard:

```
python -m streamlit run app.py
```

---

## Future Improvements

* Support for multiple datasets
* Advanced natural language query understanding
* Dynamic database integration
* Enhanced dashboard customization

---

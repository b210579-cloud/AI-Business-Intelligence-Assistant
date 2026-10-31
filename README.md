# AI Business Intelligence Assistant

A mini business intelligence application that answers questions about sales data using Python, SQLite, FastAPI, Streamlit, and an optional Gemini-powered agent.

## Features

- Loads sales transaction data from CSV.
- Cleans invalid records before storing data in SQLite.
- Calculates revenue as `Quantity * Unit_price - Discount_amount`.
- Answers questions about total revenue, highest-revenue product, highest-revenue region, monthly revenue, and revenue changes between two months.
- Provides a FastAPI backend, Streamlit interface, and automated API tests.
- Includes an optional Gemini agent endpoint (`/ask-ai`) that uses predefined sales-data tools.

## Project structure

```text
AI_Business_Intelligence_Assistant/
├── backend/
│   ├── main.py
│   └── agent.py
├── data/
│   ├── ai_bi_assistant_sales_data - GET.csv
│   └── cleaned_sales_data.csv
├── frontend/
│   └── app.py
├── tests/
│   └── test_api.py
├── clean_data.py
├── database.py
├── sales.db
├── requirements.txt
├── .gitignore
└── README.md
```

## Data processing

The cleaning script keeps completed transactions with a positive quantity, a valid positive unit price, and a valid non-negative discount amount.

Revenue formula:

`Revenue = Quantity * Unit_price - Discount_amount`

For the supplied dataset, 48 valid records remain after cleaning. The calculated total revenue is ₹1,439,200.

## Technology stack

- Python and Pandas
- SQLite
- FastAPI
- Streamlit
- Pytest
- Google Gemini API (optional AI agent)

## Setup

Run these commands from the project root in PowerShell:

```powershell
py -m pip install -r requirements.txt
py clean_data.py
py database.py
```

The cleaning and database commands regenerate the cleaned CSV and SQLite database from the source CSV.

## Run the application

Start the backend in one terminal:

```powershell
py -m uvicorn backend.main:app --reload
```

API base URL: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

Start the frontend in a second terminal:

```powershell
py -m streamlit run frontend/app.py
```

Streamlit usually opens at `http://localhost:8501`.

## API endpoints

### `GET /`

Returns the API status.

### `POST /ask`

Accepts a sales question and returns a structured answer using predefined SQL queries.

Example request:

```json
{
  "question": "Which region generated the highest sales?"
}
```

Example response:

```json
{
  "question": "Which region generated the highest sales?",
  "answer": "South region generated the highest sales: ₹411,200.00",
  "supporting_data": {
    "region": "South",
    "revenue": 411200
  }
}
```

### `POST /ask-ai`

Calls the optional Gemini-powered agent. It is designed to select from predefined data-retrieval tools instead of generating and executing arbitrary SQL.

To configure Gemini, create a `.env` file in the project root:

```text
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Replace the placeholder with your own key. Never share or commit the real `.env` file. The `.gitignore` file excludes `.env`.

**Runtime note:** The Gemini endpoint depends on external Gemini service availability and a valid API key. During development, requests to the selected model returned a temporary service-unavailable (503) response. The endpoint is included in the source code, but a successful live response was not confirmed during testing. The deterministic `/ask` endpoint was tested successfully.

## Safety and answer reliability

- The `/ask` endpoint uses predefined SQL statements and does not execute SQL supplied by the user.
- The Gemini agent is designed to call predefined sales-data tools rather than run arbitrary model-generated SQL.
- The agent's SQLite query connection enables `PRAGMA query_only = ON`.
- Unsupported questions receive a fallback response instead of an invented sales figure.
- Further validation and monitoring would be needed before production use.

## Automated tests

Run tests from the project root:

```powershell
py -m pytest -v
```

Development test result: **7 tests passed**. Tests cover supported sales questions, month comparison, an empty question, and an unsupported question.

## Architecture overview

1. **CSV input:** The original sales dataset is stored in the `data` folder.
2. **Data cleaning:** `clean_data.py` validates and filters records and creates the cleaned CSV.
3. **Database:** `database.py` loads cleaned records into `sales.db`.
4. **Backend:** FastAPI in `backend/main.py` receives questions and executes predefined SQL. The optional `backend/agent.py` connects Gemini to predefined sales-data tools.
5. **Frontend:** Streamlit in `frontend/app.py` provides a simple question-and-answer interface.
6. **Testing:** Pytest checks supported and unsupported API questions.

## Limitations and future improvements

- Expand natural-language question coverage and improve intent recognition.
- Confirm Gemini operation when the provider is available and add retry handling for temporary service errors.
- Add charts, filters, and date-range selection to the frontend.
- Add logging and deployment hardening before production use.

## AI assistance disclosure

AI assistance was used to help with Python, SQL, FastAPI, Streamlit, test writing, debugging, and documentation. The developer ran the application and tests and checked returned sales figures against the supplied dataset.

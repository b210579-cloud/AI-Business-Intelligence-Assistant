
import os
import sqlite3
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key securely from the project root .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = "gemini-3.8-flash"
DATABASE = PROJECT_ROOT / "sales.db"


def get_client():
    """Create the Gemini client only when the optional AI endpoint is used."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Create a .env file in the project root."
        )
    return genai.Client(api_key=api_key)


def run_query(query, parameters=()):
    """Run a read-only SQL query against the sales database."""
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA query_only = ON")

    try:
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        return cursor.fetchall()
    finally:
        connection.close()


# TOOL 1: Total revenue
def get_total_revenue():
    """Get the total revenue from all valid sales transactions."""
    rows = run_query("SELECT SUM(Revenue) FROM sales")
    return {"total_revenue": rows[0][0] or 0}


# TOOL 2: Highest revenue product
def get_top_product():
    """Find the product that generated the highest total revenue."""
    rows = run_query("""
        SELECT Product, SUM(Revenue) AS revenue
        FROM sales
        GROUP BY Product
        ORDER BY revenue DESC
        LIMIT 1
    """)
    return {"product": rows[0][0], "revenue": rows[0][1]}


# TOOL 3: Highest sales region
def get_top_region():
    """Find the region with the highest total sales revenue."""
    rows = run_query("""
        SELECT Region, SUM(Revenue) AS revenue
        FROM sales
        GROUP BY Region
        ORDER BY revenue DESC
        LIMIT 1
    """)
    return {"region": rows[0][0], "revenue": rows[0][1]}


# TOOL 4: Monthly revenue
def get_monthly_revenue():
    """Get revenue totals for every month in the sales dataset."""
    rows = run_query("""
        SELECT SUBSTR(Order_date, 4, 2), SUM(Revenue)
        FROM sales
        GROUP BY SUBSTR(Order_date, 4, 2)
        ORDER BY SUBSTR(Order_date, 4, 2)
    """)

    months = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June"
    }

    return {
        "monthly_revenue": [
            {
                "month": months.get(row[0], row[0]),
                "revenue": row[1]
            }
            for row in rows
        ]
    }


# TOOL 5: Compare two months
def compare_months(first_month: str, second_month: str):
    """Compare revenue between two months by their full month names."""
    months = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06"
    }

    first = first_month.strip().lower()
    second = second_month.strip().lower()

    if first not in months or second not in months:
        return {"error": "Please provide month names from January to June."}

    rows = run_query("""
        SELECT
            SUM(CASE WHEN SUBSTR(Order_date, 4, 2) = ?
                THEN Revenue ELSE 0 END),
            SUM(CASE WHEN SUBSTR(Order_date, 4, 2) = ?
                THEN Revenue ELSE 0 END)
        FROM sales
    """, (months[first], months[second]))

    first_revenue = rows[0][0] or 0
    second_revenue = rows[0][1] or 0
    difference = second_revenue - first_revenue

    percentage = (
        difference / first_revenue * 100
        if first_revenue else None
    )

    return {
        "first_month": first.title(),
        "first_month_revenue": first_revenue,
        "second_month": second.title(),
        "second_month_revenue": second_revenue,
        "revenue_change": difference,
        "percentage_change": percentage
    }


# AI AGENT: Gemini selects and calls the appropriate Python tools
def ask_sales_agent(question: str):
    """Understand a sales question, call database tools, and explain results."""

    client = get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction="""
            You are an AI Business Intelligence Assistant.

            You answer questions only about the sales dataset.

            You have five Python tools:
            1. get_total_revenue
            2. get_top_product
            3. get_top_region
            4. get_monthly_revenue
            5. compare_months

            For every question about sales data, call the relevant tool.
            For questions requiring multiple facts, you may call multiple tools.

            Use only the results returned by the tools.
            Never invent revenue figures or database facts.
            Explain numerical results clearly in Indian Rupees (₹).
            If the question is unrelated to the sales dataset or cannot
            be answered using the available tools, politely say so.
            Do not generate or execute SQL yourself.
            """
            ,
            tools=[
                get_total_revenue,
                get_top_product,
                get_top_region,
                get_monthly_revenue,
                compare_months
            ]
        )
    )

    if not response.text:
        return "I could not generate an answer. Please try again."

    return response.text


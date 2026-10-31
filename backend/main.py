

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from .agent import ask_sales_agent

app = FastAPI(
    title="AI Business Intelligence Assistant",
    description="Ask questions about sales data",
    version="1.0"
)


# Database connection function
def get_connection():
    return sqlite3.connect("sales.db")


# Request format
class QuestionRequest(BaseModel):
    question: str


# Home API
@app.get("/")
def home():
    return {
        "message": "Welcome to AI Business Intelligence Assistant",
        "status": "Running"
    }


# Question API
@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.lower().strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # 1. Total revenue
        if "total revenue" in question:

            cursor.execute("""
                SELECT SUM(Revenue)
                FROM sales
            """)

            result = cursor.fetchone()[0]

            return {
                "question": request.question,
                "answer": f"Total revenue is ₹{result:,.2f}",
                "supporting_data": {
                    "total_revenue": result
                }
            }

        # 2. Highest revenue product
        elif "product" in question and (
            "highest" in question or "top" in question
        ):

            cursor.execute("""
                SELECT Product, SUM(Revenue) AS total_revenue
                FROM sales
                GROUP BY Product
                ORDER BY total_revenue DESC
                LIMIT 1
            """)

            result = cursor.fetchone()

            return {
                "question": request.question,
                "answer": (
                    f"{result[0]} generated the highest "
                    f"revenue: ₹{result[1]:,.2f}"
                ),
                "supporting_data": {
                    "product": result[0],
                    "revenue": result[1]
                }
            }

        # 3. Highest sales region - corrected query
        elif "region" in question and (
            "highest" in question or "top" in question
        ):

            cursor.execute("""
                SELECT
                    MIN(TRIM(Region)) AS region,
                    SUM(Revenue) AS total_revenue
                FROM sales
                WHERE Region IS NOT NULL
                  AND TRIM(Region) <> ''
                GROUP BY LOWER(TRIM(Region))
                ORDER BY total_revenue DESC
                LIMIT 1
            """)

            result = cursor.fetchone()

            if result is None:
                return {
                    "question": request.question,
                    "answer": "No valid region data found.",
                    "supporting_data": None
                }

            return {
                "question": request.question,
                "answer": (
                    f"{result[0]} region generated the "
                    f"highest sales: ₹{result[1]:,.2f}"
                ),
                "supporting_data": {
                    "region": result[0],
                    "revenue": result[1]
                }
            }

        # 4. Revenue change between two months
        elif "change" in question and "between" in question:

            month_numbers = {
                "january": "01",
                "february": "02",
                "march": "03",
                "april": "04",
                "may": "05",
                "june": "06"
            }

            selected_months = [
                month for month in month_numbers
                if month in question
            ]

            if len(selected_months) != 2:
                return {
                    "question": request.question,
                    "answer": "Please mention two months.",
                    "supporting_data": None
                }

            first_month, second_month = selected_months

            cursor.execute("""
                SELECT
                    SUM(
                        CASE WHEN SUBSTR(Order_date, 4, 2) = ?
                        THEN Revenue ELSE 0 END
                    ),
                    SUM(
                        CASE WHEN SUBSTR(Order_date, 4, 2) = ?
                        THEN Revenue ELSE 0 END
                    )
                FROM sales
            """, (
                month_numbers[first_month],
                month_numbers[second_month]
            ))

            first_revenue, second_revenue = cursor.fetchone()

            first_revenue = first_revenue or 0
            second_revenue = second_revenue or 0

            difference = second_revenue - first_revenue

            percentage = (
                difference / first_revenue * 100
                if first_revenue else None
            )

            return {
                "question": request.question,
                "answer": (
                    f"Revenue changed by ₹{difference:,.2f} "
                    f"from {first_month.title()} "
                    f"to {second_month.title()}."
                ),
                "supporting_data": {
                    "first_month_revenue": first_revenue,
                    "second_month_revenue": second_revenue,
                    "revenue_change": difference,
                    "percentage_change": percentage
                }
            }

        # 5. Monthly revenue trend
        elif "monthly" in question or "month" in question:

            cursor.execute("""
                SELECT
                    SUBSTR(Order_date, 4, 2),
                    SUM(Revenue)
                FROM sales
                GROUP BY SUBSTR(Order_date, 4, 2)
                ORDER BY SUBSTR(Order_date, 4, 2)
            """)

            rows = cursor.fetchall()

            months = {
                "01": "January",
                "02": "February",
                "03": "March",
                "04": "April",
                "05": "May",
                "06": "June"
            }

            data = [
                {
                    "month": months.get(row[0], row[0]),
                    "revenue": row[1]
                }
                for row in rows
            ]

            return {
                "question": request.question,
                "answer": "Monthly revenue calculated successfully.",
                "supporting_data": data
            }

        # 6. Unsupported question
        else:
            return {
                "question": request.question,
                "answer": "Sorry, I cannot answer this question yet.",
                "supporting_data": None
            }

    except sqlite3.Error as error:

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(error)}"
        )

    finally:
        connection.close()


# Gemini AI Agent API
@app.post("/ask-ai")
def ask_ai_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        answer = ask_sales_agent(question)

        return {
            "question": question,
            "answer": answer,
            "mode": "Gemini LLM with Agentic Tool Calling"
        }

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(error)}"
        )


import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="AI Business Intelligence Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Business Intelligence Assistant")
st.write("Ask questions about your sales data and get instant insights.")

st.divider()

st.subheader("Ask a Business Question")

question = st.text_input(
    "Enter your question:",
    placeholder="Example: What is the total revenue?"
)

if st.button("Get Insights"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            response = requests.post(
                API_URL,
                json={"question": question},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                st.success("Answer generated successfully!")
                st.subheader("Answer")
                st.write(result["answer"])

                st.subheader("Supporting Data")
                data = result.get("supporting_data")

                if isinstance(data, list):
                    st.dataframe(pd.DataFrame(data))
                elif isinstance(data, dict):
                    st.json(data)
                else:
                    st.info("No supporting data available.")

            else:
                st.error(f"API Error: {response.text}")

        except requests.exceptions.RequestException:
            st.error("Could not connect to the backend. Make sure it is running.")

st.divider()

st.subheader("Try Sample Questions")

questions = [
    "What is the total revenue?",
    "Which product generated the highest revenue?",
    "Which region has the highest sales?",
    "Show me the monthly revenue trend."
]

for item in questions:
    st.write("•", item)

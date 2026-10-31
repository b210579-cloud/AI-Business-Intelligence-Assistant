
import sqlite3
import pandas as pd

# Read the cleaned sales data
df = pd.read_csv("data/cleaned_sales_data.csv")

# Create or connect to SQLite database
connection = sqlite3.connect("sales.db")

# Store the data in a database table
df.to_sql(
    "sales",
    connection,
    if_exists="replace",
    index=False
)

print("Database created successfully!")

# Check the number of records
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM sales")

count = cursor.fetchone()[0]

print("Records stored in database:", count)

# Calculate total revenue using SQL
cursor.execute("SELECT SUM(Revenue) FROM sales")

revenue = cursor.fetchone()[0]

print("Total revenue:", revenue)

# Close database connection
connection.close()

print("Database connection closed.")


import sqlite3

# Connect to database
connection = sqlite3.connect("sales.db")

cursor = connection.cursor()

# Question 1: Total revenue
cursor.execute("SELECT SUM(Revenue) FROM sales")
print("Total Revenue:", cursor.fetchone()[0])

# Question 2: Highest revenue product
cursor.execute("""
SELECT Product, SUM(Revenue) AS total_revenue
FROM sales
GROUP BY Product
ORDER BY total_revenue DESC
LIMIT 1
""")

print("Highest Revenue Product:", cursor.fetchone())

# Question 3: Highest sales region
cursor.execute("""
SELECT Region, SUM(Revenue) AS total_revenue
FROM sales
GROUP BY Region
ORDER BY total_revenue DESC
LIMIT 1
""")

print("Highest Sales Region:", cursor.fetchone())

# Question 4: Monthly revenue
cursor.execute("""
SELECT
    SUBSTR(Order_date, 4, 2) AS month,
    SUM(Revenue)
FROM sales
GROUP BY month
ORDER BY month
""")

print("\nMonthly Revenue:")

for row in cursor.fetchall():
    print(row)

connection.close()


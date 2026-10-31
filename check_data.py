
import csv

file_path = "data/ai_bi_assistant_sales_data - GET.csv"

with open(file_path, "r", newline="", encoding="utf-8-sig") as file:

    reader = csv.DictReader(file)

    print("COLUMN NAMES:")
    print(reader.fieldnames)

    rows = list(reader)

    print("\nTOTAL TRANSACTIONS:")
    print(len(rows))

    print("\nFIRST 5 TRANSACTIONS:")

    for row in rows[:5]:
        print(row)

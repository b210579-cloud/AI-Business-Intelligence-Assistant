
import pandas as pd

# Read the sales CSV file
file_path = "data/ai_bi_assistant_sales_data - GET.csv"

df = pd.read_csv(file_path)

# Display original dataset information
print("ORIGINAL DATA")
print("Total records:", len(df))

# Convert numeric columns into proper numeric values
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["Unit_price"] = pd.to_numeric(df["Unit_price"], errors="coerce")
df["Discount_amount"] = pd.to_numeric(
    df["Discount_amount"], errors="coerce"
)

# Identify missing values
print("\nMISSING VALUES")
print(df.isnull().sum())

# Keep completed transactions
completed = df[df["Status"] == "Completed"].copy()

# Remove records with invalid quantity or unit price
valid = completed[
    (completed["Quantity"] > 0) &
    (completed["Unit_price"].notna()) &
    (completed["Unit_price"] > 0) &
    (completed["Discount_amount"].notna()) &
    (completed["Discount_amount"] >= 0)
].copy()

# Calculate revenue
valid["Revenue"] = (
    valid["Quantity"] * valid["Unit_price"]
    - valid["Discount_amount"]
)

print("\nCLEANED DATA")
print("Valid completed transactions:", len(valid))

print("\nTOTAL REVENUE:")
print(valid["Revenue"].sum())

print("\nEXCLUDED TRANSACTIONS:")
print(df[~df["Transaction_Id"].isin(valid["Transaction_Id"])])

# Save cleaned data
valid.to_csv("data/cleaned_sales_data.csv", index=False)

print("\nCleaned data saved successfully!")

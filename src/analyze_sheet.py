import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe

# Step 1: Connect using your service account key
gc = gspread.service_account(filename="resources/cupidmatch-6c7f5607c727.json")  # Update the path if needed

# Step 2: Open the Google Sheet by URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1yQpwRSWJ2IgTs2BiMVicmp7W4qLLVsAZ9OI0dQBD7CQ/edit?usp=sharing"
spreadsheet = gc.open_by_url(spreadsheet_url)

# Step 3: View worksheet titles (optional)
print("Available worksheets:")
for ws in spreadsheet.worksheets():
    print(f"- {ws.title}")

# Step 4: Select the first worksheet (or pick by name)
worksheet = spreadsheet.get_worksheet(0)  # or spreadsheet.worksheet("Sheet1")

# Step 5: Convert to DataFrame
df = get_as_dataframe(worksheet, evaluate_formulas=True)

# Clean up: Drop empty rows/cols
df.dropna(how="all", axis=0, inplace=True)
df.dropna(how="all", axis=1, inplace=True)

# Step 6: Output preview & basic stats
print("\nData Preview:")
print(df.head())

print("\nSummary Statistics:")
print(df.describe(include='all'))

# Optional: Save to CSV
df.to_csv("data/sheet_data.csv", index=False)

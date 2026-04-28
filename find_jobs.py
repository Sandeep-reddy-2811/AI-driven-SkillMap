import pandas as pd

occ_df = pd.read_excel("Occupation Data.xlsx")

# Search for each missing job
keywords = [
    "Data Scien",
    "Network",
    "Financial",
    "Warehouse",
    "Logistic",
    "Production"
]

for keyword in keywords:
    matches = occ_df[occ_df["Title"].str.contains(keyword, case=False, na=False)]
    print(f"\n--- '{keyword}' matches ---")
    print(matches["Title"].tolist())

# Debug exact match
skills_df = pd.read_excel("Skills.xlsx")
skills_df = skills_df[skills_df["Scale ID"] == "LV"]

print("\n--- Exact search for Data Scientists ---")
match = skills_df[skills_df["Title"].str.contains("Data Scientist", case=False, na=False)]
print(match["Title"].unique())

print("\n--- Exact search for Financial ---")
match = skills_df[skills_df["Title"].str.contains("Financial and Investment", case=False, na=False)]
print(match["Title"].unique())
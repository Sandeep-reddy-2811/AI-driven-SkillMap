import pandas as pd

# ---- Peek at Skills.xlsx ----
print("=" * 50)
print("SKILLS.xlsx - First 5 rows")
print("=" * 50)
skills_df = pd.read_excel("Skills.xlsx")
print(skills_df.head())
print("\nColumn names:")
print(skills_df.columns.tolist())
print(f"\nTotal rows: {len(skills_df)}")

# ---- Peek at Occupation Data.xlsx ----
print("\n" + "=" * 50)
print("OCCUPATION DATA.xlsx - First 5 rows")
print("=" * 50)
occ_df = pd.read_excel("Occupation Data.xlsx")
print(occ_df.head())
print("\nColumn names:")
print(occ_df.columns.tolist())
print(f"\nTotal rows: {len(occ_df)}")
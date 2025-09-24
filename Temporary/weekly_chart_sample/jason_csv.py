import os
import json
import pandas as pd
from pathlib import Path

# -------------------------------
# CONFIG
# -------------------------------
INPUT_FOLDER = Path("./weekly_diet_batch")  # folder containing diet1.json ... diet30.json
OUTPUT_CSV = Path("combined_weekly_diets.csv")

# -------------------------------
# COLLECT ALL JSON FILES
# -------------------------------
json_files = sorted(INPUT_FOLDER.glob("diet*.json"))

all_rows = []

for file in json_files:
    with open(file, "r") as f:
        data = json.load(f)
    
    user_info = data.get("user_info", {})
    weekly_diet = data.get("weekly_diet_plan", {})

    # Flatten weekly diet
    flat_diet = {}
    for day, meals in weekly_diet.items():
        date = meals.pop("Date", "")
        for meal, items in meals.items():
            col_name = f"{day}_{meal}"  # e.g., Monday_Breakfast
            flat_diet[col_name] = items

    # Combine user info and flattened diet
    row = {**user_info, **flat_diet}
    all_rows.append(row)

# -------------------------------
# SAVE TO CSV
# -------------------------------
df = pd.DataFrame(all_rows)
df.to_csv(OUTPUT_CSV, index=False)
print(f"All {len(json_files)} weekly diets saved into CSV: {OUTPUT_CSV.resolve()}")

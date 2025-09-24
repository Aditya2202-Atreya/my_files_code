import json
import csv
from pathlib import Path

OUTPUT_FOLDER = Path("./diet_results")
OUTPUT_FOLDER.mkdir(exist_ok=True)  # Ensure folder exists

def merge_json_to_csv(folder_path, output_csv_path):
    """Merge all JSON files in a folder into a single CSV."""
    all_rows = []

    for json_file in folder_path.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        user_info = data.get('user_info', {})
        diet_data = data.get('diet_chart', {}).get('Diet', {})

        # Filter Non-veg for Veg/Vegan users
        diet_habit = user_info.get('Diet_habit', '').lower()
        if diet_habit in ['veg', 'vegan'] and 'Non-veg' in diet_data:
            del diet_data['Non-veg']

        for category, items in diet_data.items():
            row = {
                "User": user_info.get('Location', 'Unknown'),  # you can change to name or age
                "Age": user_info.get('age', ''),
                "Gender": user_info.get('gender', ''),
                "BMI": user_info.get('BMI', ''),
                "BMI_Category": user_info.get('BMI_Category', ''),
                "Category": category,
                "Do": items.get("Do", ""),
                "Dont": items.get("Dont", "")
            }
            all_rows.append(row)

    # Write all rows to a single CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["User", "Age", "Gender", "BMI", "BMI_Category", "Category", "Do", "Dont"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"All JSON files merged into: {output_csv_path}")


# --- Usage ---
output_csv_file = OUTPUT_FOLDER / "merged_diet_chart.csv"
merge_json_to_csv(OUTPUT_FOLDER, output_csv_file)

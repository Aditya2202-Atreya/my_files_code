import json
import csv
from pathlib import Path

OUTPUT_FOLDER = Path("./diet_results")
OUTPUT_FOLDER.mkdir(exist_ok=True)

def flatten_json(y, parent_key='', sep='_'):
    """
    Flatten a nested JSON/dictionary.
    Nested keys are joined by sep.
    Lists are converted to comma-separated strings.
    """
    items = []
    if isinstance(y, dict):
        for k, v in y.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep=sep).items())
    elif isinstance(y, list):
        items.append((parent_key, ', '.join(map(str, y))))
    else:
        items.append((parent_key, y))
    return dict(items)

def merge_json_to_csv_generic(folder_path, output_csv_path):
    """
    Merge all JSON files in a folder into a single CSV.
    Works for any JSON structure by flattening keys.
    """
    all_rows = []

    for json_file in folder_path.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        flat_data = flatten_json(data)
        all_rows.append(flat_data)

    # Get all unique keys from all rows to form CSV headers
    fieldnames = set()
    for row in all_rows:
        fieldnames.update(row.keys())
    fieldnames = sorted(fieldnames)  # optional: sort columns alphabetically

    # Write merged CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print(f"All JSON files merged into: {output_csv_path}")


# --- Usage ---
output_csv_file ="merged_generic.csv"
merge_json_to_csv_generic(OUTPUT_FOLDER, output_csv_file)

import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from tqdm import tqdm
from weekly_chart import generate_weekly_diet  # your previous function

# -------------------------------
# BATCH SETTINGS
# -------------------------------
NUM_RESPONSES = 30
MAX_WORKERS = 5  # 5 tasks in parallel
OUTPUT_FOLDER = Path("./weekly_diet_batch")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# -------------------------------
# RANDOM USER DATA GENERATOR
# -------------------------------
import random

def random_user(i):
    locations = [
        "Mumbai, India", "Delhi, India", "Amritsar, India", "Kolkata, India",
        "Chennai, India", "Beijing, China", "Tokyo, Japan", "Berlin, Germany",
        "Pune, India", "Nagpur, India", "Patna, India", "Seoul, South Korea",
        "Cape Town, South Africa", "Shanghai, China", "Bangkok, Thailand",
        "Sydney, Australia", "London, UK", "New York, USA"
    ]
    return {
        "Prakruti": random.choice(["Vata", "Pitta", "Kapha", "Vata-Pitta", "Pitta-Kapha"]),
        "height": random.randint(150, 190),
        "weight": random.randint(50, 90),
        "age": random.randint(20, 65),
        "gender": random.choice(["male", "female"]),
        "Diet_habit": random.choice(["Veg", "Non-Veg"]),
        "Health_condition": random.choice(["Normal", "Diabetes", "Hypertension"]),
        "Location": random.choice(locations),
        "Times_you_eat": random.randint(3,5),
        "Start_Date": (datetime.today() + timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")
    }

# -------------------------------
# WORKER FUNCTION
# -------------------------------
def generate_and_save(index):
    user_info = random_user(index)
    weekly_diet = generate_weekly_diet(user_info)  # call your existing function
    output_file = OUTPUT_FOLDER / f"diet{index+1}.json"
    data_to_save = {
        "user_info": user_info,
        "weekly_diet_plan": weekly_diet
    }
    with open(output_file, "w") as f:
        json.dump(data_to_save, f, indent=4)
    return f"diet{index+1}.json saved"

# -------------------------------
# RUN IN PARALLEL WITH PROGRESS BAR
# -------------------------------
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(generate_and_save, i) for i in range(NUM_RESPONSES)]
    
    for future in tqdm(as_completed(futures), total=NUM_RESPONSES, desc="Generating diets"):
        print(future.result())

print(f"\nAll {NUM_RESPONSES} weekly diet responses saved in {OUTPUT_FOLDER.resolve()}")

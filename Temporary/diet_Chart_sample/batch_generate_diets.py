import json
import random
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from Dietchart import generate_diet_chart

NUM_USERS = 30          
MAX_WORKERS = 5          
OUTPUT_FOLDER = Path("./diet_results")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# RANDOMIZATION HELPERS
def random_height(): return random.randint(150, 190)
def random_weight(): return random.randint(45, 90)
def random_age(): return random.randint(18, 70)
def random_gender(): return random.choice(["male", "female"])
def random_diet_habit(): return random.choice(["Veg", "Non-Veg", "Vegan"])
def random_health_condition(): return random.choice(["Diabetes", "Hypertension", "None"])
def random_location(): return random.choice([
        "Mumbai, India", "Delhi, India", "Amritsar, India", "Kolkata, India", "Chennai, India",
        "Beijing, China", "Tokyo, Japan", "Berlin, Germany",
        "New York, USA", "London, UK", "Sydney, Australia", "Toronto, Canada",
        "Paris, France", "Cape Town, South Africa", "Seoul, South Korea",
        "Singapore, Singapore", "Dubai, UAE", "Bangkok, Thailand"
    ])
def random_times_to_eat(): return str(random.randint(2, 5))
def random_prakruti(): return random.choice(["Vata", "Pitta", "Kapha", "Vata Pitta"])

# -------------------------------
# GENERATE USER PROFILES
# -------------------------------
user_profiles = [
    {
        "Prakruti": random_prakruti(),
        "height": random_height(),
        "weight": random_weight(),
        "age": random_age(),
        "gender": random_gender(),
        "Diet_habit": random_diet_habit(),
        "Health_condition": random_health_condition(),
        "Location": random_location(),
        "Times_you_eat": random_times_to_eat()
    }
    for _ in range(NUM_USERS)
]

# -------------------------------
# FUNCTION TO PROCESS SINGLE USER
# -------------------------------
def process_user(idx_user_tuple):
    idx, user_info = idx_user_tuple
    try:
        diet_chart = generate_diet_chart(user_info)
        result = {
            "user_info": user_info,
            "diet_chart": diet_chart
        }
        # Save individual JSON file
        file_path = OUTPUT_FOLDER / f"diet{idx+1}.json"
        with open(file_path, "w") as f:
            json.dump(result, f, indent=4)
        return True, idx+1
    except Exception as e:
        return False, f"User {idx+1} error: {e}"

# BATCH PARALLEL PROCESSING
results = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(process_user, item): item[0] for item in enumerate(user_profiles)}
    
    for future in tqdm(as_completed(futures), total=len(futures), desc="Generating diet charts"):
        success, info = future.result()
        results.append((success, info))
        if not success:
            print(info)

print(f"\n✅ Parallel batch generation completed! Results saved in '{OUTPUT_FOLDER.resolve()}'")

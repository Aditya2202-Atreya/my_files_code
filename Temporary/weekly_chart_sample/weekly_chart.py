import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import google.generativeai as genai

# -------------------------------
# CONFIGURE GEMINI API
# -------------------------------
env_path = Path(".env")
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("Missing API_KEY. Set it in environment or .env file.")

genai.configure(api_key=API_KEY)

# -------------------------------
# BMI CALCULATION FUNCTIONS
# -------------------------------
def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# -------------------------------
# WEEKLY DIET GENERATOR FUNCTION
# -------------------------------
def generate_weekly_diet(user_info):
    """
    Generates a weekly diet plan based on user info and sends prompt to Gemini API.
    Returns the filled weekly diet as a dictionary.
    """
    # -------------------------------
    # CALCULATE BMI
    # -------------------------------
    user_info['BMI'] = calculate_bmi(user_info['height'], user_info['weight'])
    user_info['BMI_Category'] = bmi_category(user_info['BMI'])

    # -------------------------------
    # CREATE WEEKLY TEMPLATE BASED ON TIMES YOU EAT
    # -------------------------------
    meal_keys = ["Early_Morning", "Breakfast", "Lunch", "Snacks", "Dinner"]
    selected_meals = meal_keys[:user_info.get("Times_you_eat", 3)]  # default 3

    start_date = datetime.strptime(user_info["Start_Date"], "%Y-%m-%d")
    weekly_diet_template = {}
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%A")
        date_str = current_date.strftime("%Y-%m-%d")
        weekly_diet_template[day_name] = {
            "Date": date_str,
            **{meal: "" for meal in selected_meals}
        }

    # -------------------------------
    # BUILD PROMPT FOR GEMINI
    # -------------------------------
    user_info_str = json.dumps(user_info, indent=4)
    weekly_template_str = json.dumps(weekly_diet_template, indent=4)

    prompt = f"""
You are an expert Ayurvedic nutritionist.

Based on the following user information:
{user_info_str}

And the following weekly diet template (including actual dates and correct day names):
{weekly_template_str}

Instructions for diet generation:

1. Fill each meal (Early_Morning, Breakfast, Lunch, Snacks, Dinner) with 4-6 practical food/diet items.  
2. Make the suggestions Ayurvedic, healthy, and suitable for the user's Prakruti, BMI, health condition, and age.  
3. Include **local dishes or ingredients** from the user's location for at least **50% of the items**.  
   For example, if the user is in Mumbai, include local Maharashtrian dishes or commonly available ingredients.  
4. Keep the rest of the items general healthy options compatible with Ayurvedic principles.  
5. Return the response strictly in only JSON format matching the template exactly, **without changing keys**.  
6. Keep responses concise and practical.
"""

    # -------------------------------
    # CALL GEMINI
    # -------------------------------
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:
        weekly_diet_filled = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Gemini did not return valid JSON. Response was:\n" + text)

    return weekly_diet_filled

# -------------------------------
# FOR TESTING PURPOSE
# -------------------------------
if __name__ == "__main__":
    # Example user
    user_info = {
        "Prakruti": "Vata Pitta",
        "height": 167,
        "weight": 72,
        "age": 45,
        "gender": "female",
        "Diet_habit": "Veg",
        "Health_condition": "Diabetes",
        "Location": "Mumbai, India",
        "Times_you_eat": 3,
        "Start_Date": "2025-09-24"
    }

    diet_plan = generate_weekly_diet(user_info)
    print("\n--- USER INFO ---")
    print(json.dumps(user_info, indent=4))
    print("\n--- FILLED WEEKLY DIET ---")
    print(json.dumps(diet_plan, indent=4))

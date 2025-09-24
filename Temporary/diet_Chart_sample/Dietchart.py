import os
import json
import google.generativeai as genai
from pathlib import Path

# Load environment (from .env or direct API key)
env_path = Path(".env")
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("Missing API_KEY. Set it in environment or .env file.")

genai.configure(api_key=API_KEY)

# BMI helper
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

# Define function to generate diet chart 
def generate_diet_chart(user_info):
    # Compute BMI + category
    bmi = calculate_bmi(user_info['height'], user_info['weight'])
    user_info['BMI'] = bmi
    user_info['BMI_Category'] = bmi_category(bmi)

    # print("Final user input created")
    # print(json.dumps(user_info, indent=4))

    # Dynamically build user info string for prompt
    user_info_str = "\n".join([f"{k}: {v}" for k, v in user_info.items()])

    prompt = f"""
    You are an Ayurvedic nutrition expert.
    Based on the following user info:

    {user_info_str}
    generate 4 to 6 food or diet in applicable each category and recommend amount also.
    Generate a JSON object in this exact format:

    "Diet": {{
        "Grain": {{"Do": "", "Dont": ""}},
        "Legume": {{"Do": "", "Dont": ""}},
        "Veg": {{"Do": "", "Dont": ""}},
        "Spices": {{"Do": "", "Dont": ""}},
        "Leafy veg": {{"Do": "", "Dont": ""}},
        "Oil": {{"Do": "", "Dont": ""}},
        "Fruits": {{"Do": "", "Dont": ""}},
        "Nuts and Dry fruits": {{"Do": "", "Dont": ""}},
        "Milk product": {{"Do": "", "Dont": ""}},
        "Non-veg": {{"Do": "", "Dont": ""}},
        "Condiments": {{"Do": "", "Dont": ""}}
    }}

    Keep the responses concise and practical.
    """

    # print("Prompt sent to Gemini:")
    # print(prompt)

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)

    # print("Raw Gemini Response:")
    # print(response.text)

    # Clean response to ensure JSON
    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    # print("Cleaned Text")
    # print(text)

    try:
        diet_json = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Gemini did not return valid JSON. Response was:\n" + text)
    
    # --- Filter non-veg for Veg or Vegan users ---
    if user_info['Diet_habit'].lower() in ['veg']:
        if 'Diet' in diet_json and 'Non-veg' in diet_json['Diet']:
            del diet_json['Diet']['Non-veg']

    print("Final Parsed JSON:")
    print(json.dumps(diet_json, indent=4))

    return diet_json


# usage
if __name__ == "__main__":
    user_info = {
        'Prakruti': 'Vata pitta',
        'height': 167,
        'weight': 72,
        'age': 45,
        'gender': 'female',
        'Diet_habit': 'Non Veg',
        'Health_condition': 'Diabetes',
        'Location': 'Tokyo, Japan',
        'Times_you_eat': '3'
    }

    diet_chart = generate_diet_chart(user_info)

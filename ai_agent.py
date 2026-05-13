import os
import json
import re
from google.genai import Client # Ensure: pip install google-genai
from dotenv import load_dotenv

load_dotenv()

# Simplified initialization
client = Client(api_key=os.getenv("API_KEY"))

def get_clean_json_task(text: str):
    prompt = f"""
    Extract task details and return ONLY a JSON object.
    Text: "{text}"
    Required format:
    {{
        "title": "Short title",
        "description": "Brief details",
        "deadline": "YYYY-MM-DD",
        "priority": "High/Medium/Low",
        "status": "Pending"
    }}
    If no deadline, use '2026-05-15'.
    """
    
    # List of models to try in order of availability in 2026
    models_to_try = ["gemini-3-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt
            )
            
            raw_content = response.text
            # Regex to clean markdown
            pattern = r"""```(?:json)?\s*(.*?)\s*
```"""
            match = re.search(pattern, raw_content, re.DOTALL)
            clean_json_str = match.group(1) if match else raw_content.strip()
            
            return json.loads(clean_json_str)
            
        except Exception as e:
            if "404" in str(e):
                print(f"Skipping {model_name}: Not found.")
                continue # Try the next model in the list
            print(f"AI Error: {e}")
            return None
            
    print("All models failed. Please check your API key permissions in Google AI Studio.")
    return None
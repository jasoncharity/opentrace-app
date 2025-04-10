import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HIBP_API_KEY")

def check_breaches(email):
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": API_KEY,
        "user-agent": "OpenTracePrototype"
    }
    params = {
        "truncateResponse": False
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 404:
        return []  # No breaches
    elif response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} — {response.text}")
        return None

def save_breach_results(breaches, filename="output_hibp.json"):
    with open(filename, "w") as f:
        json.dump(breaches, f, indent=2)

if __name__ == "__main__":
    # Replace with subject's known or test email
    subject_email = "jasonderby@mac.com"
    breaches = check_breaches(subject_email)

    if breaches is not None:
        print(f"Found {len(breaches)} breaches for {subject_email}")
        for b in breaches:
            print(f"- {b['Name']} ({b['BreachDate']}): {b['Description'][:100]}...")
        save_breach_results(breaches)
    else:
        print("No results or error occurred.")
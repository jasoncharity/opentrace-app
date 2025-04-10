import os
import json
import requests
from dotenv import load_dotenv

# === Load API keys ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

# === Load subject data ===
def load_subject(filename="subject.json"):
    with open(filename, "r") as f:
        return json.load(f)

# === Search Google Programmable Search ===
def search_google_multiple(subject_profile, num_results=5):
    base_url = "https://www.googleapis.com/customsearch/v1"

    # Build queries using name, aliases, affiliations + location
    queries = [subject_profile["name"]] \
            + subject_profile.get("aliases", []) \
            + subject_profile.get("affiliations", [])
    location = subject_profile.get("location", "")
    all_results = []

    for q in queries:
        full_query = f"{q} {location} site:twitter.com".strip()

        params = {
            "key": API_KEY,
            "cx": CSE_ID,
            "q": full_query,
            "num": num_results
        }

        print(f"🔍 Searching Google for: '{full_query}'")
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            results = response.json().get("items", [])
            print(f"  → Found {len(results)} results for: '{full_query}'")
            all_results.extend(results)
        else:
            print(f"⚠️ Google API error {response.status_code}: {response.text}")

    return all_results

# === Main execution ===
if __name__ == "__main__":
    subject = load_subject()
    results = search_google_multiple(subject)

    print(f"\n✅ Total Google results retrieved: {len(results)}")

    for r in results:
        print(f"- {r['title']} ({r['link']})")
        print(f"  {r.get('snippet', '')}\n")

    with open("output_google.json", "w") as f:
        json.dump(results, f, indent=2)

    print("📝 Saved Google results to output_google.json")
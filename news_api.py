import os
import requests
import json
from dotenv import load_dotenv

# === Load .env and API key ===
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

# === Load subject from JSON ===
def load_subject(filename="subject.json"):
    with open(filename, "r") as f:
        return json.load(f)

# === Search NewsAPI using name, aliases, affiliations + location ===
def search_news_multiple(subject_profile, from_date="2025-03-01", page_size=5):
    base_url = "https://newsapi.org/v2/everything"

    # Compile search terms from subject
    queries = [subject_profile["name"]] \
            + subject_profile.get("aliases", []) \
            + subject_profile.get("affiliations", [])
    location = subject_profile.get("location", "")

    all_articles = []

    for q in queries:
        full_query = f"{q} {location}".strip()
        params = {
            "q": full_query,
            "from": from_date,
            "sortBy": "relevancy",
            "pageSize": page_size,
            "apiKey": API_KEY
        }

        print(f"🔍 Searching NewsAPI for: '{full_query}'")
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            articles = response.json().get("articles", [])
            print(f"  → Found {len(articles)} articles for: '{full_query}'")
            all_articles.extend(articles)
        else:
            print(f"⚠️ NewsAPI error {response.status_code}: {response.text}")

    return all_articles

# === Main script ===
if __name__ == "__main__":
    subject = load_subject()
    articles = search_news_multiple(subject)

    print(f"\n✅ Total articles retrieved: {len(articles)}")

    for article in articles:
        print(f"- {article['title']} ({article['source']['name']})")
        print(f"  {article['url']}\n")

    with open("output_newsapi.json", "w") as f:
        json.dump(articles, f, indent=2)

    print("📝 Saved combined news results to output_newsapi.json")
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_subject_path():
    path = os.path.join(os.path.expanduser("~"), ".opentrace", "subject.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def load_subject():
    with open(get_subject_path(), "r") as f:
        return json.load(f)

def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

def call_gpt4(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def analyse_news(subject, articles):
    return [{
        "title": a["title"],
        "url": a["url"],
        "summary": call_gpt4(f"""
        You are an OSINT analyst. Analyse the article:

        Title: {a['title']}
        URL: {a['url']}
        Description: {a.get('description', '')}
        """),
        "reliability": "C - Mixed Reliability",
        "confidence": "High"
    } for a in articles[:5]]

def analyse_breaches(email, breaches):
    return [{
        "breach": b["Name"],
        "date": b["BreachDate"],
        "summary": call_gpt4(f"""
        Breach: {b['Name']}
        Date: {b['BreachDate']}
        Description: {b['Description']}

        What was exposed, what’s the risk, and how severe is it?
        """),
        "confidence": "Medium"
    } for b in breaches[:5]]

def analyse_google(subject_name, results):
    return [{
        "title": r["title"],
        "url": r["link"],
        "summary": call_gpt4(f"""
        You are an OSINT analyst. Review this snippet from Google:

        Title: {r["title"]}
        URL: {r["link"]}
        Snippet: {r.get("snippet", "")}

        Identify any reputational or political risk related to {subject_name}.
        """),
        "reliability": "D - Unverified",
        "confidence": "Medium"
    } for r in results[:5]]

if __name__ == "__main__":
    subject = load_subject()
    print(f"🧾 Subject loaded: {subject['name']}")

    news = analyse_news(subject, load_json("output_newsapi.json"))
    breaches = analyse_breaches(subject["email"], load_json("output_hibp.json"))
    google = analyse_google(subject["name"], load_json("output_google.json"))

    with open("report_newsapi.json", "w") as f:
        json.dump(news, f, indent=2)
    with open("report_hibp.json", "w") as f:
        json.dump(breaches, f, indent=2)
    with open("report_google_twitter.json", "w") as f:
        json.dump(google, f, indent=2)

    print("✅ All analysis complete and reports saved.")
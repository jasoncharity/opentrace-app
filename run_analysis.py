import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_subject_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "subject.json"))

def load_subject():
    with open(get_subject_path(), "r") as f:
        return json.load(f)

def load_news_data(filename="output_newsapi.json"):
    with open(filename, "r") as f:
        return json.load(f)

def load_hibp_data(filename="output_hibp.json"):
    with open(filename, "r") as f:
        return json.load(f)

def load_google_results(filename="output_google.json"):
    with open(filename, "r") as f:
        return json.load(f)

def structure_news_findings(subject, findings):
    return [
        {
            "source": "NewsAPI",
            "subject": subject["name"],
            "theme": "Media/Press Coverage",
            "title": item["title"],
            "url": item["url"],
            "summary": item["summary"],
            "reliability": item["reliability"],
            "confidence": item["confidence"]
        }
        for item in findings
    ]

def call_gpt4(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def analyse_news_articles(subject, articles):
    summaries = []
    for article in articles[:5]:
        prompt = f"""
        You are an OSINT analyst. Review the news article below and identify:
        - Reputational concerns
        - Legal or political controversies
        - Links to extremist or high-risk associations

        Title: {article.get("title")}
        URL: {article.get("url")}
        Description: {article.get("description", "")}
        """
        summaries.append({
            "title": article.get("title"),
            "url": article.get("url"),
            "summary": call_gpt4(prompt),
            "reliability": "C - Mixed Reliability",
            "confidence": "High"
        })
    return summaries

def analyse_breaches(email, breaches):
    summaries = []
    for breach in breaches[:5]:
        prompt = f"""
        Breach: {breach.get("Name")}
        Date: {breach.get("BreachDate")}
        Description: {breach.get("Description")}

        You are an OSINT analyst. Identify:
        - Type of data exposed
        - Reputational or security risks
        - Severity (low/medium/high)
        """
        summaries.append({
            "breach": breach.get("Name"),
            "date": breach.get("BreachDate"),
            "summary": call_gpt4(prompt),
            "confidence": "Medium"
        })
    return summaries

def analyse_google_snippets(name, results):
    summaries = []
    for result in results[:5]:
        prompt = f"""
        You are an OSINT analyst. Based on the content below from Google-indexed Twitter content,
        identify reputational or political risks for {name}.

        Title: {result.get("title")}
        URL: {result.get("link")}
        Snippet: {result.get("snippet", "")}
        """
        summaries.append({
            "title": result.get("title"),
            "url": result.get("link"),
            "summary": call_gpt4(prompt),
            "reliability": "D - Unverified",
            "confidence": "Medium"
        })
    return summaries

# === MAIN ===
if __name__ == "__main__":
    subject = load_subject()
    print(f"📦 Loaded subject: {subject['name']}")

    news = analyse_news_articles(subject, load_news_data())
    hibp = analyse_breaches(subject["email"], load_hibp_data())
    google = analyse_google_snippets(subject["name"], load_google_results())

    with open("report_newsapi.json", "w") as f:
        json.dump(structure_news_findings(subject, news), f, indent=2)
    with open("report_hibp.json", "w") as f:
        json.dump(hibp, f, indent=2)
    with open("report_google_twitter.json", "w") as f:
        json.dump(google, f, indent=2)

    print("✅ All report components saved")
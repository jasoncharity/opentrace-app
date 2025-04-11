import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# === Load environment ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Shared path helper ===
def get_subject_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "subject.json"))

# === Load subject profile ===
def load_subject():
    with open(get_subject_path(), "r") as f:
        return json.load(f)

# === Load JSON inputs ===
def load_news_data(filename="output_newsapi.json"):
    with open(filename, "r") as f:
        return json.load(f)

def load_hibp_data(filename="output_hibp.json"):
    with open(filename, "r") as f:
        return json.load(f)

def load_google_results(filename="output_google.json"):
    with open(filename, "r") as f:
        return json.load(f)

# === Structure outputs ===
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

# === GPT Analysis Functions ===
def call_gpt4(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def analyse_news_articles(subject, articles):
    summaries = []
    for article in articles[:5]:
        title = article.get("title")
        url = article.get("url")
        description = article.get("description", "")

        prompt = f"""
        You are an OSINT analyst. Review the news article below and identify:

        - Reputational concerns
        - Legal or political controversies
        - Links to extremist or high-risk associations

        Title: {title}
        URL: {url}
        Description: {description}
        """

        result = call_gpt4(prompt)

        summaries.append({
            "title": title,
            "url": url,
            "summary": result,
            "reliability": "C - Mixed Reliability",
            "confidence": "High"
        })
    return summaries

def analyse_breaches(email, breaches):
    summaries = []
    for breach in breaches[:5]:
        content = f"""
        Breach: {breach.get('Name')}
        Date: {breach.get('BreachDate')}
        Description: {breach.get('Description')}
        """

        prompt = f"""
        You are an OSINT analyst. Review the following breach record for {email}. Identify:

        - Type of data exposed
        - Reputational or security risks
        - Severity (low, medium, high)

        Provide bullet points and include breach name and date in each point.

        {content}
        """

        result = call_gpt4(prompt)

        summaries.append({
            "breach": breach.get("Name"),
            "date": breach.get("BreachDate"),
            "summary": result,
            "confidence": "Medium"
        })
    return summaries

def analyse_google_snippets(subject_name, results):
    summaries = []
    for result in results[:5]:
        title = result.get("title")
        url = result.get("link")
        snippet = result.get("snippet", "")

        prompt = f"""
        You are an OSINT analyst. Based on this snippet from a Google-indexed Twitter post, assess any public risk factors for {subject_name}.

        - Highlight reputational issues
        - Identify political or controversial content
        - Note any affiliations or signals

        Title: {title}
        URL: {url}
        Snippet: {snippet}
        """

        result_text = call_gpt4(prompt)

        summaries.append({
            "title": title,
            "url": url,
            "summary": result_text,
            "reliability": "D - Unverified",
            "confidence": "Medium"
        })
    return summaries

# === MAIN EXECUTION ===
if __name__ == "__main__":
    subject = load_subject()
    print(f"✅ Subject loaded from: {get_subject_path()}")
    print(f"📦 Running analysis for: {subject['name']}")

    # --- NewsAPI Flow ---
    articles = load_news_data()
    news_summaries = analyse_news_articles(subject, articles)

    print("\n=== News Analysis Summary ===\n")
    for i, item in enumerate(news_summaries, 1):
        print(f"{i}. {item['title']}")
        print(f"{item['summary']}\n")

    structured_news = structure_news_findings(subject, news_summaries)
    with open("report_newsapi.json", "w") as f:
        json.dump(structured_news, f, indent=2)
    print("✅ News findings saved to report_newsapi.json")

    # --- HIBP Flow ---
    hibp_data = load_hibp_data()
    hibp_summaries = analyse_breaches(subject["email"], hibp_data)

    print("\n=== Breach Exposure Analysis ===\n")
    for i, item in enumerate(hibp_summaries, 1):
        print(f"{i}. {item['breach']} ({item['date']})")
        print(f"{item['summary']}\n")

    with open("report_hibp.json", "w") as f:
        json.dump(hibp_summaries, f, indent=2)
    print("✅ Breach findings saved to report_hibp.json")

    # --- Google Flow ---
    google_data = load_google_results()
    google_summaries = analyse_google_snippets(subject["name"], google_data)

    print("\n=== Google Search Twitter Analysis ===\n")
    for i, item in enumerate(google_summaries, 1):
        print(f"{i}. {item['title']}")
        print(f"{item['summary']}\n")

    with open("report_google_twitter.json", "w") as f:
        json.dump(google_summaries, f, indent=2)
    print("✅ Google Twitter findings saved to report_google_twitter.json")
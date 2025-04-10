import os
import json
import openai
def load_subject(filename="subject.json"):
    with open(filename, "r") as f:
        return json.load(f)
from dotenv import load_dotenv
from source_reliability import get_source_reliability

# === Load API Key ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === GPT Wrapper ===
def call_gpt4(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# === NewsAPI Functions ===

def load_news_data(filename="output_newsapi.json"):
    with open(filename, "r") as f:
        return json.load(f)

def analyse_news_articles(subject, articles):
    summaries = []
    for article in articles[:5]:
        title = article.get("title")
        url = article.get("url")
        description = article.get("description", "")

        content = f"""
        Title: {title}
        URL: {url}
        Description: {description}
        """

        prompt = f"""
        You are an OSINT analyst. Review the news article below and identify:

        - Any reputational concerns
        - Legal or political controversies
        - Links to extremist or high-risk associations

        Provide bullet points. Add the article's URL in brackets at the end of each point.

        {content}
        """

        result = call_gpt4(prompt)
        reliability = get_source_reliability(url)

        summaries.append({
            "title": title,
            "url": url,
            "summary": result,
            "reliability": reliability,
            "confidence": "High"
        })
    return summaries

def structure_news_findings(subject, findings):
    return [
        {
            "source": "NewsAPI",
            "subject": subject,
            "theme": "Media/Press Coverage",
            "title": item["title"],
            "url": item["url"],
            "summary": item["summary"],
            "reliability": item["reliability"],
            "confidence": item["confidence"]
        }
        for item in findings
    ]

# === HIBP Functions ===

def load_hibp_data(filename="output_hibp.json"):
    with open(filename, "r") as f:
        return json.load(f)

def analyse_breaches(subject_email, breaches):
    summaries = []
    for breach in breaches:
        content = f"""
        Breach: {breach.get('Name')}
        Date: {breach.get('BreachDate')}
        Description: {breach.get('Description')}
        Domain: {breach.get('Domain')}
        """

        prompt = f"""
        You are an OSINT analyst. Based on the breach below involving the email '{subject_email}', identify:

        - The type of data exposed (e.g. passwords, usernames, emails, IPs)
        - The reputational or security risk this creates for the subject
        - The severity of the breach (low/medium/high)

        Return bullet points. Include the breach name and date in each bullet.

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

# === Google Search (Twitter) Functions ===

def load_google_results(filename="output_google.json"):
    with open(filename, "r") as f:
        return json.load(f)

def analyse_google_snippets(subject, results):
    summaries = []
    for result in results[:5]:
        title = result.get("title")
        url = result.get("link")
        snippet = result.get("snippet", "")

        content = f"""
        Title: {title}
        URL: {url}
        Snippet: {snippet}
        """

        prompt = f"""
        You are an OSINT analyst. Based on the content below from Twitter (indexed via Google), extract:

        - Reputational risks or controversial statements
        - Policy positions or campaign themes
        - Links to extremist or politically sensitive figures
        - Anything that may affect public perception of {subject}

        Provide bullet points. Include the source URL at the end of each point.

        {content}
        """

        result_text = call_gpt4(prompt)
        reliability = get_source_reliability(url)

        summaries.append({
            "title": title,
            "url": url,
            "summary": result_text,
            "reliability": reliability,
            "confidence": "Medium"
        })

    return summaries

# === MAIN EXECUTION ===

if __name__ == "__main__":
    subject = load_subject()

    # --- NewsAPI Flow ---
    articles = load_news_data()
    news_summaries = analyse_news_articles(subject["name"], articles)

    print("\n=== News Analysis Summary ===\n")
    for i, item in enumerate(news_summaries, 1):
        print(f"{i}. {item['title']}")
        print(f"{item['summary']}\n")

    structured_news = structure_news_findings(subject, news_summaries)
    with open("report_newsapi.json", "w") as f:
        json.dump(structured_news, f, indent=2)
    print("✅ News findings saved to report_newsapi.json")

    # --- HIBP Flow ---
    email_to_check = subject["email"]
    hibp_data = load_hibp_data()
    hibp_summaries = analyse_breaches(email_to_check, hibp_data)

    print("\n=== Breach Exposure Analysis ===\n")
    for i, item in enumerate(hibp_summaries, 1):
        print(f"{i}. {item['breach']} ({item['date']})")
        print(f"{item['summary']}\n")

    with open("report_hibp.json", "w") as f:
        json.dump(hibp_summaries, f, indent=2)
    print("✅ Breach findings saved to report_hibp.json")

    # --- Google (Twitter) Flow ---
    google_data = load_google_results()
    google_summaries = analyse_google_snippets(subject["name"], google_data)

    print("\n=== Google Search Twitter Analysis ===\n")
    for i, item in enumerate(google_summaries, 1):
        print(f"{i}. {item['title']}")
        print(f"{item['summary']}\n")

    with open("report_google_twitter.json", "w") as f:
        json.dump(google_summaries, f, indent=2)
    print("✅ Google Twitter findings saved to report_google_twitter.json")
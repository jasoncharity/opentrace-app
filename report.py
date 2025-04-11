import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_subject_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "subject.json"))

def load_subject():
    with open(get_subject_path(), "r") as f:
        return json.load(f)

def load_report(filename):
    if not os.path.exists(filename):
        print(f"⚠️ Skipping {filename}")
        return []
    with open(filename, "r") as f:
        return json.load(f)

def generate_executive_summary(subject, sources):
    summaries = [item.get("summary", "") for section in sources for item in section]
    prompt = f"""
    Write a 150–200 word executive summary assessing reputational, political, and digital risk for: {subject['name']}.
    Findings:
    {'\n\n'.join(summaries)}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def format_subject_profile(subject):
    return f"""
**Name**: {subject.get('name')}  
**DOB**: {subject.get('dob')}  
**Email**: {subject.get('email')}  
**Phone**: {subject.get('phone')}  
**Address**: {subject.get('address')}  
**Location**: {subject.get('location')}  
**Aliases**: {", ".join(subject.get('aliases', []))}  
**Affiliations**: {", ".join(subject.get('affiliations', []))}  
**Usernames**: {subject.get('usernames')}  
**Notes**: {subject.get('notes')}
""".strip()

def format_section(title, items):
    section = f"\n## {title}\n"
    if not items:
        return section + "_No findings available._\n"
    for i, item in enumerate(items, 1):
        section += f"\n### {i}. {item.get('title', item.get('breach', 'Untitled'))}\n"
        section += f"{item.get('summary', '')}\n"
        if "url" in item:
            section += f"[Source]({item['url']})\n"
        section += f"**Reliability**: {item.get('reliability', 'Unknown')}  \n"
        section += f"**Confidence**: {item.get('confidence', 'Not rated')}\n"
    return section

# === MAIN ===
if __name__ == "__main__":
    subject = load_subject()
    print(f"📄 Generating report for: {subject['name']}")

    news = load_report("report_newsapi.json")
    hibp = load_report("report_hibp.json")
    google = load_report("report_google_twitter.json")
    reddit = load_report("report_reddit.json")

    summary = generate_executive_summary(subject, [news, hibp, google, reddit])

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    filename_ts = now.strftime("%Y%m%d_%H%M")

    report_md = f"# Protection Briefing: {subject['name']}\n"
    report_md += "_Generated by OpenTrace_\n\n"
    report_md += f"**Generated on:** {timestamp}\n\n"
    report_md += "## Subject Profile\n" + format_subject_profile(subject) + "\n"
    report_md += "\n## Executive Summary\n" + summary + "\n"
    report_md += format_section("Media Coverage (NewsAPI)", news)
    report_md += format_section("Breach Exposure (HIBP)", hibp)
    report_md += format_section("Mentions on Twitter (Google)", google)
    report_md += format_section("Mentions on Reddit", reddit)

    try:
        with open("disclaimer.md", "r") as f:
            report_md += "\n" + f.read()
    except FileNotFoundError:
        report_md += "\n\n_Disclaimer missing._"

    os.makedirs("reports", exist_ok=True)
    name_parts = subject["name"].lower().split()
    filename = f"reports/{name_parts[-1]}_{name_parts[0]}_{filename_ts}.md"

    with open(filename, "w") as f:
        f.write(report_md)

    print(f"✅ Report saved to {filename}")
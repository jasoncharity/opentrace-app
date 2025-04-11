import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# === Load environment ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Shared path helpers ===
def get_subject_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "subject.json"))

def load_subject():
    with open(get_subject_path(), "r") as f:
        return json.load(f)

def load_report(filename):
    if not os.path.exists(filename):
        print(f"⚠️ Skipping {filename} (not found)")
        return []
    with open(filename, "r") as f:
        return json.load(f)

# === GPT Executive Summary ===
def generate_executive_summary(subject, sources):
    all_summaries = [item.get("summary", "") for section in sources for item in section]
    combined = "\n\n".join(all_summaries)

    prompt = f"""
    You are an intelligence analyst. Write a 150–200 word executive summary assessing reputational, political, and digital risk for the subject: {subject['name']}.

    Subject profile:
    - Name: {subject['name']}
    - DOB: {subject.get('dob', '')}
    - Email: {subject.get('email', '')}
    - Location: {subject.get('location', '')}
    - Affiliations: {", ".join(subject.get('affiliations', []))}
    - Aliases: {", ".join(subject.get('aliases', []))}

    Findings:
    {combined}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# === Markdown Formatting ===
def format_subject_profile(subject):
    return f"""
**Name**: {subject.get('name', 'N/A')}  
**Date of Birth**: {subject.get('dob', 'N/A')}  
**Email**: {subject.get('email', 'N/A')}  
**Phone**: {subject.get('phone', 'N/A')}  
**Address**: {subject.get('address', 'N/A')}  
**Location**: {subject.get('location', 'N/A')}  
**Aliases**: {", ".join(subject.get('aliases', []))}  
**Affiliations**: {", ".join(subject.get('affiliations', []))}  
**Usernames**: {subject.get('usernames', 'N/A')}  
**Notes**: {subject.get('notes', '')}
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
        section += f"**Source Reliability**: {item.get('reliability', 'Unknown')}  \n"
        section += f"**Confidence**: {item.get('confidence', 'Not rated')}\n"
    return section

# === MAIN ===
if __name__ == "__main__":
    subject = load_subject()
    print(f"🧪 Loaded subject: {subject['name']}")
    print(f"📄 Generating report for subject: {subject['name']}")

    # Load analysis output
    news = load_report("report_newsapi.json")
    hibp = load_report("report_hibp.json")
    google = load_report("report_google_twitter.json")
    reddit = load_report("report_reddit.json")

    # Executive summary
    summary = generate_executive_summary(subject, [news, hibp, google, reddit])

    # Report header
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M")
    report_md = f"# Protection Briefing: {subject['name']}\n"
    report_md += "_Generated by OpenTrace Prototype_\n\n"
    report_md += f"**Generated on:** {timestamp_str}\n\n"

    report_md += "## Subject Profile\n"
    report_md += format_subject_profile(subject) + "\n"

    report_md += "\n## Executive Summary\n"
    report_md += summary + "\n"

    report_md += format_section("Media Coverage (NewsAPI)", news)
    report_md += format_section("Breach Exposure (HIBP)", hibp)
    report_md += format_section("Mentions on Twitter (Google Search)", google)
    report_md += format_section("Mentions on Reddit", reddit)

    # === Append Legal Disclaimer ===
    try:
        with open("disclaimer.md", "r") as f:
            disclaimer_text = f.read()
        report_md += "\n" + disclaimer_text
    except FileNotFoundError:
        report_md += "\n\n_⚠️ Disclaimer not found. Please ensure disclaimer.md is present._"

    # === Create subject-specific filename ===
    name_parts = subject["name"].strip().lower().split()
    firstname = name_parts[0]
    surname = name_parts[-1] if len(name_parts) > 1 else firstname
    timestamp_file = timestamp.strftime("%Y%m%d_%H%M")
    filename = f"reports/{surname}_{firstname}_{timestamp_file}.md"

    # Ensure /reports directory exists
    os.makedirs("reports", exist_ok=True)

    # Save file
    with open(filename, "w") as f:
        f.write(report_md)

    print(f"✅ Report saved to {filename}")
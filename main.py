import streamlit as st
import json
import subprocess
import os
import time
from datetime import datetime

# === Ensure consistent path to subject.json ===
def get_subject_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "subject.json"))

st.set_page_config(page_title="OpenTrace Briefing Generator", layout="centered")

st.title("🧠 OpenTrace: OSINT Briefing Generator")

st.markdown("""
Welcome to OpenTrace. Fill out a subject profile, run a multi-source intelligence analysis,
and generate a final briefing — all within one interface.
""")

# === Session State to Track Progress ===
if "stage" not in st.session_state:
    st.session_state.stage = 1

# === Step 1: Input Subject ===
st.header("Step 1: Input Subject")

with st.form("subject_form"):
    name = st.text_input("Full Name")
    aliases = st.text_area("Aliases (comma-separated)", value="")
    email = st.text_input("Email")
    dob = st.date_input("Date of Birth")
    address = st.text_input("Address")
    location = st.text_input("Location")
    affiliations = st.text_area("Affiliations (comma-separated)", value="")
    usernames = st.text_input("Usernames / Handles")
    phone = st.text_input("Phone")
    notes = st.text_area("Analyst Notes / Context")

    submitted = st.form_submit_button("Save Subject Profile")
    st.caption(f"📌 Form submitted: {submitted}")

    if submitted:
        subject = {
            "name": name,
            "aliases": [a.strip() for a in aliases.split(",") if a.strip()],
            "email": email,
            "dob": dob.isoformat(),
            "address": address,
            "location": location,
            "affiliations": [a.strip() for a in affiliations.split(",") if a.strip()],
            "usernames": usernames,
            "phone": phone,
            "notes": notes
        }

        try:
            with open(get_subject_path(), "w") as f:
                json.dump(subject, f, indent=2)

            time.sleep(0.5)  # Flush time
            with open(get_subject_path(), "r") as f:
                confirmed = json.load(f)

            st.success("✅ Subject profile saved to subject.json")
            st.caption(f"📂 Path: `{get_subject_path()}`")
            st.caption(f"🕒 Saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown("### 🧾 Confirmed Saved Subject")
            st.json(confirmed)
            st.session_state.stage = 2

        except Exception as e:
            st.error(f"❌ Failed to write or read subject.json: {e}")

# === Step 2: Run Analysis ===
if st.session_state.stage >= 2:
    st.header("Step 2: Run Analysis")

    if st.button("Run run_analysis.py"):
        try:
            with open(get_subject_path(), "r") as f:
                subject = json.load(f)
            st.info(f"🔍 Running analysis for: {subject['name']}")

            with st.spinner("Running multi-source analysis..."):
                try:
                    exec(open("report.py").read())
                    st.success("✅ Report script executed successfully")
                except Exception as e:
                    st.error(f"❌ Failed to generate report: {e}")
            st.success("✅ Analysis complete.")
            st.session_state.stage = 3

        except Exception as e:
            st.error(f"❌ Failed to run analysis: {e}")

# === Step 3: Generate Report ===
if st.session_state.stage >= 3:
    st.header("Step 3: Generate Report")

    if st.button("Run report.py"):
        try:
            with open(get_subject_path(), "r") as f:
                subject = json.load(f)
            st.info(f"📄 Generating report for: {subject['name']}")

            with st.spinner("Generating final report..."):
                try:
                    exec(open("run_analysis.py").read())
                    st.success("✅ Analysis script executed successfully")
                except Exception as e:
                    st.error(f"❌ Failed to run analysis: {e}")
            st.success("✅ Report generated")

        except Exception as e:
            st.error(f"❌ Failed to generate report: {e}")

    if st.checkbox("Preview Report"):
        try:
            with open("protection_briefing.md", "r") as f:
                report_md = f.read()
            st.markdown(report_md)
        except FileNotFoundError:
            st.warning("📄 Report not found. Please run report.py first.")
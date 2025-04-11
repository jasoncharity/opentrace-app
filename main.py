import streamlit as st
import json
import os
import time
from datetime import datetime

def get_subject_path():
    path = os.path.join(os.path.expanduser("~"), ".opentrace", "subject.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

st.set_page_config(page_title="OpenTrace Briefing Generator", layout="centered")
st.title("🧠 OpenTrace: OSINT Briefing Generator")

if "stage" not in st.session_state:
    st.session_state.stage = 1

# === Step 1: Input Subject ===
st.header("Step 1: Input Subject")

with st.form("subject_form"):
    name = st.text_input("Full Name")
    aliases = st.text_area("Aliases (comma-separated)")
    email = st.text_input("Email")
    dob = st.date_input("Date of Birth")
    address = st.text_input("Address")
    location = st.text_input("Location")
    affiliations = st.text_area("Affiliations (comma-separated)")
    usernames = st.text_input("Usernames / Handles")
    phone = st.text_input("Phone")
    notes = st.text_area("Analyst Notes / Context")
    submitted = st.form_submit_button("Save Subject Profile")

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
            time.sleep(0.5)
            with open(get_subject_path(), "r") as f:
                confirmed = json.load(f)

            st.success("✅ Subject profile saved")
            st.caption(f"📂 Saved to: {get_subject_path()}")
            st.caption(f"🧾 Confirmed subject: {confirmed['name']}")
            st.json(confirmed)
            st.session_state.stage = 2
        except Exception as e:
            st.error(f"❌ Failed to write subject.json: {e}")

# === Step 2: Run Analysis ===
if st.session_state.stage >= 2:
    st.header("Step 2: Run Analysis")
    if st.button("Run Analysis"):
        try:
            exec(open("run_analysis.py").read())
            st.success("✅ Analysis complete")
            st.session_state.stage = 3
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")

# === Step 3: Generate Report ===
if st.session_state.stage >= 3:
    st.header("Step 3: Generate Report")
    if st.button("Run Report"):
        try:
            exec(open("report.py").read())
            st.success("✅ Report generated")
        except Exception as e:
            st.error(f"❌ Report failed: {e}")

    if st.checkbox("Preview Report"):
        try:
            with open("protection_briefing.md", "r") as f:
                st.markdown(f.read())
        except FileNotFoundError:
            st.warning("📄 Report not found. Please run report.py first.")
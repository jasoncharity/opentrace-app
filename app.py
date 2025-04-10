import streamlit as st
import json
import subprocess

st.set_page_config(page_title="OpenTrace Briefing Generator", layout="centered")
st.title("🧠 OpenTrace Prototype 1")

st.markdown("""
Not to user: this form is for testing purposes only and should not be relied upon for real-world intelligence reporting.
""")

# === Session state to manage workflow ===
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
    notes = st.text_area("Context / Analyst Notes")

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

    with open("subject.json", "w") as f:
        json.dump(subject, f, indent=2)

    st.success("✅ Subject profile saved.")
    st.session_state.stage = 2

# === Step 2: Run Analysis (main.py) ===
if st.session_state.stage >= 2:
    st.header("Step 2: Run Source Analysis")
    if st.button("Run main.py (GPT-powered analysis)"):
        with st.spinner("Running multi-source analysis..."):
            result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
            st.text(result.stdout[-1000:])
        st.success("✅ Analysis complete.")
        st.session_state.stage = 3

# === Step 3: Generate Report ===
if st.session_state.stage >= 3:
    st.header("Step 3: Generate & View Report")
    if st.button("Generate Final Report (Markdown)"):
        with st.spinner("Building final report..."):
            result = subprocess.run(["python", "report.py"], capture_output=True, text=True)
            st.text(result.stdout[-1000:])
        st.success("✅ Report generated: protection_briefing.md")

    if st.checkbox("Preview Report"):
        with open("protection_briefing.md", "r") as f:
            report = f.read()
        st.markdown(report)
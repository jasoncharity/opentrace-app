import streamlit as st
import json
import subprocess

# === Page Setup ===
st.set_page_config(page_title="OpenTrace Briefing Generator", layout="centered")
st.title("OpenTrace Prototype Brief Capture")

st.markdown("Complete the subject profile below and click **Generate Briefing** to produce a full intelligence report.")

# === Subject Form ===
with st.form("subject_form"):
    name = st.text_input("Full Name")
    aliases = st.text_area("Aliases (comma-separated)", value="")
    email = st.text_input("Email")
    dob = st.date_input("Date of Birth (YYYY/MM/DD format)")
    address = st.text_input("Full Address")
    location = st.text_input("Location (City, Region, Country)")
    affiliations = st.text_area("Affiliations (comma-separated)", value="")
    usernames = st.text_input("All known usernames and social media handles (comma-separated)")
    phone = st.text_input("Phone Number")
    notes = st.text_area("Notes or additional context")

    submitted = st.form_submit_button("Generate Briefing")

# === Run the Report ===
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

    # Save to subject.json
    with open("subject.json", "w") as f:
        json.dump(subject, f, indent=2)

    st.success("✅ Subject profile saved to subject.json")

    # Run main.py
    with st.spinner("Running analysis..."):
        subprocess.run(["python", "main.py"], check=True)

    # Run report.py
    with st.spinner("Generating final report..."):
        subprocess.run(["python", "report.py"], check=True)

    st.success("✅ Briefing complete — protection_briefing.md generated.")

    # Optional: Preview the output
    if st.checkbox("Preview Report"):
        with open("protection_briefing.md", "r") as f:
            report_md = f.read()
        st.markdown(report_md)
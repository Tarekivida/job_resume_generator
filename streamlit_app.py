import streamlit as st
import os
import json
from datetime import datetime
from agents.job_parser import extract_job_description
from agents.resume_generator import extract_text_from_pdf, perform_strategic_analysis, generate_resume, generate_cover_letter

HISTORY_PATH = os.path.join("output", "history.json")

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def run_app():
    history = load_history()
    st.title("AI-Powered Resume Generator")
    st.markdown(
        "Enter a LinkedIn job URL and generate a tailored resume based on your CV."
    )
    
    st.sidebar.title("Application History")
    if history:
        for idx, entry in enumerate(history):
            if st.sidebar.button(f"{idx+1}. {entry['url']}"):
                st.sidebar.write(f"**Date:** {entry['timestamp']}")
                st.sidebar.markdown("**Strategic Analysis:**")
                st.sidebar.text(entry["analysis"])
                st.sidebar.markdown("**Resume:**")
                st.sidebar.code(entry["resume"])
                st.sidebar.markdown("**Cover Letter:**")
                st.sidebar.code(entry["cover_letter"])
    else:
        st.sidebar.write("No history yet.")

    url = st.text_input("LinkedIn Job URL", "")
    cv_file = st.file_uploader("Upload your CV (PDF)", type=["pdf"])
    if not cv_file:
        cv_path = os.path.join("prompts", "CVFULL.pdf")
    else:
        cv_path = os.path.join("output", "uploaded_cv.pdf")
        with open(cv_path, "wb") as f:
            f.write(cv_file.getbuffer())

    if st.button("Generate Resume"):
        if not url:
            st.error("Please enter a LinkedIn job URL.")
            return
        with st.spinner("Extracting job description..."):
            job_description = extract_job_description(url)[:1500]
        with st.spinner("Loading CV..."):
            cv_text = extract_text_from_pdf(cv_path)
        with st.spinner("Performing strategic analysis..."):
            analysis_text = perform_strategic_analysis(job_description, cv_text)
        if analysis_text:
            st.subheader("Strategic Analysis")
            st.text_area("", analysis_text, height=200)
        with st.spinner("Generating resume..."):
            resume_text = generate_resume(job_description, cv_text)
        with st.spinner("Generating cover letter..."):
            cover_letter_text = generate_cover_letter(job_description, cv_text)
        if resume_text:
            st.subheader("Generated Resume")
            st.text_area("", resume_text, height=400)
        if cover_letter_text:
            st.subheader("Generated Cover Letter")
            st.text_area("", cover_letter_text, height=400)
        # Download buttons
        st.download_button("Download Resume", resume_text, "resume.md", "text/markdown")
        st.download_button("Download Cover Letter", cover_letter_text, "cover_letter.md", "text/markdown")

        # Save to history
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "analysis": analysis_text,
            "resume": resume_text,
            "cover_letter": cover_letter_text
        }
        history.append(new_entry)
        save_history(history)

run_app()

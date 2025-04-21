#!/usr/bin/env python
# Streamlit web app for generating resumes and cover letters based on a LinkedIn job posting and a PDF CV.
# It performs strategic analysis and offers download buttons along with historical view of past generations.
import streamlit as st
import os
import json
from datetime import datetime
from agents.job_parser import extract_job_description
from agents.resume_generator import extract_text_from_pdf, perform_strategic_analysis, generate_resume, generate_cover_letter

HISTORY_PATH = os.path.join("output", "history.json")

    # Load past resume/cover letter generations from the history file
def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

    # Save resume/cover letter generation results to a history file
def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    # Main function to run the Streamlit application
def run_app():
    # Load generation history from disk
    history = load_history()
    st.title("AI-Powered Resume Generator")
    st.markdown(
        "Enter a LinkedIn job URL and generate a tailored resume based on your CV."
    )
    
    # Display historical resume/cover letter generations in sidebar
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

    # Input fields for job URL and PDF CV
    url = st.text_input("LinkedIn Job URL", "")
    cv_file = st.file_uploader("Upload your CV (PDF)", type=["pdf"])
    if not cv_file:
        cv_path = os.path.join("prompts", "CVFULL.pdf")
    else:
        cv_path = os.path.join("output", "uploaded_cv.pdf")
        with open(cv_path, "wb") as f:
            f.write(cv_file.getbuffer())

    # Trigger resume and cover letter generation process when button is clicked
    if st.button("Generate Resume"):
        if not url:
            st.error("Please enter a LinkedIn job URL.")
            return
        # Step 1: Extract job description from the LinkedIn URL
        with st.spinner("Extracting job description..."):
            job_description = extract_job_description(url)[:1500]
        # Step 2: Extract text from the uploaded CV
        with st.spinner("Loading CV..."):
            cv_text = extract_text_from_pdf(cv_path)
        # Step 3: Analyze how the CV matches the job description
        with st.spinner("Performing strategic analysis..."):
            analysis_text = perform_strategic_analysis(job_description, cv_text)
        if analysis_text:
            st.subheader("Strategic Analysis")
            st.text_area("", analysis_text, height=200)
        # Step 4: Generate the optimized resume
        with st.spinner("Generating resume..."):
            resume_text = generate_resume(job_description, cv_text)
        # Step 5: Generate the personalized cover letter
        with st.spinner("Generating cover letter..."):
            cover_letter_text = generate_cover_letter(job_description, cv_text)
        if resume_text:
            st.subheader("Generated Resume")
            st.text_area("", resume_text, height=400)
        if cover_letter_text:
            st.subheader("Generated Cover Letter")
            st.text_area("", cover_letter_text, height=400)
        # Provide buttons for downloading generated resume and cover letter
        st.download_button("Download Resume", resume_text, "resume.md", "text/markdown")
        st.download_button("Download Cover Letter", cover_letter_text, "cover_letter.md", "text/markdown")

        # Add new generation result to history and save it
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

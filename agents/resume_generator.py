#!/usr/bin/env python3
# This script defines core logic for generating resumes and cover letters using autonomous AI agents.
# It supports PDF CV parsing, strategic analysis, resume optimization through multi-agent debate,
# and cover letter creation tailored to a specific job description.

import os
import json
from datetime import datetime
import fitz  # PyMuPDF
from autogen import ConversableAgent
from utils.llm_configs import llm_config

HISTORY_PATH = os.path.join("output", "history.json")

# Load previous generation history if available
def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save generation history to a file
def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# Use a specialized agent to perform SWOT-like analysis between the job description and CV
def perform_strategic_analysis(job_description, cv_text):
    """
    Generate a strategic analysis of the user's CV relative to the job description.
    Returns bullet-point insights.
    """
    analysis_agent = ConversableAgent(
        name="strategic_analyzer",
        llm_config=llm_config,
        system_message="""
    You are a senior career strategist. Given the user's CV and a target job description,
    identify the user's key strengths, gaps, and recommend focus areas to optimize the resume.
    Respond in concise, markdown-formatted bullet points.
        """,
        code_execution_config=False,
        human_input_mode="NEVER",
    )
    prompt = (
        f"CV:\n{cv_text}\n\nJob Description:\n{job_description}\n\n"
        "Please provide a strategic analysis in bullet points."
    )
    return analysis_agent.generate_reply([{"role": "user", "content": prompt}])

# Extract full text from a PDF CV using PyMuPDF
def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyMuPDF.
    """
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

# Load prompt templates for resume and cover letter generation
with open("prompts/resume_prompt.txt", "r", encoding="utf-8") as f:
    resume_prompt = f.read()
with open("prompts/cover_letter_prompt.txt", "r", encoding="utf-8") as f:
    cover_letter_prompt = f.read()

# Generate an optimized resume through a multi-agent iterative improvement process
def generate_resume(job_description, cv_text, max_rounds=4):
    """
    Manually run a round-robin discussion between resume_creator and resume_challenger,
    then return strategic assessment and final optimized resume.
    """
    # Run a strategic analysis to guide the resume creation
    strategic_analysis = perform_strategic_analysis(job_description, cv_text)

    # Initialize the resume creator agent
    creator = ConversableAgent(
        name="resume_creator",
        llm_config=llm_config,
        system_message=resume_prompt + "\n\n"
                       "⚠️ **Constraint:** Use only information present in the provided CV. "
                       "Do not invent or fabricate any experiences, dates, or details not found in the CV."
                       "\n\nPlease generate the resume in the same language as the provided job description.",
        code_execution_config=False,
        human_input_mode="NEVER",
    )
    # Initialize the resume challenger agent for critique and improvement
    challenger = ConversableAgent(
        name="resume_challenger",
        llm_config=llm_config,
        system_message="""
    You are a senior recruiter at a large international company. Your mission is to read the generated resume,
    identify any vague or weak sections, suggest more impactful phrasing, and ensure ATS-friendliness.
    Respond only in markdown, professionally.
        """,
        code_execution_config=False,
        human_input_mode="NEVER",
    )
    agents = [creator, challenger]
    # Seed the agent conversation with initial system/user prompts
    conversation = [
        {"role": "system", "content": resume_prompt},
        {"role": "user", "content": (
            f"Based on this strategic analysis:\n{strategic_analysis}\n\n"
            f"Please draft the complete ATS-optimized resume in markdown format using the CV and job description.\n\n"
            f"CV:\n{cv_text}\n\n"
            f"Job Description:\n{job_description}"
        )}
    ]
    # Conduct a round-robin dialogue between the creator and challenger agents
    for i in range(max_rounds):
        agent = agents[i % 2]
        reply = agent.generate_reply(conversation)
        conversation.append({"role": "assistant", "name": agent.name, "content": reply})
    # Extract the final version of the resume from the conversation history
    final_msgs = [m["content"] for m in conversation if m.get("name") == creator.name]
    final_resume = final_msgs[-1] if final_msgs else ""
    return final_resume

# Generate a cover letter tailored to the job description using a dedicated agent
def generate_cover_letter(job_description, cv_text):
    """
    Generate a cover letter based on the job description and CV text.
    """
    agent = ConversableAgent(
        name="cover_letter_agent",
        llm_config=llm_config,
        system_message=cover_letter_prompt,
        code_execution_config=False,
        human_input_mode="NEVER",
    )
    prompt = (
        f"{cover_letter_prompt}\n\nBase CV:\n{cv_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Please draft a persuasive cover letter."
    )
    response = agent.generate_reply([{"role": "user", "content": prompt}])
    return response

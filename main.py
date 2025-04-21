#!/usr/bin/env python3
# Main script for orchestrating resume and cover letter generation using AI agents.
# It loads job and CV inputs, performs strategic analysis, and conducts multi-agent discussions.
import os
import fitz  # PyMuPDF
from autogen import ConversableAgent
from utils.llm_configs import llm_config
from agents.resume_generator import perform_strategic_analysis
import json
from datetime import datetime

HISTORY_PATH = os.path.join("output", "history.json")

# Load past resume and cover letter generation history from file

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
 
# Save updated generation history to file
def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

#+ Generate an ATS-optimized resume using a creator-challenger agent loop and strategic analysis
def generate_resume(job_description, cv_text, max_rounds=4):
    """
    Manually run a round-robin discussion between resume_creator and resume_challenger,
    then return final optimized resume.
    """
    # Pre-run strategic analysis to guide resume writing
    # Analyze the alignment between job description and CV to guide the generation process
    strategic_analysis = perform_strategic_analysis(job_description, cv_text)

    # Initialize agents
    # Set up the resume creator agent
    creator = ConversableAgent(
        name="resume_creator",
        llm_config=llm_config,
        system_message=resume_prompt,
        code_execution_config=False,
        human_input_mode="NEVER",
    )
    # Set up the resume challenger agent to review and improve the resume
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
    # Seed conversation
    # Start the conversation with a strategic prompt including job and CV content
    conversation = [{
        "role": "user",
        "content": (
            f"Strategic Analysis:\n{strategic_analysis}\n\n"
            f"Now, generate an ATS-optimized resume in markdown using the CV and Job Description.\n\n"
            f"CV:\n{cv_text}\n\nJob Description:\n{job_description}"
        )
    }]
    # Round-robin discussion
    # Alternate between the creator and challenger agents to refine the resume
    for i in range(max_rounds):
        agent = agents[i % 2]
        reply = agent.generate_reply(conversation)
        conversation.append({"role": "assistant", "name": agent.name, "content": reply})
    # Extract final resume
    # Extract the final version of the resume from the creator agent's last message
    final_msgs = [m["content"] for m in conversation if m.get("name") == creator.name]
    final_resume = final_msgs[-1] if final_msgs else ""
    return final_resume

## Generate a persuasive cover letter using a dedicated AI agent
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

    # Construct the prompt including base CV and job description
    prompt = (
        f"{cover_letter_prompt}\n\nBase CV:\n{cv_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Please draft a persuasive cover letter."
    )
    # Generate the cover letter using the cover_letter_agent
    response = agent.generate_reply([{"role": "user", "content": prompt}])
    return response

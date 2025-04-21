# Job Resume Generator

This project is an AI-powered tool designed to help users generate customized resumes and cover letters tailored to specific job descriptions using advanced natural language models.

## Features

- Upload a LinkedIn job posting URL and your existing CV (PDF)
- Extract job description automatically using Selenium
- Perform strategic analysis of the CV vs. job description
- Generate optimized resumes through a multi-agent conversation
- Create tailored cover letters using the same inputs
- Download results as markdown files
- View history of previously generated content

## Technologies Used

- Python 3.10+
- Streamlit
- Selenium
- PyMuPDF
- BeautifulSoup
- OpenAI (or other LLM) API
- LangChain (for agent orchestration)

## How It Works

1. The user uploads a job URL and a PDF CV.
2. The system scrapes and parses the job description.
3. A strategic analysis is performed comparing the CV to the job requirements.
4. Two autonomous agents ("resume_creator" and "resume_challenger") debate and refine a resume based on this analysis.
5. A third agent generates a cover letter tailored to the same job.
6. The app displays and offers download buttons for all generated documents.

## Getting Started

### Prerequisites

- Python 3.10+
- Chrome browser and ChromeDriver installed
- OpenAI API key

### Installation

```bash
git clone https://github.com/yourusername/job_resume_generator.git
cd job_resume_generator
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

## Project Structure

```
job_resume_generator/
├── app.py                  # Streamlit app UI
├── job_parser.py           # Extracts job descriptions from LinkedIn
├── resume_generator.py     # Multi-agent logic for resume & letter creation
├── prompts/                # Prompt templates for agents
├── output/                 # Saved history and debug files
├── requirements.txt
└── README.md
```

## License

MIT License

## Author

Tarek Aghenda

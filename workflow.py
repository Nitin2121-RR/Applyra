from langgraph.graph import StateGraph , START , END
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv
import os
from state import State
from langchain_google_genai import ChatGoogleGenerativeAI
import fitz
from schema import company_details , candidate_details , application_assistent_response

load_dotenv(".env")

gemini_1 = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY_1"),
)

gemini_2 = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY_2"),
)



def job_analyse(state:State):
    uuid = state['uuid']
    resume_path = f"resume/{uuid}.pdf"
    docs = fitz.open(resume_path)
    full_text = ""
    for page in docs:
        full_text += page.get_text("text", sort=True) + "\n"
    # Resume text
    

    # Job description text
    job_description_path = f"description/{uuid}.txt"
    with open(job_description_path, "r") as f:
        text = f.read()

    # Adding role , company_name and required_skills

    llm_structured = gemini_1.with_structured_output(company_details)
    JOB_ANALYZER_PROMPT = """
You are an expert Job Description Analyzer.

Your task is to carefully analyze the provided job description and extract accurate, explicit job information.

Extract the following information:

1. company_name
   - Identify the company or organization offering the role.
   - Use the company name exactly as stated in the job description.
   - Do not guess or infer a company name if it is not explicitly mentioned.
   - If the company name is unavailable, return "Unknown".

2. role
   - Identify the exact job title or role being offered.
   - Prefer the official title explicitly mentioned in the job description.
   - Do not unnecessarily rewrite, shorten, or generalize the role.
   - If the role is unavailable, return "Unknown".

3. required_skills
   - Extract technical skills, technologies, programming languages, frameworks, libraries, databases, platforms, cloud services, tools, and technical concepts required or expected for the role.
   - Include skills mentioned as required, expected, preferred, desired, or good-to-have when they are relevant to the candidate's technical capability.
   - Normalize obvious naming variations to commonly recognized names.
   - For example:
     "js" -> "JavaScript"
     "postgres" -> "PostgreSQL"
     "k8s" -> "Kubernetes"
   - Keep distinct technologies as separate skills.
   - Do not extract responsibilities, personality traits, soft skills, benefits, salary information, location, or generic phrases as skills.
   - Do not invent skills that are not supported by the job description.
   - Remove duplicate skills.
   - Return concise skill names rather than complete sentences.

Analyze only the supplied job description.

JOB DESCRIPTION:
{job_description}
"""
    response = llm_structured.invoke(JOB_ANALYZER_PROMPT.format(job_description=text))
    
    return {
        "role": response.role,
        "company_name": response.company_name,
        "required_skills": response.required_skills,
        "resume_text": full_text ,
        "job_description_text": text
    }

def profile_match(state:State):
    llm_structured = gemini_2.with_structured_output(candidate_details)
    PROMPT = PROFILE_MATCHER_PROMPT = """
You are an expert technical resume-to-job profile matcher.

Your task is to evaluate how well the candidate's resume matches the technical skill requirements for the given role.

You are provided with:
- The company name
- The job role
- A list of required skills extracted from the job description
- The candidate's complete resume text

Carefully analyze the complete resume, including the skills section, projects, work experience, internships, certifications, and technical achievements.

For every skill in REQUIRED SKILLS, determine whether the candidate's resume provides sufficient evidence of that skill.

MATCHED SKILLS RULES:
- A required skill is matched if it is explicitly mentioned in the resume.
- A required skill is also matched if the candidate clearly demonstrates practical use of it in a project, internship, or work experience.
- Recognize standard aliases and equivalent names.
- Examples:
  "JS" and "JavaScript" are equivalent.
  "Postgres" and "PostgreSQL" are equivalent.
  "K8s" and "Kubernetes" are equivalent.
  "ML" and "Machine Learning" are equivalent.
- Return only skills that exist in REQUIRED SKILLS.
- Preserve the original skill name from REQUIRED SKILLS.

MISSING SKILLS RULES:
- A required skill is missing if the resume contains no explicit or clearly demonstrated evidence of that skill.
- Do not assume knowledge of one technology implies knowledge of another.
- For example:
  Python does not imply Django.
  Machine Learning does not imply TensorFlow.
  Docker does not imply Kubernetes.
  LangChain does not automatically imply LangGraph.
- Return only skills that exist in REQUIRED SKILLS.
- Preserve the original skill name from REQUIRED SKILLS.

IMPORTANT RULES:
- Every required skill must appear in exactly one category: matched_skills or missing_skills.
- A skill must never appear in both categories.
- Do not invent skills, experience, projects, or candidate capabilities.
- Do not add resume skills that are not present in REQUIRED SKILLS.
- Evaluate the entire resume, not only the skills section.
- Be evidence-based and consistent.

COMPANY NAME:
{company_name}

JOB ROLE:
{role}

REQUIRED SKILLS:
{required_skills}

CANDIDATE RESUME:
{resume_text}
"""
    responce = llm_structured.invoke(PROMPT.format(
        company_name=state['company_name'],
        role=state['role'],
        required_skills=state['required_skills'],
        resume_text=state['resume_text']
    ))
    return {
        "missing_skills": responce.missing_skills,
        "matched_skills": responce.matched_skills,
        "match_score": responce.match_score
    }

def application_assistent(state:State):
    PROMPT = APPLICATION_ASSISTANT_PROMPT = """
You are an expert job application assistant and professional recruiter outreach writer.

Your task is to analyze the candidate's job match information and resume, then:

1. Provide a useful application recommendation when needed.
2. Write a professional, personalized recruiter outreach email.

RECOMMENDATION RULES:

- Analyze the candidate's matched skills, missing skills, match score, job role, and resume.
- Provide specific and actionable advice that can improve the candidate's application.
- Highlight relevant projects, internship experience, technical skills, or achievements the candidate should emphasize.
- If important skills are missing, mention the most relevant gaps and suggest what the candidate should focus on.
- Do not give generic advice such as "work hard", "prepare well", or "improve your skills".
- Do not invent experience, skills, projects, achievements, or qualifications.
- Keep the recommendation concise and directly relevant to the role.
- If there is no meaningful recommendation to provide, return null.

RECRUITER EMAIL RULES:

- Write the email from the candidate's perspective in first person.
- Clearly express interest in the provided job role and company.
- Use the candidate's complete resume to identify the strongest and most relevant experience.
- Prioritize projects, internships, technical work, and skills that align with the matched skills and job requirements.
- Mention only information explicitly supported by the candidate's resume.
- Never claim experience with a missing skill.
- Do not mention the match score.
- Do not mention matched_skills or missing_skills as analysis categories.
- Do not invent a recruiter name.
- Do not use placeholders such as [Recruiter Name], [Your Name], [Company Name], or [Role].
- If the candidate's name is clearly present in the resume, use it in the email sign-off.
- Keep the email concise, professional, natural, and recruiter-friendly.
- Avoid exaggerated claims and overly formal language.
- Avoid sounding AI-generated.
- Write 3 to 4 short paragraphs.
- Return the email as plain text.
- Preserve proper email formatting using newline characters between paragraphs.
- Use a professional greeting such as "Hi," when no recruiter name is available.
- End with a natural professional sign-off.

COMPANY NAME:
{company_name}

JOB ROLE:
{role}

REQUIRED SKILLS:
{required_skills}

MATCHED SKILLS:
{matched_skills}

MISSING SKILLS:
{missing_skills}

MATCH SCORE:
{match_score}

CANDIDATE RESUME:
{resume_text}
"""
    llm_structured = gemini_1.with_structured_output(application_assistent_response)
    responce = llm_structured.invoke(PROMPT.format(
        company_name=state['company_name'],
        role=state['role'],
        required_skills=state['required_skills'],
        matched_skills=state['matched_skills'],
        missing_skills=state['missing_skills'],
        match_score=state['match_score'],
        resume_text=state['resume_text']
    ))

    return {
        "recommendation": responce.recommendation,
        "email_suggestion": responce.email_suggestion
    }

graph = StateGraph(State) 

#Nodes

graph.add_node("job_analyse", job_analyse)
graph.add_node("profile_match", profile_match)
graph.add_node("application_assistent", application_assistent)

#Edges

graph.add_edge(START,"job_analyse")
graph.add_edge("job_analyse", "profile_match")
graph.add_edge("profile_match", "application_assistent")
graph.add_edge("application_assistent", END) 

graph = graph.compile()
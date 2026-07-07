from typing import List, Optional , TypedDict
from pydantic import BaseModel 


class State(TypedDict):
    company_name : str #
    role : str #
    match_score : int #
    required_skills : List[str] #
    matched_skills : List[str] #
    missing_skills : List[str] #
    recommendation : Optional[str] #
    resume_text : str #
    job_description_text : str #
    uuid : str #
    email_suggestion : Optional[str] #

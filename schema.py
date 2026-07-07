from pydantic import BaseModel , EmailStr
from typing import Optional , List , Annotated
from datetime import datetime
class UserCreate(BaseModel):
    username : str
    email : EmailStr
    password : str

class login_user(BaseModel):
    email : EmailStr
    password : str


class ApplicationListingResponse(BaseModel):

    id: int

    company_name: str | None

    role: str | None

    match_score: int | None

    applied_at: datetime 


    class Config:

        from_attributes = True


class job_description(BaseModel):
    job_description : str
    resume_uuid : str


class company_details(BaseModel):
    required_skills : Annotated[List[str], "Required Skills"]
    role : Annotated[str , "Job role"]
    company_name : Annotated[str , "Company Name"]

class candidate_details(BaseModel):
    matched_skills : List[str]
    missing_skills : List[str]
    match_score : int

class application_assistent_response(BaseModel):
    recommendation : Optional[str]
    email_suggestion : Optional[str]
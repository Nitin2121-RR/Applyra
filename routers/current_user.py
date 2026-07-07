from fastapi import APIRouter , Depends , Request , File , UploadFile
from database import get_db
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from auth import get_current_user
from schema import ApplicationListingResponse , job_description
import models
import uuid
import shutil
import os
from state import State
from workflow import graph

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/listing")
async def index(request : Request):
    return templates.TemplateResponse(
        request=request,
        name="listings.html"
    )

@router.get(
    "/listing/all",
    response_model=list[ApplicationListingResponse] 
)
def get_all_listings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    applications = (
        db.query(models.Application)
        .filter(
            models.Application.user_id ==
            current_user.id
        )
        .order_by(
            models.Application.applied_at.desc()
        )
        .all()
    )


    return applications 


@router.get('/user/resume')
def index(request : Request):
    return templates.TemplateResponse(
        request=request,
        name="resume_upload.html"
    )

async def save_resume(
    resume: UploadFile
):
    resume_uuid = str(uuid.uuid4()) 
    os.makedirs("resume" , exist_ok=True)
    path = f"resume/{resume_uuid}.pdf"

    with open(path, "wb") as f:
        shutil.copyfileobj(resume.file, f)
    
    return resume_uuid

@router.post('/user/resume')
async def upload_resume(

    resume: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    
    resume_uuid = await save_resume(
        resume
    )


    return {
        "resume_uuid": resume_uuid
    }

@router.get("/user/job_description")
def index(request : Request):
    return templates.TemplateResponse(
        request=request,
        name="job_description.html"
    )

@router.post("/user/job_description")
async def create_job_description(
    job_description : job_description,
    current_user = Depends(get_current_user)
):
    os.makedirs("description" , exist_ok=True)
    with open(f"description/{job_description.resume_uuid}.txt" , "w" , encoding="utf-8") as f:
        f.write(job_description.job_description)
    
    return job_description

@router.get("/user/analyse_resume")
def index(request : Request):
    return templates.TemplateResponse(
        request=request,
        name="application_analysis.html"
    )

@router.get("/user/analyse_resume/{uuid}") 
async def index(uuid : str , current_user = Depends(get_current_user) , db : Session = Depends(get_db)):

    responce = graph.invoke({"uuid" : uuid})
    application = models.Application(
        user_id=current_user.id,
        company_name=responce['company_name'],
        role=responce['role'],
        job_description=responce['job_description_text'],
        required_skills=responce['required_skills'],
        matched_skills=responce['matched_skills'],
        missing_skills=responce['missing_skills'],
        match_score=responce['match_score'],
        recommendation=responce['recommendation'],
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application

@router.get("/listing/details/{listing_id}")
def index(request : Request):
    return templates.TemplateResponse(
        request=request,
        name="application_details.html"
    ) 


@router.get("/listing/{listing_id}")
def index(listing_id : int , current_user = Depends(get_current_user) , db : Session = Depends(get_db)):

    application = db.query(models.Application).filter(models.Application.id == listing_id).first()

    return application

@router.delete("/listing/{listing_id}")
def index(listing_id : int , current_user = Depends(get_current_user) , db : Session = Depends(get_db)):

    application = db.query(models.Application).filter(models.Application.id == listing_id) 

    application.delete(synchronize_session=False)
    db.commit()

    return application
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
import models
from datetime import datetime , timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv(".env")

scheduler = BackgroundScheduler()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY_1"),
)
def check_remainder():
    db = SessionLocal()
    try:
        time = datetime.now() - timedelta(days=3)
        applications = db.query(models.Application).filter(models.Application.applied_at <= time).all()
        
        for application in applications:
            title = f"You applied for {application.role} at {application.company_name} on {application.applied_at}."

            responce = llm.invoke(f"You have a create a notification message to the user to make a remainder regarding " \
            "the application." \
            f"role - {application.role}" \
            f"company_name - {application.company_name}" \
            f"applied_at - {application.applied_at}")
            
            notification = models.Notification(title=title, message=responce.content[0]["text"], application_id=application.id, user_id=application.user_id)
            db.add(notification)
            db.commit()
            db.refresh(notification)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(check_remainder, "interval", days=1)
    scheduler.start()


from sqlalchemy import Column, Integer, String , ForeignKey , Text , JSON , DateTime
from datetime import datetime, timezone
from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer , primary_key=True)
    username = Column(String , nullable=False)
    email = Column(String , nullable=False , unique=True)
    password = Column(String , nullable=False)

    
class Application(Base):

    __tablename__ = "applications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    company_name = Column(
        String,
        nullable=True
    )

    role = Column(
        String,
        nullable=True
    )

    job_description = Column(
        Text,
        nullable=False
    )

    required_skills = Column(
        JSON,
        nullable=True 
    )

    matched_skills = Column(
        JSON,
        nullable=True
    )

    missing_skills = Column(
        JSON,
        nullable=True 
    )

    match_score = Column(
        Integer,
        nullable=True
    )

    recommendation = Column(
        Text,
        nullable=True
    )

    applied_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Notification(Base):

    __tablename__ = "notification"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False
    )
    message = Column(
        String,
        nullable=False
    )
    title = Column(
        String,
        nullable=False
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
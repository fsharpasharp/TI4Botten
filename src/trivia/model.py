import enum
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Integer, String, Enum, Boolean, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.sql import func
from typing import Optional, List

from .. import models


class TriviaSessionState(enum.Enum):
    WAITING = "Waiting"
    ACTIVE = "Active"
    FINISHED = "Finished"


class TriviaSession(models.Base):
    __tablename__ = "trivia_session"
    
    session_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[int] = mapped_column(Integer, unique=True)
    creator_id: Mapped[int] = mapped_column(Integer)
    state: Mapped[TriviaSessionState] = mapped_column(Enum(TriviaSessionState), default=TriviaSessionState.WAITING)
    current_question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trivia_question.question_id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    current_question: Mapped[Optional["TriviaQuestion"]] = relationship("TriviaQuestion")
    answers: Mapped[List["TriviaAnswer"]] = relationship("TriviaAnswer", back_populates="session")


class TriviaQuestion(models.Base):
    __tablename__ = "trivia_question"
    
    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_text: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(String)
    category: Mapped[Optional[str]] = mapped_column(String, default="general")
    difficulty: Mapped[Optional[str]] = mapped_column(String, default="medium") 
    creator_id: Mapped[Optional[int]] = mapped_column(Integer)  # Who added this question
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class TriviaAnswer(models.Base):
    __tablename__ = "trivia_answer"
    
    answer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("trivia_session.session_id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("trivia_question.question_id"))
    player_id: Mapped[int] = mapped_column(Integer)
    answer_text: Mapped[str] = mapped_column(String)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    session: Mapped["TriviaSession"] = relationship("TriviaSession", back_populates="answers")
    question: Mapped["TriviaQuestion"] = relationship("TriviaQuestion")
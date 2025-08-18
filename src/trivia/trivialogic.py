import logging
import random
import discord
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from typing import Optional, List, Tuple
from ..typing import *
from . import model


class TriviaLogic:
    def __init__(self, bot: discord.ext.commands.Bot, engine: Engine):
        self.bot = bot
        self.engine = engine

    def create_session(self, channel_id: int, creator_id: int) -> Result[str]:
        """Create a new trivia session in the given channel."""
        with Session(self.engine) as session:
            try:
                # Check if there's already an active session in this channel
                existing = session.scalar(
                    select(model.TriviaSession)
                    .where(model.TriviaSession.channel_id == channel_id)
                    .where(model.TriviaSession.state != model.TriviaSessionState.FINISHED)
                )
                
                if existing:
                    return Err("There is already an active trivia session in this channel. Use !trivia stop to end it first.")
                
                # Create new session
                trivia_session = model.TriviaSession(
                    channel_id=channel_id,
                    creator_id=creator_id,
                    state=model.TriviaSessionState.WAITING
                )
                session.add(trivia_session)
                session.commit()
                
                return Ok(f"Trivia session created! Use `!trivia next` to start the first question.")
                
            except Exception as e:
                logging.exception("Error creating trivia session")
                return Err("An error occurred while creating the trivia session.")

    def stop_session(self, channel_id: int, user_id: int) -> Result[str]:
        """Stop the trivia session in the given channel."""
        with Session(self.engine) as session:
            try:
                trivia_session = session.scalar(
                    select(model.TriviaSession)
                    .where(model.TriviaSession.channel_id == channel_id)
                    .where(model.TriviaSession.state != model.TriviaSessionState.FINISHED)
                )
                
                if not trivia_session:
                    return Err("No active trivia session found in this channel.")
                
                # Only creator can stop the session
                if trivia_session.creator_id != user_id:
                    return Err("Only the session creator can stop the trivia session.")
                
                trivia_session.state = model.TriviaSessionState.FINISHED
                trivia_session.finished_at = datetime.utcnow()
                session.commit()
                
                return Ok("Trivia session stopped.")
                
            except Exception as e:
                logging.exception("Error stopping trivia session")
                return Err("An error occurred while stopping the trivia session.")

    def next_question(self, channel_id: int) -> Result[Tuple[str, int]]:
        """Get the next random question for the trivia session."""
        with Session(self.engine) as session:
            try:
                trivia_session = session.scalar(
                    select(model.TriviaSession)
                    .where(model.TriviaSession.channel_id == channel_id)
                    .where(model.TriviaSession.state != model.TriviaSessionState.FINISHED)
                )
                
                if not trivia_session:
                    return Err("No active trivia session found in this channel.")
                
                # Get a random active question
                questions = session.scalars(
                    select(model.TriviaQuestion)
                    .where(model.TriviaQuestion.is_active == True)
                ).all()
                
                if not questions:
                    return Err("No trivia questions available. Add some questions first using `!trivia add`.")
                
                question = random.choice(questions)
                
                # Update session with current question
                trivia_session.current_question_id = question.question_id
                trivia_session.state = model.TriviaSessionState.ACTIVE
                session.commit()
                
                return Ok((question.question_text, question.question_id))
                
            except Exception as e:
                logging.exception("Error getting next question")
                return Err("An error occurred while getting the next question.")

    def answer_question(self, channel_id: int, user_id: int, answer_text: str) -> Result[str]:
        """Submit an answer to the current trivia question."""
        with Session(self.engine) as session:
            try:
                trivia_session = session.scalar(
                    select(model.TriviaSession)
                    .where(model.TriviaSession.channel_id == channel_id)
                    .where(model.TriviaSession.state == model.TriviaSessionState.ACTIVE)
                )
                
                if not trivia_session or not trivia_session.current_question_id:
                    return Err("No active question found in this channel.")
                
                # Check if user already answered this question
                existing_answer = session.scalar(
                    select(model.TriviaAnswer)
                    .where(model.TriviaAnswer.session_id == trivia_session.session_id)
                    .where(model.TriviaAnswer.question_id == trivia_session.current_question_id)
                    .where(model.TriviaAnswer.player_id == user_id)
                )
                
                if existing_answer:
                    return Err("You have already answered this question.")
                
                # Get the question
                question = session.get(model.TriviaQuestion, trivia_session.current_question_id)
                if not question:
                    return Err("Question not found.")
                
                # Check if answer is correct (case-insensitive)
                is_correct = answer_text.lower().strip() == question.correct_answer.lower().strip()
                
                # Save the answer
                trivia_answer = model.TriviaAnswer(
                    session_id=trivia_session.session_id,
                    question_id=question.question_id,
                    player_id=user_id,
                    answer_text=answer_text,
                    is_correct=is_correct
                )
                session.add(trivia_answer)
                session.commit()
                
                if is_correct:
                    return Ok(f"🎉 Correct! The answer was: {question.correct_answer}")
                else:
                    return Ok(f"❌ Incorrect. The correct answer was: {question.correct_answer}")
                
            except Exception as e:
                logging.exception("Error submitting answer")
                return Err("An error occurred while submitting your answer.")

    def add_question(self, user_id: int, question_text: str, answer: str, category: str = "custom") -> Result[str]:
        """Add a new trivia question."""
        with Session(self.engine) as session:
            try:
                if len(question_text.strip()) < 10:
                    return Err("Question must be at least 10 characters long.")
                
                if len(answer.strip()) < 1:
                    return Err("Answer cannot be empty.")
                
                question = model.TriviaQuestion(
                    question_text=question_text.strip(),
                    correct_answer=answer.strip(),
                    category=category,
                    creator_id=user_id
                )
                session.add(question)
                session.commit()
                
                return Ok(f"Question added successfully! Category: {category}")
                
            except Exception as e:
                logging.exception("Error adding question")
                return Err("An error occurred while adding the question.")

    def get_scores(self, channel_id: int) -> Result[str]:
        """Get scores for the current trivia session."""
        with Session(self.engine) as session:
            try:
                trivia_session = session.scalar(
                    select(model.TriviaSession)
                    .where(model.TriviaSession.channel_id == channel_id)
                    .where(model.TriviaSession.state != model.TriviaSessionState.FINISHED)
                )
                
                if not trivia_session:
                    return Err("No active trivia session found in this channel.")
                
                # Get scores grouped by player
                scores = session.execute(
                    select(
                        model.TriviaAnswer.player_id,
                        func.sum(model.TriviaAnswer.is_correct).label('correct_answers'),
                        func.count(model.TriviaAnswer.answer_id).label('total_answers')
                    )
                    .where(model.TriviaAnswer.session_id == trivia_session.session_id)
                    .group_by(model.TriviaAnswer.player_id)
                    .order_by(func.sum(model.TriviaAnswer.is_correct).desc())
                ).all()
                
                if not scores:
                    return Ok("No answers submitted yet.")
                
                lines = ["**Trivia Scores:**"]
                for i, (player_id, correct, total) in enumerate(scores, 1):
                    lines.append(f"{i}. <@{player_id}>: {correct}/{total} correct")
                
                return Ok("\n".join(lines))
                
            except Exception as e:
                logging.exception("Error getting scores")
                return Err("An error occurred while getting scores.")

    def list_questions(self, category: Optional[str] = None) -> Result[str]:
        """List available trivia questions."""
        with Session(self.engine) as session:
            try:
                query = select(model.TriviaQuestion).where(model.TriviaQuestion.is_active == True)
                
                if category:
                    query = query.where(model.TriviaQuestion.category == category)
                
                questions = session.scalars(query).all()
                
                if not questions:
                    if category:
                        return Ok(f"No questions found in category '{category}'.")
                    else:
                        return Ok("No questions available.")
                
                lines = [f"**Available Questions ({len(questions)} total):**"]
                for q in questions[:10]:  # Limit to first 10 to avoid spam
                    lines.append(f"• {q.question_text[:100]}{'...' if len(q.question_text) > 100 else ''} (Category: {q.category})")
                
                if len(questions) > 10:
                    lines.append(f"... and {len(questions) - 10} more questions")
                
                return Ok("\n".join(lines))
                
            except Exception as e:
                logging.exception("Error listing questions")
                return Err("An error occurred while listing questions.")
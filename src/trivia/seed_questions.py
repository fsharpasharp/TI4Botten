import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.trivia.model import TriviaQuestion
from src import models


def seed_trivia_questions():
    """Seed the database with TI4-related trivia questions."""
    
    default_questions = [
        {
            "question": "What is the maximum number of strategy cards a player can hold?",
            "answer": "1",
            "category": "rules"
        },
        {
            "question": "Which faction has the ability to build War Suns without owning the technology?",
            "answer": "The Embers of Muaat",
            "category": "factions"
        },
        {
            "question": "What is the name of the central planet in Twilight Imperium?",
            "answer": "Mecatol Rex",
            "category": "lore"
        },
        {
            "question": "How many victory points are needed to win a standard game?",
            "answer": "10",
            "category": "rules"
        },
        {
            "question": "Which faction starts the game with 2 War Suns?",
            "answer": "The Embers of Muaat",
            "category": "factions"
        },
        {
            "question": "What is the name of the precursor race that once ruled the galaxy?",
            "answer": "Lazax",
            "category": "lore"
        },
        {
            "question": "How many trade goods does the Trade strategy card give its primary user?",
            "answer": "3",
            "category": "rules"
        },
        {
            "question": "Which faction has the racial ability called 'Fragile'?",
            "answer": "The Winnu",
            "category": "factions"
        },
        {
            "question": "What planet produces the most resources in the base game?",
            "answer": "Wellon",
            "category": "planets"
        },
        {
            "question": "How many command tokens does each player start with?",
            "answer": "8",
            "category": "rules"
        },
        {
            "question": "Which faction can produce units in any system containing their units?",
            "answer": "The Arborec",
            "category": "factions"
        },
        {
            "question": "What is the maximum fleet supply in the base game without technologies?",
            "answer": "3",
            "category": "rules"
        },
        {
            "question": "Which strategy card allows you to build a PDS or Space Dock on any planet you control?",
            "answer": "Construction",
            "category": "strategy"
        },
        {
            "question": "What faction has the ability to ignore planetary shields?",
            "answer": "The L1Z1X Mindnet",
            "category": "factions"
        },
        {
            "question": "How many plastic pieces does a standard TI4 game contain?",
            "answer": "354",
            "category": "components"
        }
    ]
    
    engine = create_engine("sqlite:///app.db")
    models.Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        for q_data in default_questions:
            # Check if question already exists
            existing = session.query(TriviaQuestion).filter_by(
                question_text=q_data["question"]
            ).first()
            
            if not existing:
                question = TriviaQuestion(
                    question_text=q_data["question"],
                    correct_answer=q_data["answer"],
                    category=q_data["category"],
                    creator_id=None  # System-created questions
                )
                session.add(question)
        
        session.commit()
        print(f"Seeded {len(default_questions)} trivia questions")


if __name__ == "__main__":
    seed_trivia_questions()
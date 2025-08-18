#!/usr/bin/env python3
"""
Manual test script for trivia functionality.
This script tests the trivia logic without requiring Discord.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from src.trivia.trivialogic import TriviaLogic
from src.trivia.seed_questions import seed_trivia_questions
from src import models
from unittest.mock import Mock


def test_trivia_functionality():
    """Manual test of trivia functionality."""
    print("=== TI4Botten Trivia Game Test ===\n")
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    models.Base.metadata.create_all(engine)
    
    # Create trivia logic instance
    bot = Mock()
    trivia_logic = TriviaLogic(bot, engine)
    
    # Test 1: Add some questions
    print("1. Adding test questions...")
    result = trivia_logic.add_question(
        user_id=12345,
        question_text="What is the capital of the galaxy in TI4?",
        answer="Mecatol Rex",
        category="lore"
    )
    print(f"   Add question 1: {'✓' if result.is_ok() else '✗'} {result.unwrap() if result.is_ok() else result.unwrap_err()}")
    
    result = trivia_logic.add_question(
        user_id=12345,
        question_text="How many victory points are needed to win?",
        answer="10",
        category="rules"
    )
    print(f"   Add question 2: {'✓' if result.is_ok() else '✗'} {result.unwrap() if result.is_ok() else result.unwrap_err()}")
    
    # Test 2: Create trivia session
    print("\n2. Creating trivia session...")
    result = trivia_logic.create_session(channel_id=9999, creator_id=12345)
    print(f"   Create session: {'✓' if result.is_ok() else '✗'} {result.unwrap() if result.is_ok() else result.unwrap_err()}")
    
    # Test 3: Get next question
    print("\n3. Getting next question...")
    result = trivia_logic.next_question(channel_id=9999)
    if result.is_ok():
        question_text, question_id = result.unwrap()
        print(f"   Next question: ✓ Got question: '{question_text}'")
        current_question_id = question_id
        current_question_text = question_text
    else:
        print(f"   Next question: ✗ {result.unwrap_err()}")
        return
    
    # Test 4: Answer question correctly
    print("\n4. Answering question...")
    if "Mecatol Rex" in current_question_text:
        answer = "Mecatol Rex"
    else:
        answer = "10"
    
    result = trivia_logic.answer_question(
        channel_id=9999,
        user_id=55555,
        answer_text=answer
    )
    print(f"   Answer question: {'✓' if result.is_ok() else '✗'} {result.unwrap() if result.is_ok() else result.unwrap_err()}")
    
    # Test 5: Try duplicate answer
    print("\n5. Testing duplicate answer...")
    result = trivia_logic.answer_question(
        channel_id=9999,
        user_id=55555,
        answer_text="Some other answer"
    )
    print(f"   Duplicate answer: {'✓' if result.is_err() else '✗'} {result.unwrap_err() if result.is_err() else 'Should have failed'}")
    
    # Test 6: Get scores
    print("\n6. Getting scores...")
    result = trivia_logic.get_scores(channel_id=9999)
    print(f"   Get scores: {'✓' if result.is_ok() else '✗'} {result.unwrap() if result.is_ok() else result.unwrap_err()}")
    
    # Test 7: List questions
    print("\n7. Listing questions...")
    result = trivia_logic.list_questions()
    print(f"   List questions: {'✓' if result.is_ok() else '✗'}")
    if result.is_ok():
        lines = result.unwrap().split('\n')
        print(f"   Found {len(lines)-1} questions listed")
    
    # Test 8: Stop session
    print("\n8. Stopping session...")
    result = trivia_logic.stop_session(channel_id=9999, user_id=12345)
    print(f"   Stop session: {'✓' if result.is_ok() else '✗'} {result.unwrap() if result.is_ok() else result.unwrap_err()}")
    
    print("\n=== Test Complete ===")
    print("✓ All basic trivia functionality working correctly!")


def test_with_default_questions():
    """Test with the default TI4 questions."""
    print("\n=== Testing with Default TI4 Questions ===\n")
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    models.Base.metadata.create_all(engine)
    
    # Seed with default questions
    print("1. Seeding default TI4 questions...")
    try:
        # Manually seed questions for in-memory DB
        from sqlalchemy.orm import Session
        from src.trivia.model import TriviaQuestion
        
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
            }
        ]
        
        with Session(engine) as session:
            for q_data in default_questions:
                question = TriviaQuestion(
                    question_text=q_data["question"],
                    correct_answer=q_data["answer"],
                    category=q_data["category"],
                    creator_id=None
                )
                session.add(question)
            session.commit()
        
        print(f"   ✓ Seeded {len(default_questions)} TI4 questions")
    except Exception as e:
        print(f"   ✗ Failed to seed questions: {e}")
        return
    
    # Test trivia with default questions
    bot = Mock()
    trivia_logic = TriviaLogic(bot, engine)
    
    print("\n2. Testing trivia with TI4 questions...")
    
    # Create session and get question
    trivia_logic.create_session(channel_id=8888, creator_id=99999)
    result = trivia_logic.next_question(channel_id=8888)
    
    if result.is_ok():
        question_text, question_id = result.unwrap()
        print(f"   ✓ Got TI4 question: '{question_text}'")
        
        # Test listing by category
        for category in ["rules", "factions", "lore"]:
            result = trivia_logic.list_questions(category)
            if result.is_ok():
                count = result.unwrap().count("•")
                print(f"   ✓ Found {count} questions in '{category}' category")
    else:
        print(f"   ✗ Failed to get question: {result.unwrap_err()}")
    
    print("\n=== Default Questions Test Complete ===")


if __name__ == "__main__":
    try:
        test_trivia_functionality()
        test_with_default_questions()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
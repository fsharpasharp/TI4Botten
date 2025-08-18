import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.trivia.model import TriviaSession, TriviaQuestion, TriviaAnswer, TriviaSessionState
from src.trivia.trivialogic import TriviaLogic
from src.models import Base
from unittest.mock import Mock


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def trivia_logic(engine):
    """Create a TriviaLogic instance for testing."""
    bot = Mock()
    return TriviaLogic(bot, engine)


def test_create_session(trivia_logic, engine):
    """Test creating a new trivia session."""
    result = trivia_logic.create_session(channel_id=12345, creator_id=67890)
    
    assert result.is_ok()
    assert "Trivia session created" in result.unwrap()
    
    # Verify session was created in database
    with Session(engine) as session:
        trivia_session = session.query(TriviaSession).filter_by(channel_id=12345).first()
        assert trivia_session is not None
        assert trivia_session.creator_id == 67890
        assert trivia_session.state == TriviaSessionState.WAITING


def test_create_duplicate_session(trivia_logic, engine):
    """Test that creating a duplicate session fails."""
    # Create first session
    result1 = trivia_logic.create_session(channel_id=12345, creator_id=67890)
    assert result1.is_ok()
    
    # Try to create second session in same channel
    result2 = trivia_logic.create_session(channel_id=12345, creator_id=11111)
    assert result2.is_err()
    assert "already an active trivia session" in result2.unwrap_err()


def test_add_question(trivia_logic, engine):
    """Test adding a new trivia question."""
    result = trivia_logic.add_question(
        user_id=12345,
        question_text="What is the capital of France?",
        answer="Paris",
        category="geography"
    )
    
    assert result.is_ok()
    assert "Question added successfully" in result.unwrap()
    
    # Verify question was added to database
    with Session(engine) as session:
        question = session.query(TriviaQuestion).filter_by(
            question_text="What is the capital of France?"
        ).first()
        assert question is not None
        assert question.correct_answer == "Paris"
        assert question.category == "geography"
        assert question.creator_id == 12345


def test_add_invalid_question(trivia_logic, engine):
    """Test adding invalid questions."""
    # Too short question
    result1 = trivia_logic.add_question(12345, "Short?", "Answer")
    assert result1.is_err()
    assert "at least 10 characters" in result1.unwrap_err()
    
    # Empty answer
    result2 = trivia_logic.add_question(12345, "Valid question text?", "")
    assert result2.is_err()
    assert "Answer cannot be empty" in result2.unwrap_err()


def test_next_question_no_session(trivia_logic, engine):
    """Test getting next question when no session exists."""
    result = trivia_logic.next_question(channel_id=12345)
    assert result.is_err()
    assert "No active trivia session" in result.unwrap_err()


def test_next_question_no_questions(trivia_logic, engine):
    """Test getting next question when no questions exist."""
    # Create session first
    trivia_logic.create_session(channel_id=12345, creator_id=67890)
    
    result = trivia_logic.next_question(channel_id=12345)
    assert result.is_err()
    assert "No trivia questions available" in result.unwrap_err()


def test_next_question_with_questions(trivia_logic, engine):
    """Test getting next question when questions exist."""
    # Add a question first
    trivia_logic.add_question(12345, "Test question?", "Test answer")
    
    # Create session
    trivia_logic.create_session(channel_id=12345, creator_id=67890)
    
    result = trivia_logic.next_question(channel_id=12345)
    assert result.is_ok()
    question_text, question_id = result.unwrap()
    assert question_text == "Test question?"
    assert isinstance(question_id, int)


def test_answer_question(trivia_logic, engine):
    """Test answering a trivia question."""
    # Setup: Add question, create session, get next question
    trivia_logic.add_question(12345, "Test question?", "Correct Answer")
    trivia_logic.create_session(channel_id=12345, creator_id=67890)
    trivia_logic.next_question(channel_id=12345)
    
    # Test correct answer
    result = trivia_logic.answer_question(
        channel_id=12345,
        user_id=99999,
        answer_text="Correct Answer"
    )
    assert result.is_ok()
    assert "Correct!" in result.unwrap()
    
    # Test duplicate answer from same user
    result2 = trivia_logic.answer_question(
        channel_id=12345,
        user_id=99999,
        answer_text="Another answer"
    )
    assert result2.is_err()
    assert "already answered" in result2.unwrap_err()


def test_answer_question_incorrect(trivia_logic, engine):
    """Test answering a trivia question incorrectly."""
    # Setup
    trivia_logic.add_question(12345, "Test question?", "Correct Answer")
    trivia_logic.create_session(channel_id=12345, creator_id=67890)
    trivia_logic.next_question(channel_id=12345)
    
    # Test incorrect answer
    result = trivia_logic.answer_question(
        channel_id=12345,
        user_id=99999,
        answer_text="Wrong Answer"
    )
    assert result.is_ok()
    assert "Incorrect" in result.unwrap()
    assert "Correct Answer" in result.unwrap()


def test_get_scores_no_session(trivia_logic, engine):
    """Test getting scores when no session exists."""
    result = trivia_logic.get_scores(channel_id=12345)
    assert result.is_err()
    assert "No active trivia session" in result.unwrap_err()


def test_get_scores_no_answers(trivia_logic, engine):
    """Test getting scores when no answers have been submitted."""
    trivia_logic.create_session(channel_id=12345, creator_id=67890)
    
    result = trivia_logic.get_scores(channel_id=12345)
    assert result.is_ok()
    assert "No answers submitted" in result.unwrap()


def test_stop_session(trivia_logic, engine):
    """Test stopping a trivia session."""
    # Create session
    trivia_logic.create_session(channel_id=12345, creator_id=67890)
    
    # Stop session by creator
    result = trivia_logic.stop_session(channel_id=12345, user_id=67890)
    assert result.is_ok()
    assert "Trivia session stopped" in result.unwrap()
    
    # Verify session is finished
    with Session(engine) as session:
        trivia_session = session.query(TriviaSession).filter_by(channel_id=12345).first()
        assert trivia_session.state == TriviaSessionState.FINISHED


def test_stop_session_wrong_user(trivia_logic, engine):
    """Test that only the creator can stop a session."""
    # Create session
    trivia_logic.create_session(channel_id=12345, creator_id=67890)
    
    # Try to stop session with different user
    result = trivia_logic.stop_session(channel_id=12345, user_id=11111)
    assert result.is_err()
    assert "Only the session creator" in result.unwrap_err()
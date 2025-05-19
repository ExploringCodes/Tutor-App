

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import List,Optional
from datetime import datetime
from .database.session import SessionLocal, Base, engine
from .database.models import Quiz0, Subject, Topic, Subtopic, MCQ, User, UserSelection, QuizAttempt, QuizAnswer, QuizScore,UserProgress,Diagram,Quiz1,Quiz1Attempt,Quiz1Score
from .schemas.models import SubjectBase, TopicBase, SubtopicBase, MCQBase
from sqlalchemy.sql import func
from pydantic import BaseModel

from fastapi import Request
from starlette.middleware.sessions import SessionMiddleware

import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse


from fastapi.middleware.cors import CORSMiddleware


from .database.models import Subject, Topic, Subtopic, User, Explain
import faiss
from sentence_transformers import SentenceTransformer
from pylatexenc.latex2text import LatexNodes2Text

import base64  # Add this import for base64 encoding
import json 

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="AITutor Quiz Webapp")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "quiz-app-se1ssion-secret-key"),
    same_site="none",  # 👈 important for frontend-backend on different ports
    https_only=False  # 👈 ensure False for localhost
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

##########################login stuff 





import secrets
from urllib.parse import urlencode
import requests
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .database.session import SessionLocal, Base, engine
from .database.models import User

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Configuration
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/google/callback"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SECRET_KEY = secrets.token_hex(32)

# Initialize FastAPI app
app = FastAPI(title="FastAPI Google OAuth")

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=60*60,
    same_site="lax",
    https_only=False
)

# Models
class UserModel(BaseModel):
    id: Optional[int] = None
    email: str
    name: str
    picture: Optional[str] = None

# Routes
@app.get("/api/user")
async def get_user(request: Request):
    user = request.session.get("user")
    return {"user": user}

@app.get("/login")
async def login(request: Request):
    state = secrets.token_hex(16)
    request.session["oauth_state"] = state
    
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(auth_url)

@app.get("/auth/google/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    state = request.session.get("oauth_state")
    state_param = request.query_params.get("state")
    if state and state_param and state != state_param:
        print(f"Warning: State mismatch. Expected {state}, got {state_param}")
    
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    if not token_response.ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to retrieve access token"
        )
    
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    
    user_response = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if not user_response.ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to retrieve user information"
        )
    
    user_info = user_response.json()
    
    # Database session
    db: Session = SessionLocal()
    try:
        # Check if user exists, if not create new user
        db_user = db.query(User).filter(User.email == user_info.get("email")).first()
        if not db_user:
            db_user = User(email=user_info.get("email"))
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        
        user = UserModel(
            id=db_user.id,
            email=user_info.get("email", ""),
            name=user_info.get("name", ""),
            picture=user_info.get("picture", "")
        )
        
        request.session["user"] = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
        
        request.session.pop("oauth_state", None)
        
        return RedirectResponse(url="http://localhost:3000")
    finally:
        db.close()

@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return {"message": "Logged out successfully"}







#######################
class Quiz0Response(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    category: str

    class Config:
        orm_mode = True



# Request model for submitting answers
class AnswerSubmission(BaseModel):
    question_id: int
    selected_option: str

class QuizSubmission(BaseModel):
    answers: List[AnswerSubmission]



# Updated MCQResponse model to include correct_option
class MCQResponse(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    hardness_level: int
    correct_option: str
    explanation: Optional[str] = None
    class Config:
        from_attributes = True


# Response model for practice quiz question
class PracticeQuizQuestionResponse(BaseModel):
    question: Optional[MCQResponse] = None
    hardness_level: int
    message: Optional[str] = None

    class Config:
        from_attributes = True

# Request model for submitting practice quiz answer
class PracticeQuizAnswerSubmission(BaseModel):
    question_id: int
    is_correct: bool
    current_hardness_level: int
    questions_tried: int
# # Model for selecting subject, topic, subtopic
# class SelectionRequest(BaseModel):
#     name: str
# Model for selecting subject, topic, and subtopic
class SelectionRequest(BaseModel):
    subject: str  # Name of the subject
    topic: str    # Name of the topic under the selected subject
    subtopic: Optional[str] = None  # Subtopic is optional now


# New QuizQuestionResponse schema
class QuizQuestionResponse(BaseModel):
    question: Optional[MCQResponse] = None
    hardness_level: int
    message: Optional[str] = None
    attempt_id: Optional[int] = None
    score:Optional[int]=None,
    questions_tried:Optional[int]=None
    class Config:
        from_attributes = True

# New QuizAnswerSubmission schema
class QuizAnswerSubmission(BaseModel):
    question_id: int
    is_correct: bool
    current_hardness_level: int
    questions_tried: int
    attempt_id: int
# Request model for user input
class ExplainQuery(BaseModel):
    query: str
    is_initial: Optional[bool] = False

# Response model for explain (only answer)
class ExplainResponse(BaseModel):
    answer: str
    image: Optional[str] = None  # Base64-encoded image string (or None if no image)
    total:Optional[int]=None
    current:Optional[int]=None
    initial_response: Optional[List[str]] = None




# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}

# Endpoint to fetch all subjects
@app.get("/subjects/", response_model=List[SubjectBase])
async def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    if not subjects:
        raise HTTPException(status_code=404, detail="No subjects found")
    return subjects

# Endpoint to fetch topics for a subject
@app.get("/{subject}/topics/", response_model=List[TopicBase])
async def get_topics(subject: str, db: Session = Depends(get_db)):
    subject_obj = db.query(Subject).filter(Subject.name == subject).first()
    if not subject_obj:
        raise HTTPException(status_code=404, detail=f"Subject {subject} not found")
    topics = db.query(Topic).filter(Topic.subject_id == subject_obj.id).all()
    if not topics:
        raise HTTPException(status_code=404, detail=f"No topics found for subject {subject}")
    return topics

# Endpoint to fetch subtopics for a topic under a subject
@app.get("/{subject}/{topic}/subtopics/", response_model=List[SubtopicBase])
async def get_subtopics(subject: str, topic: str, db: Session = Depends(get_db)):
    subject_obj = db.query(Subject).filter(Subject.name == subject).first()
    if not subject_obj:
        raise HTTPException(status_code=404, detail=f"Subject {subject} not found")
    topic_obj = db.query(Topic).filter(
        Topic.name == topic,
        Topic.subject_id == subject_obj.id
    ).first()
    if not topic_obj:
        raise HTTPException(status_code=404, detail=f"Topic {topic} not found in subject {subject}")
    subtopics = db.query(Subtopic).filter(Subtopic.topic_id == topic_obj.id).all()
    if not subtopics:
        raise HTTPException(status_code=404, detail=f"No subtopics found for topic {topic}")
    return subtopics



@app.post("/quiz1/", response_model=QuizQuestionResponse)
async def quiz1(
    submission: Optional[QuizAnswerSubmission] = None,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    # Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")

    hardness_level = 1
    attempt_id = None

    if submission:
        # Validate question and attempt
        question = db.query(MCQ).filter(MCQ.id == submission.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question ID {submission.question_id} not found")

        attempt = db.query(Quiz1Attempt).filter(Quiz1Attempt.id == submission.attempt_id, Quiz1Attempt.user_id == user_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail=f"Attempt ID {submission.attempt_id} not found")
        attempt_id = submission.attempt_id

        # Record quiz answer
        quiz_answer = Quiz1(
            user_id=user_id,
            attempt_id=submission.attempt_id,
            question_id=submission.question_id,
            hardness_level=submission.current_hardness_level,
            is_correct=submission.is_correct,
            user_answer=question.correct_option if submission.is_correct else "incorrect",
            correct_answer=question.correct_option
        )
        db.add(quiz_answer)
        db.commit()

        # Adjust hardness level
        hardness_level = submission.current_hardness_level
        if submission.is_correct:
            hardness_level = min(hardness_level + 1, 10)
        else:
            hardness_level = max(hardness_level - 1, 1)

        # Check if quiz is complete (10 questions)
        question_number = submission.questions_tried
        if question_number >= 10:
            answers = db.query(Quiz1).filter(Quiz1.attempt_id == submission.attempt_id).all()
            total_correct = sum(1 for ans in answers if ans.is_correct)
            total_questions = len(answers)
            score_percentage = (total_correct / total_questions) * 100 if total_questions > 0 else 0

            quiz_score = Quiz1Score(
                attempt_id=submission.attempt_id,
                total_correct=total_correct,
                total_questions=total_questions,
                score_percentage=score_percentage,
                student_level=hardness_level
            )
            db.add(quiz_score)
            attempt.completed_at = datetime.utcnow()
            db.commit()

            return QuizQuestionResponse(
                hardness_level=hardness_level,
                message="You have completed the Quiz1! Check your scores.",
                attempt_id=submission.attempt_id
            )
        
        attempt_id = submission.attempt_id
    else:
        # Create new quiz attempt
        quiz_attempt = Quiz1Attempt(
            user_id=user_id
        )
        db.add(quiz_attempt)
        db.commit()
        db.refresh(quiz_attempt)
        attempt_id = quiz_attempt.id

    # Get answered question IDs for this attempt
    answered_question_ids = db.query(Quiz1.question_id).filter(Quiz1.attempt_id == attempt_id).all()
    answered_question_ids = [qid for (qid,) in answered_question_ids]

    # Try to find a question by randomly selecting subject, topic, and subtopic
    next_question = None
    max_attempts = 1000  # Prevent infinite loop
    attempt_count = 0

    while not next_question and attempt_count < max_attempts:
        # Randomly select subject
        subject = db.query(Subject).order_by(func.random()).first()
        if not subject:
            raise HTTPException(status_code=404, detail="No subjects available")

        # Randomly select topic under the subject
        topic = db.query(Topic).filter(Topic.subject_id == subject.id).order_by(func.random()).first()
        if not topic:
            attempt_count += 1
            continue

        # Randomly select subtopic under the topic
        subtopic = db.query(Subtopic).filter(Subtopic.topic_id == topic.id).order_by(func.random()).first()
        if not subtopic:
            attempt_count += 1
            continue

        # Try to find a question at the current hardness level
        next_question = (
            db.query(MCQ)
            .filter(
                MCQ.subtopic_id == subtopic.id,
                MCQ.hardness_level == hardness_level,
                ~MCQ.id.in_(answered_question_ids)
            )
            .order_by(func.random())
            .first()
        )
        attempt_count += 1

    # If no question found after max attempts
    if not next_question:
        return QuizQuestionResponse(
            hardness_level=hardness_level,
            message="No questions available at the current difficulty level. Quiz1 completed!",
            attempt_id=attempt_id
        )

    return QuizQuestionResponse(
        question=MCQResponse.from_orm(next_question),
        hardness_level=hardness_level,
        attempt_id=attempt_id
    )


# Endpoint to select subject, topic, and subtopic in one request
@app.post("/select/")
async def select_subject_topic_subtopic(
    selection: SelectionRequest,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")

    # Fetch the subject
    subject = db.query(Subject).filter(Subject.name == selection.subject).first()
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject {selection.subject} not found")

    # Fetch the topic related to the subject
    topic = db.query(Topic).filter(Topic.name == selection.topic, Topic.subject_id == subject.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {selection.topic} not found under subject {selection.subject}")

    # Check if subtopic is provided
    subtopic_id = None
    if selection.subtopic:
        # Fetch the subtopic related to the topic
        subtopic = db.query(Subtopic).filter(Subtopic.name == selection.subtopic, Subtopic.topic_id == topic.id).first()
        if not subtopic:
            raise HTTPException(status_code=404, detail=f"Subtopic {selection.subtopic} not found under topic {selection.topic}")
        subtopic_id = subtopic.id

    # Always create a new entry in the UserSelection table
    user_selection = UserSelection(
        user_id=user_id,
        subject_id=subject.id,
        topic_id=topic.id,
        subtopic_id=subtopic_id  # subtopic_id can be None if no subtopic was provided
    )
    db.add(user_selection)
    db.commit()
    db.refresh(user_selection)
    
    return {"message": f"Selected subject: {selection.subject}, topic: {selection.topic}, subtopic: {selection.subtopic if selection.subtopic else 'None'}", "selection_id": user_selection.id}

@app.post("/{subject}/{topic}/{subtopic}/quiz/", response_model=QuizQuestionResponse)
async def quiz(
    subject: str,
    topic: str,
    subtopic: str,
    submission: Optional[QuizAnswerSubmission] = None,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    # Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")

    # Validate subject, topic, subtopic
    subject_obj = db.query(Subject).filter(Subject.name == subject).first()
    if not subject_obj:
        raise HTTPException(status_code=404, detail=f"Subject {subject} not found")
    
    topic_obj = db.query(Topic).filter(Topic.name == topic, Topic.subject_id == subject_obj.id).first()
    if not topic_obj:
        raise HTTPException(status_code=404, detail=f"Topic {topic} not found in subject {subject}")
    
    subtopic_obj = db.query(Subtopic).filter(Subtopic.name == subtopic, Subtopic.topic_id == topic_obj.id).first()
    if not subtopic_obj:
        raise HTTPException(status_code=404, detail=f"Subtopic {subtopic} not found in topic {topic}")

    hardness_level = db.query(Quiz1Score).filter(Quiz1Score.attempt_id == db.query(Quiz1Attempt).filter(Quiz1Attempt.user_id == user_id).order_by(Quiz1Attempt.started_at.desc()).first().id).first().student_level if db.query(Quiz1Score).filter(Quiz1Score.attempt_id == db.query(Quiz1Attempt).filter(Quiz1Attempt.user_id == user_id).order_by(Quiz1Attempt.started_at.desc()).first().id).first() else 5
    attempt_id = None
    score = 0
    questions_tried = 0
    # Check for existing incomplete attempt
    last_attempt = (
        db.query(QuizAttempt)
        .join(UserSelection, QuizAttempt.selection_id == UserSelection.id)
        .filter(
            UserSelection.user_id == user_id,
            UserSelection.subject_id == subject_obj.id,
            UserSelection.topic_id == topic_obj.id,
            UserSelection.subtopic_id == subtopic_obj.id,
            QuizAttempt.completed_at == None
        )
        .order_by(QuizAttempt.started_at.desc())
        .first()
    )

    if last_attempt and not submission:
        # Resume incomplete attempt
        attempt_id = last_attempt.id
        # Get questions tried and score
        quiz_answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt_id).all()
        questions_tried = len(quiz_answers)
        score = sum(1 for ans in quiz_answers if ans.is_correct)
        # Get the latest hardness level from the last answer
        last_answer = (
            db.query(QuizAnswer)
            .filter(QuizAnswer.attempt_id == attempt_id)
            .order_by(QuizAnswer.id.desc())
            .first()
        )
        if last_answer:
            # Fetch the submission to determine hardness level
            last_submission = db.query(QuizAnswer).filter(
                QuizAnswer.attempt_id == attempt_id,
                QuizAnswer.question_id == last_answer.question_id
            ).first()
            hardness_level = db.query(MCQ.hardness_level).join(QuizAnswer, MCQ.id == QuizAnswer.question_id).filter(QuizAnswer.attempt_id == attempt_id).order_by(QuizAnswer.id.desc()).first()[0] if quiz_answers else 5
            
            
            if last_submission.is_correct:
                hardness_level = min(hardness_level + 1, 10)
            else:
                hardness_level = max(hardness_level - 1, 1)
    
    elif submission:
        # Validate question and attempt
        question = db.query(MCQ).filter(MCQ.id == submission.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question ID {submission.question_id} not found")

        attempt = db.query(QuizAttempt).filter(QuizAttempt.id == submission.attempt_id, QuizAttempt.user_id == user_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail=f"Attempt ID {submission.attempt_id} not found")
        attempt_id = submission.attempt_id

        # Record quiz answer
        question_number = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == submission.attempt_id).count() + 1
        quiz_type = "quiz2" if question_number <= 5 else "quiz3"

        quiz_answer = QuizAnswer(
            attempt_id=submission.attempt_id,
            quiz_type=quiz_type,
            question_id=submission.question_id,
            user_answer=question.correct_option if submission.is_correct else "incorrect",
            correct_answer=question.correct_option,
            is_correct=submission.is_correct
        )
        db.add(quiz_answer)
        db.commit()

        # Adjust hardness level
        hardness_level = submission.current_hardness_level
        if submission.is_correct:
            hardness_level = min(hardness_level + 1, 10)
        else:
            hardness_level = max(hardness_level - 1, 1)
            
            
        # Update score and questions tried
        quiz_answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt_id).all()
        questions_tried = len(quiz_answers)
        score = sum(1 for ans in quiz_answers if ans.is_correct)

        # Check if quiz is complete (10 questions)
        if question_number >= 10:
            quiz2_answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == submission.attempt_id, QuizAnswer.quiz_type == "quiz2").all()
            quiz3_answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == submission.attempt_id, QuizAnswer.quiz_type == "quiz3").all()
            quiz2_correct = sum(1 for ans in quiz2_answers if ans.is_correct)
            quiz3_correct = sum(1 for ans in quiz3_answers if ans.is_correct)
            quiz2_score = (quiz2_correct / 5) * 100 if quiz2_answers else 0
            quiz3_score = (quiz3_correct / 5) * 100 if quiz3_answers else 0

            quiz_score = QuizScore(
                attempt_id=submission.attempt_id,
                quiz2_correct=quiz2_correct,
                quiz3_correct=quiz3_correct,
                total_correct=quiz2_correct + quiz3_correct,
                quiz2_score=quiz2_score,
                quiz3_score=quiz3_score
            )
            db.add(quiz_score)
            attempt.completed_at = datetime.utcnow()
            db.commit()

            return QuizQuestionResponse (
                hardness_level=hardness_level,
                message="You have completed the quiz! Check your scores.",
                attempt_id=submission.attempt_id,
                score=score,
                questions_tried=questions_tried
            )
        
        attempt_id = submission.attempt_id
    else:
        print("I am here ")
        # Create new user selection and quiz attempt
        user_selection = UserSelection(
            user_id=user_id,
            subject_id=subject_obj.id,
            topic_id=topic_obj.id,
            subtopic_id=subtopic_obj.id
        )
        db.add(user_selection)
        db.commit()
        db.refresh(user_selection)

        quiz_attempt = QuizAttempt(
            user_id=user_id,
            selection_id=user_selection.id
        )
        db.add(quiz_attempt)
        db.commit()
        db.refresh(quiz_attempt)
        attempt_id = quiz_attempt.id
        print("after new attempt id created")

    # Get answered question IDs
    answered_question_ids = db.query(QuizAnswer.question_id).filter(QuizAnswer.attempt_id == attempt_id).all()
    answered_question_ids = [qid for (qid,) in answered_question_ids]

    # Try to find a question at the current hardness level
    next_question = (
        db.query(MCQ)
        .filter(
            MCQ.subtopic_id == subtopic_obj.id,
            MCQ.hardness_level == hardness_level,
            ~MCQ.id.in_(answered_question_ids)
        )
        .order_by(func.random())
        .first()
    )

   # If no question found, try random search at same level (ignoring answered questions)
    if not next_question:
        next_question = (
            db.query(MCQ)
            .filter(
                MCQ.subtopic_id == subtopic_obj.id,
                MCQ.hardness_level == hardness_level
            )
            .order_by(func.random())
            .first()
        )
        # If still no question found, quiz is complete
    if not next_question:
        return QuizQuestionResponse(
            hardness_level=hardness_level,
            message="No questions available \n Select Another Item",
            attempt_id=attempt_id,
            score=score,
            questions_tried=questions_tried
        )

    return QuizQuestionResponse(
        question=MCQResponse.from_orm(next_question),
        hardness_level=hardness_level,
        attempt_id=attempt_id,
        score=score,
        questions_tried=questions_tried
    )

# Updated function to handle various LaTeX commands in the first line
def get_image_data_from_chunk(chunk: str, subtopic_id: int, db: Session) -> Optional[str]:
    """
    Fetches and encodes image data from the Diagram table if the chunk contains 'image description'.
    Uses the raw first line of the chunk, cleans LaTeX commands (\section, \subsection, \textbf),
    and performs a substring search against Diagram.description.
    
    Args:
        chunk (str): The chunk text to search for image description.
        subtopic_id (int): The ID of the subtopic to query diagrams for.
        db (Session): SQLAlchemy session for database operations.
    
    Returns:
        Optional[str]: Base64-encoded image data, or None if no image is found.
    """
    image_data = None
    if isinstance(chunk, str) and "image description".lower() in chunk.lower():
        # Split the chunk into lines and get the first line
        lines = chunk.split('\n')
        if not lines:
            return None  # No lines in the chunk

        first_line = lines[0].strip()  # e.g., "\subsection*{Union of Sets}" or "\section*{Introduction}" or "\textbf{Key Concepts}"

        # Clean the first line by removing LaTeX commands (\section, \subsection, \textbf) and braces
        description = first_line
        # Remove common LaTeX commands and their variants (with or without *)
        for cmd in ["\\section*", "\\section", "\\subsection*", "\\subsection", "\\textbf"]:
            description = description.replace(cmd, "")
        # Remove braces and any remaining LaTeX markup
        description = description.replace("{", "").replace("}", "").strip()  # e.g., "Union of Sets"

        if description:
            # Query the Diagram table for an image where the description contains the cleaned first line (case-insensitive)
            diagram = db.query(Diagram).filter(
                Diagram.subtopic_id == subtopic_id,
                func.lower(Diagram.description).contains(func.lower(description))
            ).first()
            if diagram and diagram.image_content:
                # Encode the image content as base64 for the frontend
                image_data = base64.b64encode(diagram.image_content).decode('utf-8')
    return image_data

# NEW: Modified /explains/ endpoint to use UserProgress table instead of session
@app.post("/{subject}/{topic}/{subtopic}/explains/", response_model=ExplainResponse)
async def post_explain(
    subject: str,
    topic: str,
    subtopic: str,
    explain_query: ExplainQuery,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    # Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")

    # Validate subject, topic, and subtopic
    subject_obj = db.query(Subject).filter(Subject.name == subject).first()
    if not subject_obj:
        raise HTTPException(status_code=404, detail=f"Subject {subject} not found")
    
    topic_obj = db.query(Topic).filter(
        Topic.name == topic,
        Topic.subject_id == subject_obj.id
    ).first()
    if not topic_obj:
        raise HTTPException(status_code=404, detail=f"Topic {topic} not found in subject {subject}")
    
    subtopic_obj = db.query(Subtopic).filter(
        Subtopic.name == subtopic,
        Subtopic.topic_id == topic_obj.id
    ).first()
    if not subtopic_obj:
        raise HTTPException(status_code=404, detail=f"Subtopic {subtopic} not found in topic {topic}")

    # Fetch explain record
    explain = db.query(Explain).filter(Explain.subtopic_id == subtopic_obj.id).first()
    if not explain:
        raise HTTPException(status_code=404, detail=f"No explanations found for subtopic {subtopic}")

    # Load chunks
    chunks = explain.chunks
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks available for this subtopic")

    # NEW: Fetch or initialize user progress from UserProgress table
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.subtopic_id == subtopic_obj.id
    ).first()
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            subtopic_id=subtopic_obj.id,
            chunk_index=0,
            chat_memory=[]
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    # NEW: Use chunk_index and chat_memory from UserProgress
    chunk_index = progress.chunk_index
    chat_memory = progress.chat_memory
    # Handle query
    query = explain_query.query.lower()
    context = None
    
    
    
    
      # NEW: Handle initial "explain" query with non-empty chat_memory
    if query == "explain" and chat_memory and explain_query.is_initial:
        # Return all previous answers from chat_memory in initial_response
        previous_answers = [pair['answer'] for pair in chat_memory]
        return ExplainResponse(
            answer="",  # No new answer for initial response
            image=None,
            initial_response=previous_answers
        )

    if query == "explain":
        if subject =="English":
            query="please explain in easier english and easily"
        else:
            query = "please explain more easily and elaborately"
        context = chunks[chunk_index]
            # After determining context and chunk_index
        selected_chunk =chunks[chunk_index]
                
    elif query == "continue":
        chunk_index += 1
        if chunk_index >= len(chunks):
            #chunk_index = -1
            #progress.chunk_index = chunk_index
            #db.commit()
            return ExplainResponse(answer="Congratulations, you have mastered the topic!")
        query = "Explain the context easy fun way"
        context = chunks[chunk_index]
            # After determining context and chunk_index
        selected_chunk =chunks[chunk_index]
    elif query == "refresh":
        chunk_index = 0 # Start from chunk_index = 1
        progress.chunk_index = chunk_index
        chat_memory=[]
        progress.chat_memory = []  # Clear chat_memory
        db.commit()
        query =  "Explain the context easy fun way"
        context = chunks[chunk_index]
        selected_chunk = chunks[chunk_index]
    else:
        # Custom query with FAISS
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(chunks, convert_to_numpy=True)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        query_embedding = model.encode([query], convert_to_numpy=True)
        top_k = 3
        distances, indices = index.search(query_embedding, top_k)
        context = [chunks[idx] for idx in indices[0]]
        selected_chunk=None




    # Fetch image data using the new function
    image_data = get_image_data_from_chunk(selected_chunk, subtopic_obj.id, db)


    # Setup Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")

    # NEW: Prepare memory_text from UserProgress.chat_memory
    memory_text = "\n\n".join([
        f"User: {pair['question']}\nAssistant: {pair['answer']}"
        for pair in chat_memory[-30:]
    ]) if chat_memory else "No prior conversation."

    # Prepare prompt (unchanged)
    prompt = f"""
You are an educational assistant tasked with creating a step-by-step learning guide 
for a user. 
your sentences should be simple.
Use the memory of recent conversations to personalize the response and 
incorporate any relevant context to enhance clarity.

user_input:
{query}
Recent Chat History:
{memory_text}

Relevant Text:
{context if context else chunks}

Instructions:
1. Explain the Relevant Text in fun and interesting ways
2. Make the Explanation engaging , use story if necessary
3. if necessary refer to chat history

"""
    if subject !="English":
        prompt=prompt+"\n"+'''
        4. **Text**: Use Markdown for all text, headings, and lists. Use simple sentences for clarity.
5. **Mathematical Expressions**:
   - Inline math: Enclose in single dollar signs, e.g., `$x^2$`.
   - Display equations: Enclose in double dollar signs, e.g., `$$ \frac{{a}}{{b}} $$`.
   - Ensure valid LaTeX syntax.
6. **Tables**: Use Markdown table syntax, e.g.:

        
        
        
        '''
    if subject =='গণিত':
        prompt =f"""
        আপনি একজন শিক্ষাগত সহকারী। আপনার কাজ হল ৯-১০ শ্রেণির শিক্ষার্থীদের জন্য বাংলা ভাষায় সহজ ও ধাপে ধাপে শেখার গাইড তৈরি করা। আপনার বাক্যগুলো সহজ হতে হবে। সাম্প্রতিক কথোপকথনের স্মৃতি ব্যবহার করে উত্তরটি ব্যক্তিগত করুন এবং স্পষ্টতা বাড়াতে প্রাসঙ্গিক তথ্য যোগ করুন।

ব্যবহারকারীর প্রশ্ন:
{query}

সাম্প্রতিক কথোপকথনের ইতিহাস:
{memory_text}

প্রাসঙ্গিক তথ্য:
{context if context else chunks}

নির্দেশনা:





1. প্রাসঙ্গিক তথ্য: তথ্য মজার এবং আকর্ষণীয় উপায়ে ব্যাখ্যা করুন।
2. ব্যাখ্যাটি আকর্ষণীয় করুন, প্রয়োজনে গল্প ব্যবহার করুন।
3. প্রয়োজনে কথোপকথনের ইতিহাস উল্লেখ করুন।
4. **টেক্সট**: সব টেক্সট, শিরোনাম এবং তালিকার জন্য মার্কডাউন ব্যবহার করুন। স্পষ্টতার জন্য সহজ বাক্য ব্যবহার করুন।
5.গাণিতিক প্রকাশ:
- ইনলাইন(inline) গণিত:  Enclose in single dollar signs, e.g., `$x^2$`.
- সমীকরণ: Enclose in double dollar signs, e.g., `$$ \frac{{a}}{{b}} $$`.
- সঠিক ল্যাটেক্স সিনট্যাক্স (latex syntax) নিশ্চিত করুন।
6. **টেবিল**: 
    -**Tables**: Use Markdown table syntax
   -প্রয়োজনে সারসংক্ষেপ বা তুলনামূলক বিশ্লেষণের জন্য টেবিল দিন।
লক্ষ্য: শিক্ষার্থীরা যেন আনন্দের সাথে এবং সহজে বিষয়টি বুঝতে পারে।
        """
    else:
        prompt=prompt+"\n"+"4. Reply in very simpler English and write meaning around difficult word if necessary"


    # Generate response
    response = gemini_model.generate_content(prompt)

    answer = response.text.strip()  
#     answer= """
    
# |   | a   | b   |
# |---|-----|-----|
# | a | a^2 | ab  |
# | b | ab  | b^2 |
#     """
   
    
    current_dir = os.getcwd()
    filename = os.path.join(current_dir, "explain_raw_text.txt")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(answer)
    
    
    # NEW: Update UserProgress with new chunk_index and chat_memory
 

    # When updating:
    new_pair = {"question": explain_query.query, "answer": answer}
    chat_memory_updated = chat_memory + [new_pair] 
    
    if len(chat_memory_updated) > 30:
        chat_memory_updated = chat_memory_updated[-30:]  # Keep only last 30

    # Assign the new list to progress.chat_memory
    progress.chat_memory = chat_memory_updated
    progress.chunk_index = chunk_index
    progress.last_updated = datetime.utcnow()
    db.commit()



    return ExplainResponse(answer=answer,image=image_data)





# Practice quiz endpoint
@app.post("/{subject}/{topic}/{subtopic}/practise/", response_model=PracticeQuizQuestionResponse)
async def practice_quiz(
    subject: str,
    topic: str,
    subtopic: str,
    submission: Optional[PracticeQuizAnswerSubmission] = None,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    # Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")

    # Validate subject, topic, and subtopic
    subject_obj = db.query(Subject).filter(Subject.name == subject).first()
    if not subject_obj:
        raise HTTPException(status_code=404, detail=f"Subject {subject} not found")
    
    topic_obj = db.query(Topic).filter(
        Topic.name == topic,
        Topic.subject_id == subject_obj.id
    ).first()
    if not topic_obj:
        raise HTTPException(status_code=404, detail=f"Topic {topic} not found in subject {subject}")
    
    subtopic_obj = db.query(Subtopic).filter(
        Subtopic.name == subtopic,
        Subtopic.topic_id == topic_obj.id
    ).first()
    if not subtopic_obj:
        raise HTTPException(status_code=404, detail=f"Subtopic {subtopic} not found in topic {topic}")

    # Determine hardness level and questions tried
    hardness_level = db.query(Quiz1Score).filter(Quiz1Score.attempt_id == db.query(Quiz1Attempt).filter(Quiz1Attempt.user_id == user_id).order_by(Quiz1Attempt.started_at.desc()).first().id).first().student_level if db.query(Quiz1Score).filter(Quiz1Score.attempt_id == db.query(Quiz1Attempt).filter(Quiz1Attempt.user_id == user_id).order_by(Quiz1Attempt.started_at.desc()).first().id).first() else 5  # Default for first question
    questions_tried = 0
    if submission:
        # Validate question
        question = db.query(MCQ).filter(MCQ.id == submission.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail=f"Question ID {submission.question_id} not found")

        # Update hardness level based on correctness
        hardness_level = submission.current_hardness_level
        if submission.is_correct:
            hardness_level = min(hardness_level + 1, 10)  # Increase, max 10
        else:
            hardness_level = max(hardness_level - 1, 1)   # Decrease, min 1

        # Update questions tried
        questions_tried = submission.questions_tried

        # Check if 20 questions have been reached
        if questions_tried >= 20:
            return PracticeQuizQuestionResponse(
                hardness_level=hardness_level,
                message="You have completed 20 practice questions!"
            )

    # Fetch next question (allow reuse of questions)
    next_question = (
        db.query(MCQ)
        .filter(
            MCQ.subtopic_id == subtopic_obj.id,
            MCQ.hardness_level == hardness_level
        )
        .order_by(func.random())
        .first()
    )

    # If no questions are available at this hardness level, end the quiz
    if not next_question:
        return PracticeQuizQuestionResponse(
            hardness_level=hardness_level,
            message=f"No questions available at difficulty level {hardness_level}. Practice completed!"
        )

    return PracticeQuizQuestionResponse(
        question=MCQResponse.from_orm(next_question),
        hardness_level=hardness_level
    )


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    
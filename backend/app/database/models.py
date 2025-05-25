from sqlalchemy import Column, Integer, String, ForeignKey, Text,DateTime, Boolean, Float,JSON,LargeBinary
from sqlalchemy.orm import relationship
from .session import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import LargeBinary  # Add this import for binary data
from datetime import datetime
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    topics = relationship("Topic", back_populates="subject")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    subject = relationship("Subject", back_populates="topics")
    subtopics = relationship("Subtopic", back_populates="topic")


class Subtopic(Base):
    __tablename__ = "subtopics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"))

    topic = relationship("Topic", back_populates="subtopics")
    questions = relationship("MCQ", back_populates="subtopic")
    explains = relationship("Explain", back_populates="subtopic")
    diagrams = relationship("Diagram", back_populates="subtopic")

class MCQ(Base):
    __tablename__ = "mcqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_option = Column(String, nullable=False)
    

    explanation = Column(Text, nullable=True)  # New column for explanation
    hardness_level = Column(Integer, nullable=True, default=5)  # Set default to 5
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"))



    subtopic = relationship("Subtopic", back_populates="questions")


class Quiz0(Base):
    __tablename__ = "quiz0s"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_option = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # "Math" or "English"




# New User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    selections = relationship("UserSelection", back_populates="user")
    attempts = relationship("QuizAttempt", back_populates="user")

    progress = relationship("UserProgress", back_populates="user")  # Links back to UserProgress

# New UserSelection model
class UserSelection(Base):
    __tablename__ = "user_selections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="selections")
    subject = relationship("Subject")
    topic = relationship("Topic")
    subtopic = relationship("Subtopic")
    #attempts = relationship("QuizAttempt", back_populates="selection")

# New QuizAttempt model
# Modified QuizAttempt model
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), index=True, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), index=True, nullable=False)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), index=True, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User", back_populates="attempts")
    subject = relationship("Subject")
    topic = relationship("Topic")
    subtopic = relationship("Subtopic")
    answers = relationship("QuizAnswer", back_populates="attempt")
    score = relationship("QuizScore", uselist=False, back_populates="attempt")
# New QuizAnswer model
class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), index=True)
    quiz_type = Column(String)  # "quiz2" or "quiz3"
    question_id = Column(Integer, ForeignKey("mcqs.id"), index=True)
    user_answer = Column(String)
    correct_answer = Column(String)
    is_correct = Column(Boolean)
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("MCQ")


# New QuizScore model
class QuizScore(Base):
    __tablename__ = "quiz_scores"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), index=True)
    quiz2_correct = Column(Integer, default=0)
    quiz3_correct = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    quiz2_score = Column(Float, default=0.0)
    quiz3_score = Column(Float, default=0.0)
    attempt = relationship("QuizAttempt", back_populates="score")




class Explain(Base):
    __tablename__ = "explains"

    id = Column(Integer, primary_key=True, index=True)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"))
    chunks = Column(JSONB, nullable=False)  # Store list of chunk texts as JSONB
    index_faiss_embedding = Column(JSONB, nullable=True)  # Nullable embedding column for 384-dim vectors

    subtopic = relationship("Subtopic", back_populates="explains")



    # NEW: UserProgress model to store chunk_index and chat_memory
class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), index=True, nullable=False)
    chunk_index = Column(Integer, default=0, nullable=False)  # Tracks current chunk
    chat_memory = Column(JSONB, default=list, nullable=False)  # Stores question-answer pairs
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="progress")
    subtopic = relationship("Subtopic")


# Add this new Diagram class
class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True, index=True)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"))
    description = Column(Text, nullable=False)
    image_content = Column(LargeBinary, nullable=False)  # Use LargeBinary for PNG binary data

    subtopic = relationship("Subtopic", back_populates="diagrams")
    
    
    

# New Quiz1 model
# Quiz1 model
class Quiz1(Base):
    __tablename__ = "quiz1s"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    attempt_id = Column(Integer, ForeignKey("quiz1_attempts.id"), index=True)
    question_id = Column(Integer, ForeignKey("mcqs.id"), index=True)
    hardness_level = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    user_answer = Column(String)  # Store user's selected answer
    correct_answer = Column(String)  # Store correct answer
    user = relationship("User")
    attempt = relationship("Quiz1Attempt", back_populates="answers")
    question = relationship("MCQ")

# Quiz1Attempt model
class Quiz1Attempt(Base):
    __tablename__ = "quiz1_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User")
    answers = relationship("Quiz1", back_populates="attempt")
    score = relationship("Quiz1Score", uselist=False, back_populates="attempt")

# Quiz1Score model
class Quiz1Score(Base):
    __tablename__ = "quiz1_scores"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz1_attempts.id"), index=True)
    total_correct = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    student_level=Column(Integer,default=1)
    attempt = relationship("Quiz1Attempt", back_populates="score")
    
class PractiseAttempt(Base):
    __tablename__ = "practise_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    subject = relationship("Subject")
    topic = relationship("Topic")
    subtopic = relationship("Subtopic")
    answers = relationship("PractiseAnswer", back_populates="attempt")
class PractiseAnswer(Base):
    __tablename__ = "practise_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("practise_attempts.id"), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("mcqs.id"), index=True, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    attempt = relationship("PractiseAttempt", back_populates="answers")
    question = relationship("MCQ")
    
    
    
class FacialExpression(Base):
    __tablename__ = "facial_expressions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    facial_expression = Column(String, nullable=False)
    image = Column(LargeBinary, nullable=False)
    
class UserInteraction(Base):
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String, nullable=False)  # e.g., "dropdown_select", "button_click"
    details = Column(String)  # e.g., "Selected subject: English"
    timestamp = Column(DateTime, default=datetime.utcnow)
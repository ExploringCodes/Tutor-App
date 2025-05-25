

from fastapi import FastAPI, Depends, HTTPException, Header, Query,status
from sqlalchemy.orm import Session
from typing import List,Optional
from datetime import datetime
from .database.session import SessionLocal, Base, engine
from .database.models import  Subject, Topic, Subtopic, MCQ, User, UserSelection, QuizAttempt, QuizAnswer, QuizScore,UserProgress,Diagram,Quiz1,Quiz1Attempt,Quiz1Score,PractiseAnswer,PractiseAttempt,FacialExpression,UserInteraction
from .schemas.models import SubjectBase, TopicBase, SubtopicBase,UserModel,UserInteractionCreate
from .schemas.quizzes import QuizAnswerSubmission, QuizQuestionResponse, PracticeQuizAnswerSubmission, PracticeQuizQuestionResponse,MCQResponse
from .schemas.explains import ExplainQuery,ExplainResponse
from .schemas.selections import SelectionRequest

from sqlalchemy.sql import func
from pydantic import BaseModel
from .router.quizzes import router as quizzes_router
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


import secrets
from urllib.parse import urlencode
import requests


import base64  # Add this import for base64 encoding
import json 

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="AITutor Quiz Webapp")


Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

##########################login stuff 






from pydantic import BaseModel






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


# Endpoint to select subject, topic, and subtopic in one request
@app.post("/select/")
async def select_subject_topic_subtopic(
    selection: SelectionRequest,
    user_id: int = Header(...),
    db: Session = Depends(get_db),
    request:Request=None
):
    session_user = request.session.get("user")
    if not session_user or session_user.get("id") != user_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing session")
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

app.include_router(quizzes_router)


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
    db: Session = Depends(get_db),
    request:Request=None 
):
    # Check session for authenticated user
    session_user = request.session.get("user")
    if not session_user or session_user.get("id") != user_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing session")
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


@app.post("/interactions")
async def save_interaction(interaction: UserInteractionCreate, db: Session = Depends(get_db), request: Request = None):
    # Check session for authenticated user
    session_user = request.session.get("user")
    if not session_user or session_user.get("id") != interaction.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing session")
    
    # Validate user
    user = db.query(User).filter(User.id == interaction.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {interaction.user_id} not found")
    
    # Proceed with saving the interaction
    db_interaction = UserInteraction(
        user_id=interaction.user_id,
        interaction_type=interaction.interaction_type,
        details=interaction.details
    )
    db.add(db_interaction)
    db.commit()
    logger.info(f"Interaction logged: user_id={interaction.user_id}, type={interaction.interaction_type}, details={interaction.details}")
    return {"message": "Interaction saved"}



@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    
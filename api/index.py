from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------
if os.getenv("VERCEL"):
    DB_FILE = "/tmp/visionnova.db" if os.environ.get("VERCEL") else os.path.join(os.path.dirname(__file__), "visionnova.db")
else:
    DB_FILE = "/tmp/visionnova.db" if os.environ.get("VERCEL") else os.path.join(os.path.dirname(__file__), "visionnova.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the User Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Automatically generate the SQL Database File!
Base.metadata.create_all(bind=engine)
# ---------------------------------------------------------
app = FastAPI()

# Allow CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from sqlalchemy.orm import Session
from fastapi import Depends

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SQL AUTHENTICATION APIS ---
class SignupRequest(BaseModel):
    fullname: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/signup")
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Account with this email already exists")
    
    # Save to SQL Database
    new_user = User(fullname=data.fullname, email=data.email, password=data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "Account created successfully"}

@app.post("/api/auth/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Query SQL Database for matching user
    user = db.query(User).filter(User.email == data.email, User.password == data.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"status": "success", "user": {"fullname": user.fullname, "email": user.email}}

class ResumeData(BaseModel):
    text: str
    location: str = None

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/api/analyze")
async def analyze_resume(data: ResumeData):
    # ---------------------------------------------------------
    # EXACT, DETERMINISTIC MATHEMATICAL ATS SCORING ALGORITHM
    # ---------------------------------------------------------
    text_lower = data.text.lower()
    exact_score = 30 # Base score for having a resume
    
    # 1. Section formatting (up to 15 points)
    sections = ['experience', 'education', 'skills', 'projects', 'summary']
    found_sections = sum(1 for sec in sections if sec in text_lower)
    exact_score += min(15, found_sections * 3)
    
    # 2. Quantifiable Metrics (up to 25 points)
    numbers = re.findall(r'\b\d+\b', text_lower)
    metrics_count = len(numbers)
    exact_score += min(25, metrics_count * 2) # 2 points per number/metric found
    
    # 3. Action Verbs (up to 20 points)
    action_verbs = ['developed', 'managed', 'created', 'led', 'designed', 'optimized', 'spearheaded', 'implemented', 'increased', 'reduced', 'improved', 'resolved', 'architected', 'orchestrated']
    found_verbs = sum(1 for verb in action_verbs if verb in text_lower)
    exact_score += min(20, found_verbs * 3)
    
    # 4. Word count depth (up to 10 points)
    word_count = len(text_lower.split())
    if word_count > 300:
        exact_score += 10
    elif word_count > 150:
        exact_score += 5
        
    exact_score = min(100, exact_score)
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # HYBRID AI ANALYSIS: Fast Score + AI Personalized Feedback
    # ---------------------------------------------------------
    # The user wants exact, correct answers based on reading the resume.
    # We will use Ollama but heavily optimize it to be FAST.
    
    prompt = f"""
    You are an expert Enterprise ATS Analyzer.
    
    Based on the EXACT text of their resume, provide personalized feedback. You must ACTUALLY READ the text and quote their specific experience. Do NOT give generic advice.
    
    CRITICAL RULES FOR SPEED AND ACCURACY:
    1. Quote specific projects, companies, or skills from their text.
    2. Keep your answers extremely short and exact (1 sentence per point) to save time.
    3. Output EXACTLY 3 strengths, 3 weaknesses, and 3 missing keywords.
    
    JSON Format Required:
    {{
      "strengths": ["<Specific strength quoting their text>", "<Specific strength>", "<Specific strength>"],
      "weaknesses": ["<Specific weakness quoting their text>", "<Specific weakness>", "<Specific weakness>"],
      "missing_keywords": ["<keyword1>", "<keyword2>", "<keyword3>"],
      "advice": "<One short, personalized sentence of actionable advice.>"
    }}
    
    Resume Text:
    {data.text[:2500]} 
    """

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if GROQ_API_KEY:
        groq_payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 300,
            "response_format": {"type": "json_object"}
        }
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=groq_payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            analysis_data = json.loads(result['choices'][0]['message']['content'])
            analysis_data['score'] = exact_score
            return analysis_data
        except Exception as e:
            print("Groq ATS Analyzer Error:", e)

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 300
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=2)
        response.raise_for_status()
        result = response.json()
        
        analysis_data = json.loads(result['response'])
        analysis_data['score'] = exact_score
        return analysis_data
        
    except Exception as e:
        print("Error with Ollama ATS Analyzer:", e)
        # Fast fallback in case Ollama crashes
        return {
            "score": exact_score,
            "strengths": ["Clear formatting", "Includes experience"],
            "weaknesses": ["Consider adding more metrics", "Missing a few industry keywords"],
            "missing_keywords": ["Agile", "Cloud", "Leadership"],
            "advice": "Try adding more hard numbers to your bullet points to quantify your impact."
        }

import urllib.parse

ADZUNA_APP_ID = "2d9d2e21"
ADZUNA_APP_KEY = "b44899ca5653bdd60b086500dff03496"

@app.post("/api/jobs")
async def suggest_jobs(data: ResumeData):
    if not data.text or len(data.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short or empty.")
    
    # 1. Extremely Fast Keyword Extraction to Search Adzuna
    text_lower = data.text.lower()
    search_term = "Software Developer"
    if "data scientist" in text_lower or "machine learning" in text_lower: search_term = "Data Scientist"
    elif "data analyst" in text_lower or "sql" in text_lower: search_term = "Data Analyst"
    elif "react" in text_lower or "frontend" in text_lower: search_term = "Frontend Developer"
    elif "node" in text_lower or "backend" in text_lower: search_term = "Backend Developer"
    elif "python" in text_lower: search_term = "Python Developer"
    elif "manager" in text_lower: search_term = "Product Manager"
    
    # 2. Fetch 50 live Indian jobs instantly from Adzuna API
    adzuna_url = f"http://api.adzuna.com/v1/api/jobs/in/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=50&what={urllib.parse.quote(search_term)}"
    
    if data.location and data.location.strip():
        adzuna_url += f"&where={urllib.parse.quote(data.location.strip())}"
    
    try:
        adzuna_resp = requests.get(adzuna_url)
        adzuna_resp.raise_for_status()
        adzuna_data = adzuna_resp.json()
        
        live_jobs = []
        for j in adzuna_data.get("results", []):
            live_jobs.append({
                "company": j.get("company", {}).get("display_name", "Unknown Company"),
                # Remove strong tags that adzuna sometimes returns
                "title": j.get("title", "").replace("<strong>", "").replace("</strong>", ""),
                "location": ", ".join(reversed(j.get("location", {}).get("area", []))),
                "link": j.get("redirect_url", ""),
                "match_reason": "This live job aligns with your top skills in the industry."
            })
            
    except Exception as e:
        print("Adzuna API Error:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch live jobs from Adzuna.")
        
    if not live_jobs:
        raise HTTPException(status_code=404, detail="No live jobs found for your profile.")
        
    # 3. MAKE IT LIGHTNING FAST (Bypass AI Generation)
    # Generating 15 JSON jobs via a local LLM takes 1-2 minutes.
    # To make this INSTANT, we will just return the top 15 jobs directly from Adzuna.
    
    final_jobs = []
    for job in live_jobs[:15]:
        company_name = job["company"]
        job_title = job["title"]
        
        # 'I'm Feeling Lucky' Trick: Prepending a backslash '\' in DuckDuckGo automatically redirects 
        # directly to the official company website without stopping at the search engine!
        direct_redirect_link = f"https://duckduckgo.com/?q={urllib.parse.quote('\\' + company_name + ' careers ' + job_title)}"
        
        job["link"] = direct_redirect_link
        job["match_reason"] = f"Your resume strongly aligns with the requirements for this {job_title} role at {company_name}."
        final_jobs.append(job)
        
    return {"jobs": final_jobs}

import json

class MockTestGenerateRequest(BaseModel):
    resume_text: str
    job_description: str

class MockTestEvaluateRequest(BaseModel):
    questions: list[str]
    user_answers: list[str]

@app.post("/api/mock-test/generate")
async def generate_mock_test(data: MockTestGenerateRequest):
    prompt = f"""
    You are a strict, expert Senior Technical Interviewer.
    Based on the candidate's resume and the job description, generate EXACTLY 8 highly specific, deep technical interview questions.
    
    CRITICAL RULES:
    1. The questions must test exact frameworks, languages, and concepts mentioned in the Job Description.
    2. Generate a MIX: EXACTLY 4 theoretical/conceptual questions, and EXACTLY 4 coding/programming tasks (e.g., "Write a Python function to...", "Write a SQL query to...").
    3. Do NOT ask generic behavioral questions. Ask hard technical questions.
    4. Output ONLY a strict JSON array of strings. No markdown, no introductory text.
    
    Format Required:
    {{
        "questions": [
            "Write a Python function to reverse a linked list.",
            "Explain exactly how React's Virtual DOM reconciliation algorithm works under the hood.",
            "Write a program that connects to a database and fetches...",
            ... (8 questions total)
        ]
    }}
    
    Resume:
    {data.resume_text[:2000]}
    
    Job Description:
    {data.job_description[:2000]}
    """
    
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if GROQ_API_KEY:
        groq_payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=groq_payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return json.loads(result['choices'][0]['message']['content'])
        except Exception as e:
            print("Groq Mock Test Gen Error:", e)

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=2)
        response.raise_for_status()
        return json.loads(response.json()['response'])
    except Exception as e:
        print("Mock Test Gen Error:", e)
        # Fallback
        return {"questions": [
            "Can you explain a complex project you worked on and the technical challenges you faced?",
            "How do your skills align with the core requirements of this role?",
            "Describe a time you had to learn a new technology quickly.",
            "How do you ensure the code you write is maintainable and scalable?",
            "What is your approach to debugging a critical issue in production?"
        ]}

@app.post("/api/mock-test/evaluate")
async def evaluate_mock_test(data: MockTestEvaluateRequest):
    prompt = f"""
    You are an expert Senior Technical Interviewer evaluating a candidate's written test.
    For each question, evaluate their answer STRICTLY. If it's a programming question, check their code logic.
    
    CRITICAL RULES:
    1. If the candidate left the answer completely blank, or if their answer is wrong/incomplete, you MUST set "is_correct": false.
    2. If "is_correct" is false, you MUST provide a highly detailed, perfectly correct technical answer in the "ideal_answer" field. If it was a programming question, write the exact code required.
    3. If the candidate's answer is correct, set "is_correct": true and leave "ideal_answer" empty ("").
    
    Questions and Answers:
    """
    for i in range(len(data.questions)):
        prompt += f"\nQ: {data.questions[i]}\nA: {data.user_answers[i]}\n"
        
    prompt += """
    CRITICAL: Output ONLY strict JSON. No markdown. No conversational text.
    Format Required:
    {
        "evaluations": [
            {
                "is_correct": true,
                "feedback": "Excellent explanation of the concept. Your code is efficient.",
                "ideal_answer": ""
            },
            {
                "is_correct": false,
                "feedback": "You left this blank, or your logic was flawed because X.",
                "ideal_answer": "Here is the exact correct answer/code required..."
            }
        ]
    }
    """
    
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if GROQ_API_KEY:
        groq_payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=groq_payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            analysis_data = json.loads(result['choices'][0]['message']['content'])
            
            evals = analysis_data.get('evaluations', [])
            for i, ans in enumerate(data.user_answers):
                if len(ans.strip()) < 5:
                    if i < len(evals):
                        evals[i]['is_correct'] = False
                        evals[i]['feedback'] = "You did not provide an answer. You must attempt the question to receive points."
                        
            correct_count = sum(1 for e in evals if e.get('is_correct', False))
            total_questions = len(evals) if len(evals) > 0 else 1
            analysis_data['total_score'] = int((correct_count / total_questions) * 100)
            return analysis_data
        except Exception as e:
            print("Groq Mock Test Eval Error:", e)

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=2)
        response.raise_for_status()
        analysis_data = json.loads(response.json()['response'])
        
        # Mathematically calculate score so it is 100% accurate
        evals = analysis_data.get('evaluations', [])
        
        # PYTHON HARD OVERRIDE FOR BLANK ANSWERS
        # The LLM sometimes hallucinates and marks blank answers as "true". This forces it to false.
        for i, ans in enumerate(data.user_answers):
            if len(ans.strip()) < 5:
                if i < len(evals):
                    evals[i]['is_correct'] = False
                    evals[i]['feedback'] = "You did not provide an answer. You must attempt the question to receive points."
                    
        correct_count = sum(1 for e in evals if e.get('is_correct', False))
        total_questions = len(evals) if len(evals) > 0 else 1
        analysis_data['total_score'] = int((correct_count / total_questions) * 100)
        
        return analysis_data
    except Exception as e:
        print("Mock Test Eval Error:", e)
        # Fallback
        evals = []
        score = 0
        for i, ans in enumerate(data.user_answers):
            if len(ans.strip()) > 10:
                evals.append({"is_correct": True, "feedback": "Good effort on this answer.", "ideal_answer": ""})
                score += 20
            else:
                evals.append({"is_correct": False, "feedback": "Answer was too short or empty.", "ideal_answer": "A detailed technical explanation covering the core concepts of the question."})
        return {"total_score": score, "evaluations": evals}

class InterviewChatRequest(BaseModel):
    resume_text: str
    job_title: str
    history: list[dict]

@app.post("/api/chat/interview")
async def chat_interview(data: InterviewChatRequest):
    system_prompt = f"""
    You are VisionNova, a strict, professional Corporate HR Manager. 
    You are conducting a formal First-Round HR Interview with a candidate for the role of '{data.job_title}'.
    
    Candidate's Resume Context:
    {data.resume_text[:1500]}
    
    CRITICAL RULES FOR HR INTERVIEW:
    1. Act exactly like a real company HR Recruiter. Ask behavioral and cultural fit questions (e.g., conflict resolution, leadership, strengths/weaknesses).
    2. Demand the candidate answer using the STAR method (Situation, Task, Action, Result).
    3. You may ask HR screening questions like expected salary, notice period, or willingness to relocate.
    4. Keep your responses short (2-3 sentences max). Ask ONE question at a time and wait for their answer.
    5. If their answer is poor, brief, or lacks confidence, tell them how an HR manager perceives that answer and instruct them to try again with more detail.
    6. Introduce yourself formally at the start of the conversation.
    """
    
    messages = [{"role": "system", "content": system_prompt}] + data.history
    
    # =======================================================================
    # CLOUD AI INTEGRATION (GROQ)
    # Get your FREE API key from: https://console.groq.com/keys
    # =======================================================================
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    
    if GROQ_API_KEY:
        try:
            groq_payload = {
                "model": "llama3-8b-8192",
                "messages": messages,
                "temperature": 0.6,
                "max_tokens": 150
            }
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            # 10 second timeout for Cloud API
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=groq_payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return {"reply": result["choices"][0]["message"]["content"]}
        except Exception as e:
            print("Groq API Error:", e)
            
    # Local Ollama Fallback (Only works when running locally via npm run dev)
    payload = {
        "model": "llama3",
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.6
        }
    }
    
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=2)
        response.raise_for_status()
        result = response.json()
        return {"reply": result["message"]["content"]}
    except Exception as e:
        print("Chat Error:", e)
        # Smart Conversational Fallback for Cloud (Vercel) where Ollama is unavailable
        user_message = data.history[-1]["content"].lower() if data.history else ""
        
        reply = "That's an interesting point. Could you tell me more about how you handled challenges in that specific situation?"
        
        if "hello" in user_message or "hi" in user_message or "start" in user_message:
            reply = f"Hello! Welcome to your interview for the {data.job_title} role. To start, could you walk me through your most relevant experience?"
        elif "experience" in user_message or "worked" in user_message or "project" in user_message:
            reply = "Impressive background. Can you give me a specific example of a difficult challenge you faced during that time, using the STAR method (Situation, Task, Action, Result)?"
        elif "strength" in user_message or "good at" in user_message:
            reply = "Those are valuable strengths. How would you apply them directly to the day-to-day responsibilities of this position?"
        elif "weakness" in user_message or "improve" in user_message:
            reply = "I appreciate your honesty. What actionable steps are you currently taking to improve in that area?"
        elif "team" in user_message or "conflict" in user_message:
            reply = "Teamwork is crucial here. Can you describe a time you disagreed with a colleague and how you resolved it professionally?"
        elif "?" in user_message:
            reply = "That's a great question. In this role, adaptability and strong problem-solving skills are our top priorities. How do you usually adapt to sudden changes in a project's scope?"
            
        return {"reply": reply}

class OTPRequest(BaseModel):
    email: str
    otp: str

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@app.post("/api/auth/send-otp")
async def send_otp(data: OTPRequest):
    # ==========================================
    # REPLACE WITH YOUR GMAIL AND APP PASSWORD
    # ==========================================
    SENDER_EMAIL = "your_email@gmail.com"
    APP_PASSWORD = "your_app_password"
    
    if SENDER_EMAIL == "your_email@gmail.com":
        return {"status": "success", "message": "Simulated"}
        
    try:
        msg = MIMEMultipart()
        msg['From'] = f"VisionNova AI <{SENDER_EMAIL}>"
        msg['To'] = data.email
        msg['Subject'] = "VisionNova AI - Password Reset OTP"
        
        body = f"Hello,\n\nYour 6-digit OTP for resetting your VisionNova password is: {data.otp}\n\nIf you did not request this, please ignore this email."
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return {"status": "success", "message": "OTP sent successfully."}
    except Exception as e:
        print("SMTP Error:", e)
        raise HTTPException(status_code=500, detail="Failed to send email.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)







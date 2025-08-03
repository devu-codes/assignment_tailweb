from fastapi import FastAPI, Depends, Request, Form, HTTPException, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import db, models, crud, schemas, utils
import secrets

app = FastAPI()
models.Base.metadata.create_all(bind=db.engine)

import os

# Get the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set up templates and static files directories
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

sessions = {}

def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

def get_teacher_from_session(token: str = None):
    return sessions.get(token)

from fastapi.responses import HTMLResponse

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_teacher(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing = crud.get_teacher_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    teacher = crud.create_teacher(db, username, password)

    # Auto-login after registration
    token = secrets.token_hex(16)
    sessions[token] = teacher.id
    response.set_cookie(key="session", value=token, httponly=True)

    return {"message": "Registered successfully"}

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    teacher = crud.get_teacher_by_username(db, username)
    if not teacher or not crud.verify_password(password, teacher.salt, teacher.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = secrets.token_hex(16)
    sessions[token] = teacher.id
    response.set_cookie(key="session", value=token, httponly=True)
    return {"message": "Login successful"}

@app.get("/home")
def home(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session")
    teacher_id = get_teacher_from_session(session_token)
    if not teacher_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    students = crud.get_students(db)
    return students

@app.post("/student/add")
def add_student(student: schemas.StudentCreate, request: Request, db: Session = Depends(get_db)):
    teacher_id = get_teacher_from_session(request.cookies.get("session"))
    if not teacher_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    crud.add_or_update_student(db, student, teacher_id)
    return {"status": "success"}

@app.post("/student/{student_id}/update")
def update_student(student_id: int, update: schemas.StudentUpdate, request: Request, db: Session = Depends(get_db)):
    teacher_id = get_teacher_from_session(request.cookies.get("session"))
    if not teacher_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if update.marks:
        crud.update_marks(db, student_id, update.marks, teacher_id)
    elif update.subject:
        crud.update_subject(db, student_id, update.subject, teacher_id)
    return {"status": "updated"}

@app.post("/logout")
def logout(response: Response, request: Request):
    session_token = request.cookies.get("session")
    if session_token and session_token in sessions:
        del sessions[session_token]
    response.delete_cookie(key="session")
    return {"message": "Logged out successfully"}

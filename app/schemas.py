from pydantic import BaseModel

class StudentBase(BaseModel):
    name: str
    subject: str
    marks: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    marks: int
    subject: str
    name: str

class TeacherLogin(BaseModel):
    username: str
    password: str

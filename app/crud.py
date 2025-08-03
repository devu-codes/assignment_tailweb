from sqlalchemy.orm import Session
from . import models, schemas, utils

def get_teacher_by_username(db: Session, username: str):
    return db.query(models.Teacher).filter(models.Teacher.username == username).first()

def verify_password(raw_password: str, salt: str, hash_val: str):
    return utils.hash_password(raw_password, salt) == hash_val

def create_teacher(db: Session, username: str, password: str):
    salt = utils.generate_salt()
    hashed = utils.hash_password(password, salt)
    teacher = models.Teacher(username=username, password_hash=hashed, salt=salt)
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher

def get_students(db: Session):
    return db.query(models.Student).all()

def update_marks(db: Session, student_id: int, new_marks: int, teacher_id: int):
    if new_marks < 0 or new_marks > 100:
        raise ValueError("Marks must be between 0 and 100")

    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        student.marks = new_marks
        db.commit()

        log = models.AuditLog(student_id=student_id, teacher_id=teacher_id, action=f"Updated marks to {new_marks}")
        db.add(log)
        db.commit()
        return student
    
def update_subject(db: Session, student_id: int, new_subject: str, teacher_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        student.subject = new_subject
        db.commit()

        log = models.AuditLog(student_id=student_id, teacher_id=teacher_id, action=f"Updated marks to {new_subject}")
        db.add(log)
        db.commit()
        return student

def add_or_update_student(db: Session, student: schemas.StudentCreate, teacher_id: int):
    existing = db.query(models.Student).filter(
        models.Student.name == student.name,
        models.Student.subject == student.subject
    ).first()

    if existing:
        new_marks = utils.calculate_new_marks(existing.marks, student.marks)
        if new_marks > 100:
            raise ValueError("Total marks cannot exceed 100")
        existing.marks = new_marks
        db.commit()
    else:
        new_student = models.Student(name=student.name, subject=student.subject, marks=student.marks)
        db.add(new_student)
        db.commit()

    log = models.AuditLog(student_id=existing.id if existing else new_student.id, teacher_id=teacher_id,
                          action=f"Add or update student {student.name} - {student.subject}")
    db.add(log)
    db.commit()

# services.py
from database import get_db
from typing import List, Tuple, Dict, Optional
import csv
import json
import io
from database import get_connection
from models import Student

# ---------- Helper validations ----------


def validate_roll(roll: str) -> str:
    roll = roll.strip()
    if not roll:
        raise ValueError("Roll number is required.")
    if len(roll) > 20:
        raise ValueError("Roll number too long.")
    return roll


def validate_name(name: str) -> str:
    name = " ".join(name.strip().split())
    if not name:
        raise ValueError("Name is required.")
    if len(name) > 80:
        raise ValueError("Name too long.")
    return name


def validate_subject(sub: str) -> str:
    sub = " ".join(sub.strip().title().split())
    if not sub:
        raise ValueError("Subject is required.")
    if len(sub) > 60:
        raise ValueError("Subject too long.")
    return sub


def validate_grade(grade_str: str) -> int:
    try:
        grade = int(grade_str)
    except Exception:
        raise ValueError("Grade must be an integer.")
    if not (0 <= grade <= 100):
        raise ValueError("Grade must be between 0 and 100.")
    return grade

# ---------- Student operations (DB) ----------


def add_student_db(name: str, roll_number: str) -> None:
    name = validate_name(name)
    roll_number = validate_roll(roll_number)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO students (roll_number, name) VALUES (?, ?)", (roll_number, name))
        conn.commit()
    finally:
        conn.close()


def list_students_db() -> List[Dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT roll_number, name FROM students ORDER BY roll_number")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_student_db(roll_number):
    db = get_db()
    # Delete the student
    db.execute("DELETE FROM students WHERE roll_number = ?", (roll_number,))
    # Also delete associated grades (optional but recommended)
    db.execute("DELETE FROM grades WHERE student_roll = ?", (roll_number,))
    db.commit()


def get_student_db(roll_number: str) -> Optional[Dict]:
    roll_number = validate_roll(roll_number)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT roll_number, name FROM students WHERE roll_number = ?", (roll_number,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cur.execute(
        "SELECT subject, grade FROM grades WHERE roll_number = ? ORDER BY subject", (roll_number,))
    grades = [dict(r) for r in cur.fetchall()]
    conn.close()
    st = Student(row["name"], row["roll_number"])
    for g in grades:
        st.grades[g["subject"]] = g["grade"]
    return st.to_dict()


def add_grade_db(roll_number: str, subject: str, grade: int) -> None:
    roll_number = validate_roll(roll_number)
    subject = validate_subject(subject)
    grade = validate_grade(str(grade))
    conn = get_connection()
    cur = conn.cursor()
    # ensure student exists
    cur.execute("SELECT 1 FROM students WHERE roll_number=?", (roll_number,))
    if not cur.fetchone():
        conn.close()
        raise ValueError("Student not found.")
    # upsert grade
    cur.execute("""
        INSERT INTO grades (roll_number, subject, grade) VALUES (?, ?, ?)
        ON CONFLICT(roll_number, subject) DO UPDATE SET grade=excluded.grade;
    """, (roll_number, subject, grade))
    conn.commit()
    conn.close()


def compute_student_average(roll_number: str) -> float:
    roll_number = validate_roll(roll_number)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT AVG(grade) AS avg FROM grades WHERE roll_number=?", (roll_number,))
    row = cur.fetchone()
    conn.close()
    return round(row["avg"] or 0.0, 2)


def class_average_db(subject: str) -> float:
    subject = validate_subject(subject)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT AVG(grade) AS avg FROM grades WHERE subject=?", (subject,))
    row = cur.fetchone()
    conn.close()
    return round(row["avg"] or 0.0, 2)


def subject_topper_db(subject: str) -> Optional[Dict]:
    subject = validate_subject(subject)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.roll_number, s.name, g.grade
        FROM grades g
        JOIN students s ON s.roll_number = g.roll_number
        WHERE g.subject = ?
        ORDER BY g.grade DESC, s.name ASC
        LIMIT 1;
    """, (subject,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

# ---------- Save data locally (CSV / JSON downloads) ----------


def export_csv() -> bytes:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.roll_number, s.name, g.subject, g.grade
        FROM students s
        LEFT JOIN grades g ON g.roll_number = s.roll_number
        ORDER BY s.roll_number, g.subject;
    """)
    rows = cur.fetchall()
    conn.close()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["roll_number", "name", "subject", "grade"])
    for r in rows:
        writer.writerow([r["roll_number"], r["name"], r["subject"]
                        or "", r["grade"] if r["grade"] is not None else ""])
    return buf.getvalue().encode("utf-8")


def export_json() -> bytes:
    data = []
    for s in list_students_db():
        st = get_student_db(s["roll_number"])
        data.append(st)
    return json.dumps(data, indent=2).encode("utf-8")

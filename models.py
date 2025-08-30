# models.py
from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class Student:
    name: str
    roll_number: str
    grades: Dict[str, int] = field(default_factory=dict)

    def add_grade(self, subject: str, grade: int) -> None:
        """Add/update a grade with validation (0..100)."""
        if not isinstance(grade, int):
            raise ValueError("Grade must be an integer.")
        if grade < 0 or grade > 100:
            raise ValueError("Grade must be between 0 and 100.")
        subject = subject.strip().title()
        if not subject:
            raise ValueError("Subject cannot be empty.")
        self.grades[subject] = grade

    def calculate_average(self) -> float:
        if not self.grades:
            return 0.0
        return sum(self.grades.values()) / len(self.grades)

    def to_dict(self) -> dict:
        return {"name": self.name, "roll_number": self.roll_number, "grades": self.grades}


class StudentTracker:
    """In-memory manager primarily used by the CLI; mirrors DB operations for clarity."""
    def __init__(self) -> None:
        self._students: Dict[str, Student] = {}

    def add_student(self, student: Student) -> None:
        if student.roll_number in self._students:
            raise ValueError("Roll number must be unique.")
        self._students[student.roll_number] = student

    def get_student(self, roll_number: str) -> Optional[Student]:
        return self._students.get(roll_number)

    def add_grade(self, roll_number: str, subject: str, grade: int) -> None:
        st = self.get_student(roll_number)
        if not st:
            raise ValueError("Student not found.")
        st.add_grade(subject, grade)

    def view_student_details(self, roll_number: str) -> Optional[Student]:
        return self.get_student(roll_number)

    def all_students(self) -> List[Student]:
        return list(self._students.values())

    def class_average(self, subject: str) -> float:
        subject = subject.strip().title()
        vals = [s.grades[subject] for s in self._students.values() if subject in s.grades]
        return sum(vals) / len(vals) if vals else 0.0

    def subject_topper(self, subject: str) -> Optional[Student]:
        subject = subject.strip().title()
        best = None
        best_mark = -1
        for s in self._students.values():
            if subject in s.grades and s.grades[subject] > best_mark:
                best, best_mark = s, s.grades[subject]
        return best

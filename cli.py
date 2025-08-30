# cli.py
from models import Student, StudentTracker

def prompt(msg: str) -> str:
    return input(msg).strip()

def main():
    tracker = StudentTracker()
    while True:
        print("\n=== Student Performance Tracker (CLI) ===")
        print("1. Add Student")
        print("2. Add Grade")
        print("3. View Student Details")
        print("4. Calculate Student Average")
        print("5. Class Average (subject)")
        print("6. Subject-wise Topper")
        print("0. Exit")
        choice = prompt("Choose: ")

        if choice == "1":
            name = prompt("Name: ")
            roll = prompt("Roll Number: ")
            try:
                tracker.add_student(Student(name, roll))
                print("Student added.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            roll = prompt("Roll Number: ")
            subj = prompt("Subject: ")
            try:
                grade = int(prompt("Grade (0-100): "))
                tracker.add_grade(roll, subj, grade)
                print("Grade saved.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            roll = prompt("Roll Number: ")
            s = tracker.view_student_details(roll)
            if not s:
                print("Not found.")
            else:
                print(f"{s.roll_number} - {s.name} | Grades: {s.grades}")

        elif choice == "4":
            roll = prompt("Roll Number: ")
            s = tracker.view_student_details(roll)
            if not s:
                print("Not found.")
            else:
                print(f"Average: {s.calculate_average():.2f}")

        elif choice == "5":
            subj = prompt("Subject: ")
            print(f"Class average in {subj}: {tracker.class_average(subj):.2f}")

        elif choice == "6":
            subj = prompt("Subject: ")
            top = tracker.subject_topper(subj)
            if top:
                print(f"Topper in {subj}: {top.name} ({top.grades[subj]})")
            else:
                print("No data.")

        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

# app.py
from services import delete_student_db  # Add this with your other imports
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from io import BytesIO
from database import init_db
from services import (
    add_student_db, list_students_db, get_student_db, add_grade_db,
    compute_student_average, class_average_db, subject_topper_db,
    validate_grade, validate_name, validate_roll, validate_subject,
    export_csv, export_json
)

app = Flask(__name__)
app.secret_key = "change-me-in-production"

# Initialize DB on startup
init_db()


@app.route("/")
def home():
    total = len(list_students_db())
    return render_template("index.html", total_students=total)

# -------- Students --------


@app.route("/students")
def students():
    q = request.args.get("q", "").strip().lower()
    data = list_students_db()
    if q:
        data = [s for s in data if q in s["name"].lower()
                or q in s["roll_number"].lower()]
    return render_template("all_students.html", students=data, q=q)


@app.route("/students/<roll_number>/delete", methods=["POST"])
def delete_student(roll_number):
    try:
        delete_student_db(roll_number)
        flash("🗑️ Student deleted successfully.", "success")
    except Exception as e:
        flash(f"❌ Could not delete student: {e}", "danger")
    return redirect(url_for("students"))


@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        try:
            name = validate_name(request.form.get("name", ""))
            roll = validate_roll(request.form.get("roll_number", ""))
            add_student_db(name, roll)
            flash("✅ Student added successfully.", "success")
            return redirect(url_for("students"))
        except Exception as e:
            flash(f"❌ {e}", "danger")
    return render_template("add_student.html")


@app.route("/students/<roll_number>")
def student_details(roll_number):
    st = get_student_db(roll_number)
    if not st:
        flash("❌ Student not found.", "danger")
        return redirect(url_for("students"))
    avg = compute_student_average(roll_number)
    return render_template("student_details.html", student=st, avg=avg)

# -------- Grades --------


@app.route("/grades/add", methods=["GET", "POST"])
def add_grade():
    if request.method == "POST":
        try:
            roll = validate_roll(request.form.get("roll_number", ""))
            subject = validate_subject(request.form.get("subject", ""))
            grade = validate_grade(request.form.get("grade", ""))
            add_grade_db(roll, subject, grade)
            flash("✅ Grade saved.", "success")
            return redirect(url_for("student_details", roll_number=roll))
        except Exception as e:
            flash(f"❌ {e}", "danger")
    return render_template("add_grade.html")

# -------- Analytics (Class Average, Subject Topper) --------


@app.route("/analytics", methods=["GET", "POST"])
def analytics():
    result = None
    if request.method == "POST":
        subject = request.form.get("subject", "")
        try:
            avg = class_average_db(subject)
            top = subject_topper_db(subject)
            result = {"subject": subject.title(), "avg": avg, "topper": top}
        except Exception as e:
            flash(f"❌ {e}", "danger")
    return render_template("analytics.html", result=result)

# -------- Exports (Save data locally) --------


@app.route("/export/csv")
def download_csv():
    data = export_csv()
    return send_file(BytesIO(data), mimetype="text/csv",
                     as_attachment=True, download_name="students_export.csv")


@app.route("/export/json")
def download_json():
    data = export_json()
    return send_file(BytesIO(data), mimetype="application/json",
                     as_attachment=True, download_name="students_export.json")

# Health check


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # For local dev
    app.run(host="0.0.0.0", port=8080,
            debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, Response
import mysql.connector
import pandas as pd
import io
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this for better security

# Function to connect to MySQL (Use Render’s MySQL or another remote DB)
def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),  # Remote MySQL Host
        user=os.getenv("DB_USER"),  # MySQL Username
        password=os.getenv("DB_PASSWORD"),  # MySQL Password
        database="StudentDB"
    )

# Home route (Show all students)
@app.route("/")
def index():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    db.close()
    return render_template("index.html", students=students)

# Add student
@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"]
    class_name = request.form["class"]
    phone = request.form["phone"]
    address = request.form["address"]
    
    if name and class_name and phone and address:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO students (name, class, phone, address) VALUES (%s, %s, %s, %s)", 
                       (name, class_name, phone, address))
        db.commit()
        db.close()
        flash("Student added successfully!", "success")
    else:
        flash("Please fill all fields", "danger")

    return redirect(url_for("index"))

# Search student
@app.route("/search", methods=["POST"])
def search_student():
    search_query = request.form["search"]
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE name LIKE %s OR class LIKE %s", 
                   ('%' + search_query + '%', '%' + search_query + '%'))
    students = cursor.fetchall()
    db.close()
    return render_template("index.html", students=students)

# Update student
@app.route("/update", methods=["POST"])
def update_student():
    student_id = request.form.get("id")
    name = request.form.get("name")
    class_name = request.form.get("class")
    phone = request.form.get("phone")
    address = request.form.get("address")

    if not student_id:
        flash("Student ID is required!", "danger")
        return redirect(url_for("index"))

    db = connect_db()
    cursor = db.cursor()
    sql = "UPDATE students SET name=%s, class=%s, phone=%s, address=%s WHERE id=%s"
    values = (name, class_name, phone, address, student_id)
    cursor.execute(sql, values)
    db.commit()
    db.close()

    flash("Student updated successfully!", "success")
    return redirect(url_for("index"))

# Delete student
@app.route("/delete/<int:id>")
def delete_student(id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash("Student deleted!", "warning")
    
    return redirect(url_for("index"))

# Export data to Excel (Download instead of saving)
@app.route("/export")
def export_to_excel():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    db.close()
    
    df = pd.DataFrame(students, columns=["ID", "Name", "Class", "Phone", "Address"])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Students", index=False)
    
    output.seek(0)
    
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=students_data.xlsx"}
    )

# Run Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is not set
    app.run(host="0.0.0.0", port=port)

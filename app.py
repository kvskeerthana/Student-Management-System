from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flash messages

# Function to connect to MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Keerthana_@1",  # Change this to your MySQL password
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

# Export data to Excel
@app.route("/export")
def export_to_excel():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    db.close()
    
    df = pd.DataFrame(students, columns=["ID", "Name", "Class", "Phone", "Address"])
    df.to_excel("students_data.xlsx", index=False)
    
    flash("Data exported successfully!", "success")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect
from datetime import datetime
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        port = 3306,
        password = "######",
        database="appointment_tracker_db"
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add_appointment():
    if request.method == "POST":
        client_name = request.form["client_name"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form["reason"]

        db = get_db_connection()
        cursor = db.cursor()

        sql = "INSERT INTO appointments (client_name, appointment_date, appointment_time, reason) VALUES (%s, %s, %s, %s)"
        values = (client_name, appointment_date, appointment_time, reason)

        cursor.execute(sql, values)
        db.commit()

        cursor.close()
        db.close()

        return redirect("/appointments")

    return render_template("add_appointment.html")

@app.route("/appointments")
def appointments():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM appointments")
    records = cursor.fetchall()

    formatted_records = []

    for row in records:
        time_24 = row[3]  # appointment_time column

        # Convert to 12-hour format
        time_12 = datetime.strptime(str(time_24), "%H:%M:%S").strftime("%I:%M %p")

        # Replace time in row
        new_row = list(row)
        new_row[3] = time_12

        formatted_records.append(new_row)

    cursor.close()
    db.close()

    return render_template("appointments.html", appointments=formatted_records)

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []

    if request.method == "POST":
        client_name = request.form["client_name"]

        db = get_db_connection()
        cursor = db.cursor()

        sql = "SELECT * FROM appointments WHERE client_name LIKE %s"
        value = ("%" + client_name + "%",)

        cursor.execute(sql, value)
        results = cursor.fetchall()

        cursor.close()
        db.close()

    return render_template("search.html", results=results)

@app.route("/edit/<int:appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == "POST":
        client_name = request.form["client_name"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form["reason"]

        sql = "UPDATE appointments SET client_name=%s, appointment_date=%s, appointment_time=%s, reason=%s WHERE appointment_id=%s"
        values = (client_name, appointment_date, appointment_time, reason, appointment_id)

        cursor.execute(sql, values)
        db.commit()

        cursor.close()
        db.close()

        return redirect("/appointments")

    cursor.execute("SELECT * FROM appointments WHERE appointment_id=%s", (appointment_id,))
    appointment = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("edit_appointment.html", appointment=appointment)

@app.route("/delete/<int:appointment_id>")
def delete_appointment(appointment_id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM appointments WHERE appointment_id=%s", (appointment_id,))
    db.commit()

    cursor.close()
    db.close()

    return redirect("/appointments")

if __name__ == "__main__":
    app.run(debug=True)
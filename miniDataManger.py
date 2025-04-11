from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import csv
import json
from fpdf import FPDF
import os

app = Flask(__name__)

# -------------------------
# 1. DATABASE CRUD SECTION
# -------------------------
def init_db():
    with sqlite3.connect('demo.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            email TEXT)''')

def add_user(name, email):
    with sqlite3.connect('demo.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))

def get_users():
    with sqlite3.connect('demo.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        return cursor.fetchall()

# ----------------------------
# 2. FILE EXPORT/TRANSFORM SECTION
# ----------------------------
def export_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Email'])
        writer.writerows(data)

def export_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump([{'id': id, 'name': name, 'email': email} for id, name, email in data], file)

def export_to_pdf(data, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="User Report", ln=True, align='C')
    pdf.ln(10)
    for row in data:
        pdf.cell(200, 10, txt=f"ID: {row[0]} Name: {row[1]} Email: {row[2]}", ln=True)
    pdf.output(filename)

# -------------------------
# 4. FLASK ROUTES
# -------------------------
@app.route('/')
def index():
    users = get_users()
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    email = request.form['email']
    add_user(name, email)
    return redirect('/')

@app.route('/export/<file_type>')
def export(file_type):
    users = get_users()
    filename = f'users.{file_type}'

    if file_type == 'csv':
        export_to_csv(users, filename)
    elif file_type == 'json':
        export_to_json(users, filename)
    elif file_type == 'pdf':
        export_to_pdf(users, filename)
    else:
        return "Invalid file type.", 400

    try:
        return send_file(filename, as_attachment=True)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

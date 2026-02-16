
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib

app = Flask(__name__)
CORS(app)

DATABASE = "expenses.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount REAL, category TEXT, date TEXT, user_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY AUTOINCREMENT, amount REAL, user_id INTEGER)")

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                    (data["username"], hash_password(data["password"])))
        conn.commit()
        return jsonify({"message": "User registered"})
    except:
        return jsonify({"error": "User already exists"})
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                (data["username"], hash_password(data["password"])))
    user = cur.fetchone()
    conn.close()
    if user:
        return jsonify({"user_id": user["id"]})
    return jsonify({"error": "Invalid credentials"})

@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (title, amount, category, date, user_id) VALUES (?, ?, ?, ?, ?)",
                (data["title"], data["amount"], data["category"], data["date"], data["user_id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added"})

@app.route("/get_expenses/<int:user_id>")
def get_expenses(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/delete_expense/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

@app.route("/update_expense/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE expenses SET title=?, amount=?, category=?, date=? WHERE id=?",
                (data["title"], data["amount"], data["category"], data["date"], expense_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

@app.route("/set_budget", methods=["POST"])
def set_budget():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM budget WHERE user_id=?", (data["user_id"],))
    cur.execute("INSERT INTO budget (amount, user_id) VALUES (?, ?)",
                (data["amount"], data["user_id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Budget saved"})

@app.route("/get_budget/<int:user_id>")
def get_budget(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT amount FROM budget WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify({"budget": row["amount"] if row else 0})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

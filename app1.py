# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'user',
    'password': 'Ram@12345',
    'database': 'loginusers'
}

# Home page (login)
@app.route('/')
def login():
    return render_template('login.html')

# Registration page
@app.route('/register')
def register():
    return render_template('register.html')

# Register user (handle form submission)
@app.route('/register', methods=['POST'])
def register_user():
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Retrieve form data
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    retype_password = request.form['retype_password']

    # Check if passwords match
    if password != retype_password:
        return 'Passwords do not match. Please try again.'

    # Check if email is already registered
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return 'Email already registered. Please use a different email.'

    # Insert new user into the database
    cursor.execute("INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
                   (name, email, phone, password))
    conn.commit()

    # Close MySQL connection
    cursor.close()
    conn.close()

    return 'Registration successful!'

# Verify user login
@app.route('/login', methods=['POST'])
def verify_login():
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Retrieve form data
    user = request.form['user']
    password = request.form['password']

    # Verify user login
    cursor.execute("SELECT * FROM users WHERE (name = %s OR email = %s) AND password = %s",
                   (user, user, password))
    authenticated_user = cursor.fetchone()

    if authenticated_user:
        # Store user information in session
        session['user_id'] = authenticated_user[0]
        session['user_name'] = authenticated_user[1]
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid login credentials. Please try again.'

# Dashboard page (after successful login)
@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' in session:
        return f'Welcome, {session["user_name"]}! This is your dashboard.'
    else:
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production


@app.route('/')
def index():
    return redirect(url_for('login'))


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        # Simulate user creation (no database)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # Simulate login validation (no database)
        if email == "test@example.com" and password == "password":
            session['user'] = email
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for('login'))

    return render_template("login.html")


# Forgot Password Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Add logic to handle password reset (e.g., send an email)
        flash("If this email exists, a password reset link has been sent.", "info")
        return redirect(url_for('login'))
    return render_template('ForgotPassword.html')


# Dashboard Route (Protected Page)
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    return f"Welcome, {session['user']}! <br><a href='/logout'>Logout</a>"


# Logout Route
@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
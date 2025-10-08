import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production

app.config
@app.route('/')
def home():  # Renamed this function to avoid conflict
    return redirect(url_for('index'))


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
        return redirect(url_for('index'))

    return render_template('signup.html')


# Login Route
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        # Automatically log in the user and redirect to the products page
        session['user'] = "guest_user"  # Set a default user session
        flash("Login successful!", "success")
        return redirect(url_for('products'))  # Redirect to the products page

    return render_template("index.html")


# Forgot Password Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Add logic to handle password reset (e.g., send an email)
        flash("If this email exists, a password reset link has been sent.", "info")
        return redirect(url_for('index'))
    return render_template('ForgotPassword.html')


# Products Page
@app.route('/products')
def products():
    products = [
        {"name": "Smart Watch", "price": 89, "image": "uploads/smartwatch.jpg"},
        {"name": "Shoes", "price": 59, "image": "uploads/shoes.jpg"},
        {"name": "Laptop", "price": 120, "image": "uploads/laptop.jpg"},
        {"name": "T-Shirts", "price": 15, "image": "uploads/tshirt.jpg"},
        {"name": "Smart Phone", "price": 55, "image": "uploads/smartphone.jpg"},
        {"name": "Pants", "price": 20, "image": "uploads/pants.jpg"},
    ]
    return render_template('Products.html', products=products)

# Upload Route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if "user" not in session:
        flash("Please log in to upload a product.", "warning")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        title = request.form.get('title')
        price = request.form.get('price')
        category = request.form.get('category')
        condition = request.form.get('condition')
        features = request.form.get('features')
        image = request.files.get('image')
        
        if image and image.filename != "":
            # Save the uploaded image to the static/uploads folder
            image_path = f'static/uploads/{image.filename}'
            image.save(image_path)
            flash(f"Product '{title}' uploaded successfully!", "success")
            return redirect(url_for('products'))
        else:
            flash("Please upload an image.", "danger")
            return redirect(url_for('upload'))
    
    return render_template('Upload.html')

# Review Route
@app.route('/review', methods=['GET', 'POST'])
def review():
    if "user" not in session:
        flash("Please log in to submit a review.", "warning")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        rating = request.form['rating']
        comment = request.form['comment']
        flash("Thank you for your review!", "success")
        return redirect(url_for('products'))
    
    return render_template('review.html')

@app.route('/item/<int:item_id>/message', methods=['GET', 'POST'])
def message_seller(item_id):
    if "user" not in session:
        flash("Please log in to send a message.", "warning")
        return redirect(url_for("index"))

       

# Dashboard Route (Protected Page)
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("index"))
    return f"Welcome, {session['user']}! <br><a href='/logout'>Logout</a>"


# Logout Route
@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
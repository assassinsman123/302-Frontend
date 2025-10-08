import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production

# Global list to store all products (default + uploaded)
products_list = [
    {"name": "Smart Watch", "price": 89, "image": "images/daniel-korpai-hbTKIbuMmBI-unsplash.jpg"},
    {"name": "Shoes", "price": 59, "image": "images/kompjuteri-com-Saj5h85DbOs-unsplash.jpg"},
    {"name": "Laptop", "price": 120, "image": "images/matthew-moloney-YeGao3uk8kI-unsplash.jpg"},
    {"name": "T-Shirts", "price": 15, "image": "images/ryan-hoffman-6Nub980bI3I-unsplash.jpg"},
    {"name": "Smart Phone", "price": 55, "image": "images/shiwa-id-Uae7ouMw91A-unsplash.jpg"},
    {"name": "Pants", "price": 20, "image": "images/xavier-teo-SxAXphIPWeg-unsplash.jpg"},
]

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
    return render_template('Products.html', products=products_list)

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
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join('static', 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Save the uploaded image to the static/uploads folder
            image_filename = image.filename
            image_path = os.path.join(upload_dir, image_filename)
            image.save(image_path)
            
            # Add the new product to the global products list
            new_product = {
                "name": title,
                "price": float(price),
                "image": f"uploads/{image_filename}",
                "category": category,
                "condition": condition,
                "features": features
            }
            products_list.append(new_product)
            
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
    
    # Find the product by index (item_id)
    if 0 <= item_id < len(products_list):
        item = products_list[item_id]
        
        if request.method == "POST":
            message = request.form.get('message')
            flash(f"Message sent to seller of '{item['name']}'!", "success")
            return redirect(url_for('products'))
        
        return render_template('ItemMessage.html', item=item, item_id=item_id)
    else:
        flash("Product not found.", "danger")
        return redirect(url_for('products'))

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
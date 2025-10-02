from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production


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
        email = request.form['email']
        password = request.form['password']

        # Simulate login validation (replace with actual database logic)
        if email == "test@example.com" and password == "password":
            session['user'] = email  # Store user session
            flash("Login successful!", "success")
            return redirect(url_for('products'))  # Redirect to the products page
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for('index'))

    return render_template("Index.html")


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
    if 'user' not in session:  # Check if the user is logged in
        flash("Please log in to access the products page.", "warning")
        return redirect(url_for('index'))
    
    product_list = [
        {"name": "Smart Watches", "price": "$89", "image": "https://via.placeholder.com/150"},
        {"name": "shoes",  "price": "$59", "image": "https://via.placeholder.com/150"},
        {"name": "Laptop", "price": "120", "image": "https://via.placeholder.com/150"},
        {"name": "T-Shirt", "price": "15", "image": "https://via.placeholder.com/150"},
        {"name": "Smartphone", "price": "99", "image": "https://via.placeholder.com/150"},
        {"name": "Pants", "price": "20", "image": "https://via.placeholder.com/150"},
    ]
    return render_template('Products.html', products=product_list)  # Pass products to the template


# Upload Route
app.route('/upload', methods=['GET', 'POST'])
def upload():
    if "user" not in session:
        flash("please log in to upload a product.", "warning")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        category = request.form['category']
        condition = request.form['condition']
        features = request.form['features']
        image = request.files['image']
        
    if image:
        image.save(f'static/uploads/{image.filename}')
        flash("Product '{title} uploaded successfully!", "success")
    else:
        flash("Please upload an image.", "danger")
        return redirect(url_for('upload'))
    
    return redirect(url_for('products'))
    
    return render_template('Upload.html')
       

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
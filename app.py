import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production

# Global list to store all products (default + uploaded)
products_list = [
    {"name": "Smart Watch", "price": 89, "image": "images/daniel-korpai-hbTKIbuMmBI-unsplash.jpg"},
    {"name": "Laptop", "price": 59, "image": "images/kompjuteri-com-Saj5h85DbOs-unsplash.jpg"},
    {"name": "Pants", "price": 120, "image": "images/matthew-moloney-YeGao3uk8kI-unsplash.jpg"},
    {"name": "T-Shirts", "price": 15, "image": "images/ryan-hoffman-6Nub980bI3I-unsplash.jpg"},
    {"name": "Smart Phone", "price": 55, "image": "images/shiwa-id-Uae7ouMw91A-unsplash.jpg"},
    {"name": "Shoes", "price": 20, "image": "images/xavier-teo-SxAXphIPWeg-unsplash.jpg"},
]

# Global dictionary to store user wishlists (session-based)
user_wishlists = {}

# Global dictionary to store chat messages
# Format: {item_id: [{"sender": "user_id", "content": "message", "timestamp": "time"}]}
chat_messages = {}

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
        
        # Check if item is in user's wishlist
        user = session['user']
        is_in_wishlist = False
        if user in user_wishlists and item_id in user_wishlists[user]:
            is_in_wishlist = True
        
        if request.method == "POST":
            message = request.form.get('message')
            
            # Initialize message list for this item if it doesn't exist
            if item_id not in chat_messages:
                chat_messages[item_id] = []
                # Add welcome message if this is the first interaction
                welcome_message = {
                    "sender": "seller",
                    "content": f"Hi! Thanks for your interest in {item['name']}. How can I help you?",
                    "timestamp": datetime.now().strftime("%H:%M")
                }
                chat_messages[item_id].append(welcome_message)
            
            # Add user's message to the chat
            if message and message.strip():
                user_message = {
                    "sender": session['user'],
                    "content": message.strip(),
                    "timestamp": datetime.now().strftime("%H:%M")
                }
                chat_messages[item_id].append(user_message)
            
            flash(f"Message sent! Redirecting to chat with seller.", "success")
            return redirect(url_for('chat_with_seller', item_id=item_id))
        
        return render_template('ItemMessage.html', item=item, item_id=item_id, is_in_wishlist=is_in_wishlist)
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

# Wishlist Routes
@app.route('/wishlist')
def wishlist():
    if "user" not in session:
        flash("Please log in to view your wishlist.", "warning")
        return redirect(url_for("index"))
    
    user = session['user']
    user_wishlist_items = user_wishlists.get(user, [])
    
    # Get full product details for wishlist items
    wishlist_products = []
    for item_id in user_wishlist_items:
        if 0 <= item_id < len(products_list):
            product = products_list[item_id].copy()
            product['item_id'] = item_id
            wishlist_products.append(product)
    
    return render_template('Wishlist.html', products=wishlist_products)

@app.route('/add_to_wishlist/<int:item_id>')
def add_to_wishlist(item_id):
    if "user" not in session:
        if request.headers.get('Content-Type') == 'application/json' or request.args.get('ajax'):
            return jsonify({"success": False, "message": "Please log in to add items to wishlist."}), 401
        flash("Please log in to add items to wishlist.", "warning")
        return redirect(url_for("index"))
    
    user = session['user']
    if user not in user_wishlists:
        user_wishlists[user] = []
    
    if 0 <= item_id < len(products_list):
        if item_id not in user_wishlists[user]:
            user_wishlists[user].append(item_id)
            message = f"Added {products_list[item_id]['name']} to your wishlist!"
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.args:
                return jsonify({"success": True, "message": message})
            
            flash(message, "success")
        else:
            message = "Item is already in your wishlist!"
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.args:
                return jsonify({"success": False, "message": message})
                
            flash(message, "info")
    else:
        message = "Product not found."
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.args:
            return jsonify({"success": False, "message": message})
            
        flash(message, "danger")
    
    return redirect(request.referrer or url_for('products'))

@app.route('/remove_from_wishlist/<int:item_id>')
def remove_from_wishlist(item_id):
    if "user" not in session:
        flash("Please log in to manage your wishlist.", "warning")
        return redirect(url_for("index"))
    
    user = session['user']
    if user in user_wishlists and item_id in user_wishlists[user]:
        user_wishlists[user].remove(item_id)
        flash(f"Removed {products_list[item_id]['name']} from your wishlist!", "success")
    else:
        flash("Item not found in your wishlist.", "info")
    
    return redirect(request.referrer or url_for('wishlist'))

@app.route('/toggle_wishlist/<int:item_id>')
def toggle_wishlist(item_id):
    if "user" not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.args:
            return jsonify({"success": False, "message": "Please log in to manage your wishlist."}), 401
        flash("Please log in to manage your wishlist.", "warning")
        return redirect(url_for("index"))
    
    user = session['user']
    if user not in user_wishlists:
        user_wishlists[user] = []
    
    if 0 <= item_id < len(products_list):
        is_in_wishlist = item_id in user_wishlists[user]
        
        if is_in_wishlist:
            # Remove from wishlist
            user_wishlists[user].remove(item_id)
            message = f"Removed {products_list[item_id]['name']} from your wishlist!"
            action = "removed"
        else:
            # Add to wishlist
            user_wishlists[user].append(item_id)
            message = f"Added {products_list[item_id]['name']} to your wishlist!"
            action = "added"
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.args:
            return jsonify({
                "success": True, 
                "message": message, 
                "action": action,
                "is_in_wishlist": not is_in_wishlist
            })
        
        flash(message, "success")
    else:
        message = "Product not found."
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'ajax' in request.args:
            return jsonify({"success": False, "message": message})
            
        flash(message, "danger")
    
    return redirect(request.referrer or url_for('products'))

# Chat with Seller Route
@app.route('/chat/<int:item_id>')
def chat_with_seller(item_id):
    if "user" not in session:
        flash("Please log in to chat with seller.", "warning")
        return redirect(url_for("index"))
    
    # Find the product by index (item_id)
    if 0 <= item_id < len(products_list):
        item = products_list[item_id]
        
        # Get existing messages for this item
        messages = chat_messages.get(item_id, [])
        
        # Add welcome message if no messages exist
        if not messages:
            welcome_message = {
                "sender": "seller",
                "content": f"Hi! Thanks for your interest in {item['name']}. How can I help you?",
                "timestamp": datetime.now().strftime("%H:%M")
            }
            chat_messages[item_id] = [welcome_message]
            messages = chat_messages[item_id]
        
        return render_template('SellerMessage.html', item=item, item_id=item_id, messages=messages)
    else:
        flash("Product not found.", "danger")
        return redirect(url_for('products'))

# API endpoint for sending messages (for future AJAX implementation)
@app.route('/api/send_message/<int:item_id>', methods=['POST'])
def send_message_api(item_id):
    if "user" not in session:
        return jsonify({"success": False, "message": "Please log in"}), 401
    
    data = request.get_json()
    message_content = data.get('message', '').strip()
    
    if not message_content:
        return jsonify({"success": False, "message": "Message cannot be empty"}), 400
    
    if not (0 <= item_id < len(products_list)):
        return jsonify({"success": False, "message": "Product not found"}), 404
    
    # Initialize message list for this item if it doesn't exist
    if item_id not in chat_messages:
        chat_messages[item_id] = []
    
    # Add user message to the chat
    user_message = {
        "sender": session['user'],
        "content": message_content,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    chat_messages[item_id].append(user_message)
    
    return jsonify({
        "success": True, 
        "message": "Message sent successfully",
        "timestamp": user_message["timestamp"]
    })


# Logout Route
@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
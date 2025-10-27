import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this in production

# Configure Flask for UTF-8 encoding
app.config['JSON_AS_ASCII'] = False

# Configure session to be permanent and set timeout
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# Helper function to ensure user session exists
def ensure_user_session():
    if "user" not in session:
        session['user'] = f"user_{int(time.time())}"
    return session['user']

# Global list to store all products (default + uploaded)
products_list = [
    {
        "name": "Smart Watch", 
        "price": 89, 
        "image": "images/daniel-korpai-hbTKIbuMmBI-unsplash.jpg",
        "category": "Electronics",
        "condition": "Excellent",
        "features": "Heart rate monitor, GPS tracking, Waterproof design, 7-day battery life"
    },
    {
        "name": "Laptop", 
        "price": 59, 
        "image": "images/kompjuteri-com-Saj5h85DbOs-unsplash.jpg",
        "category": "Electronics",
        "condition": "Good",
        "features": "Intel Core i5, 8GB RAM, 256GB SSD, Full HD display, Lightweight design"
    },
    {
        "name": "Pants", 
        "price": 20, 
        "image": "images/matthew-moloney-YeGao3uk8kI-unsplash.jpg",
        "category": "Clothing",
        "condition": "New",
        "features": "Premium cotton blend, Tailored fit, Multiple color options, Machine washable"
    },
    {
        "name": "T-Shirts", 
        "price": 15, 
        "image": "images/ryan-hoffman-6Nub980bI3I-unsplash.jpg",
        "category": "Clothing",
        "condition": "Excellent",
        "features": "100% organic cotton, Comfortable fit, Pre-shrunk, Various sizes available"
    },
    {
        "name": "Smart Phone", 
        "price": 55, 
        "image": "images/shiwa-id-Uae7ouMw91A-unsplash.jpg",
        "category": "Electronics",
        "condition": "Good",
        "features": "Latest Android OS, Dual camera, 128GB storage, Fast charging, Unlocked"
    },
    {
        "name": "Shoes", 
        "price": 20, 
        "image": "images/xavier-teo-SxAXphIPWeg-unsplash.jpg",
        "category": "Fashion",
        "condition": "Used",
        "features": "Comfortable sole, Durable materials, Classic design, Multiple sizes"
    },
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
        # Create session for the new user
        session.permanent = True
        session['user'] = email  # Use email as user identifier
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('index'))

    return render_template('signup.html')


# Login Route
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        # Create a permanent session for the user
        session.permanent = True
        user = ensure_user_session()
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


# Search Route
@app.route('/search')
def search():
    query = request.args.get('q', '').lower().strip()
    category = request.args.get('category', '').lower().strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    filtered_products = []
    
    for i, product in enumerate(products_list):
        # Text search in name, category, condition, and features
        if query:
            searchable_text = f"{product['name']} {product['category']} {product['condition']} {product['features']}".lower()
            if query not in searchable_text:
                continue
        
        # Category filter
        if category and category != product['category'].lower():
            continue
        
        # Price range filter
        if min_price and product['price'] < float(min_price):
            continue
        if max_price and product['price'] > float(max_price):
            continue
        
        # Add item_id for frontend use
        product_with_id = product.copy()
        product_with_id['item_id'] = i
        filtered_products.append(product_with_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'products': filtered_products,
            'count': len(filtered_products)
        })
    
    return render_template('Products.html', products=filtered_products)

# Products Page
@app.route('/products')
def products():
    # Ensure user session exists (auto-create if needed)
    ensure_user_session()
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
    seller_name = request.args.get('seller')
    item_id = request.args.get('item_id')
    
    if request.method == "POST":
        if "user" not in session:
            flash("Please log in to submit a review.", "warning")
            return redirect(url_for("index"))
        
        rating = request.form['rating']
        comment = request.form['comment']
        flash("Thank you for your seller review!", "success")
        return redirect(url_for('products'))
    
    # Get product information if item_id is provided
    product_info = None
    if item_id:
        try:
            item_index = int(item_id)
            if 0 <= item_index < len(products_list):
                product_info = products_list[item_index]
        except (ValueError, TypeError):
            pass
    
    # Sample seller reviews data - Fair and Critical
    seller_reviews = {
        'Alex Thompson': [
            ('Jessica M.', 5, 'Excellent seller! The laptop was exactly as described and in perfect condition. Quick and professional transaction.'),
            ('Mike R.', 4, 'Good communication and the smartwatch works well, but pickup took longer than expected. Item had minor scratches not mentioned.'),
            ('Sarah K.', 3, 'Item was functional but condition was worse than described. Seller was responsive but should be more accurate about wear.'),
            ('David L.', 5, 'Outstanding seller! Very knowledgeable about electronics and provided great support after purchase.'),
            ('Amy T.', 2, 'Phone had battery issues that weren\'t disclosed. Seller refused partial refund. Disappointing experience.'),
            ('Chris W.', 4, 'Decent transaction overall. Item worked as expected but packaging could have been better for electronics.'),
            ('Lisa H.', 3, 'Seller was late to pickup meeting and item had more wear than photos showed. Works fine though.')
        ],
        'Sarah Johnson': [
            ('Emily T.', 5, 'Amazing clothes in perfect condition! Great style and exactly my size. Highly recommend!'),
            ('Lisa P.', 3, 'Clothing items were okay but had some stains not visible in photos. Seller was apologetic and offered small discount.'),
            ('Amanda S.', 4, 'Good fashion sense and reasonable prices. One item smelled like cigarette smoke but aired out fine.'),
            ('Rachel M.', 5, 'Professional and responsive. The accessories were exactly what I was looking for.'),
            ('Jordan K.', 2, 'Sizes were completely wrong despite asking for measurements. Had to return items. Wasted my time.'),
            ('Taylor B.', 4, 'Nice selection but some items were more worn than expected. Fair prices though.'),
            ('Morgan F.', 3, 'Clothes were clean but had pet hair all over them. Seller should mention having pets.')
        ],
        'Mike Chen': [
            ('John D.', 4, 'Reliable seller with good everyday items. Fair prices and convenient pickup location.'),
            ('Maria G.', 3, 'Items were as described but seller was 30 minutes late without notice. Communication could be better.'),
            ('Tom W.', 4, 'Good experience overall. Item had minor issues but seller was honest about condition.'),
            ('Nina F.', 2, 'Seller cancelled last minute twice. When we finally met, item wasn\'t as clean as expected.'),
            ('Alex R.', 5, 'Excellent service! Fast response and items were better than described. Very trustworthy.'),
            ('Sam L.', 3, 'Okay transaction but seller seemed disorganized. Had to remind them about our meeting time.'),
            ('Pat M.', 4, 'Fair prices and honest about item conditions. Would buy again but expect minor delays.')
        ],
        'Emily Davis': [
            ('Alex C.', 5, 'Very detailed and professional seller. The books were in excellent condition with accurate descriptions.'),
            ('Grace H.', 3, 'Books were okay but had more highlighting and notes than mentioned. Seller was understanding about complaint.'),
            ('Chris B.', 4, 'Good attention to detail but prices are a bit high for used items. Quality is consistent though.'),
            ('Zoe L.', 2, 'Several books had missing pages that weren\'t disclosed. Seller needs to check items more carefully.'),
            ('River J.', 4, 'Professional transaction and items exactly as described. Pickup was smooth and efficient.'),
            ('Sage K.', 3, 'Items were clean but seller is very picky about pickup times. Limited flexibility.'),
            ('Avery N.', 5, 'Outstanding seller! Goes above and beyond to ensure customer satisfaction. Highly recommended.')
        ],
        'David Wilson': [
            ('Kevin M.', 4, 'Good tech knowledge but phone had some software issues not mentioned. Seller helped resolve them.'),
            ('Ashley R.', 5, 'Premium quality electronics at great prices. Excellent seller with fast service and honest descriptions.'),
            ('Ryan P.', 2, 'Laptop had overheating problems that seller claimed to not know about. Felt misled about condition.'),
            ('Megan T.', 4, 'Professional tech seller but prices are on the higher side. Quality justifies cost though.'),
            ('Blake S.', 3, 'Electronics work but had to factory reset due to previous owner\'s data still on device. Awkward.'),
            ('Casey D.', 5, 'Excellent experience! Seller provided original chargers and boxes. Very thorough testing before sale.'),
            ('Quinn R.', 3, 'Item worked but seller was pushy about quick pickup and payment. Felt rushed during transaction.')
        ],
        'Lisa Garcia': [
            ('Sophie J.', 4, 'Great shoe collection but some items had odor issues. Seller offered to clean them which was nice.'),
            ('Isabella W.', 3, 'Shoes were authentic but more worn than photos suggested. Seller should take better pictures.'),
            ('Olivia M.', 5, 'Authentic designer items at great prices! Seller is knowledgeable about fashion and very helpful.'),
            ('Chloe D.', 2, 'Shoes didn\'t fit despite seller saying they ran true to size. No returns policy was disappointing.'),
            ('Harper L.', 4, 'Good selection and fair prices. One pair had a loose sole but seller offered partial refund.'),
            ('Peyton M.', 3, 'Items were clean but seller was very particular about meeting locations. Limited to her schedule only.'),
            ('Emery C.', 5, 'Excellent taste in fashion! Items were exactly as described and seller included shoe care tips.')
        ]
    }
    
    # Get reviews for the specific seller
    seller_review_list = seller_reviews.get(seller_name, [])
    
    # Calculate average rating
    seller_avg_rating = 0
    
    if seller_review_list:
        total_rating = sum(review[1] for review in seller_review_list)
        seller_avg_rating = round(total_rating / len(seller_review_list), 1)
    
    return render_template('review.html', 
                         seller_name=seller_name, 
                         seller_reviews=seller_review_list, 
                         seller_avg_rating=seller_avg_rating,
                         seller_review_count=len(seller_review_list),
                         product_info=product_info,
                         item_id=item_id)

@app.route('/item/<int:item_id>/message', methods=['GET', 'POST'])
def message_seller(item_id):
    # Ensure user session exists
    user = ensure_user_session()
    
    # Find the product by index (item_id)
    if 0 <= item_id < len(products_list):
        item = products_list[item_id]
        
        # Check if item is in user's wishlist
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
    # Ensure user session exists (auto-create if needed)
    user = ensure_user_session()
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
    # Ensure user session exists (auto-create if needed)
    user = ensure_user_session()
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
    # Ensure user session exists (auto-create if needed)
    user = ensure_user_session()
    if user in user_wishlists and item_id in user_wishlists[user]:
        user_wishlists[user].remove(item_id)
        flash(f"Removed {products_list[item_id]['name']} from your wishlist!", "success")
    else:
        flash("Item not found in your wishlist.", "info")
    
    return redirect(request.referrer or url_for('wishlist'))

@app.route('/toggle_wishlist/<int:item_id>')
def toggle_wishlist(item_id):
    # Ensure user session exists (auto-create if needed)
    user = ensure_user_session()
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
    # Ensure user session exists
    user = ensure_user_session()
    
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

# Global dictionary to store booking alerts
# Format: {user_id: {item_id: {"item_name": "name", "email": "email", "enabled": True, "date_created": "timestamp"}}}
booking_alerts = {}

# Global dictionary to store reservations/cart items
# Format: {item_id: [{"user": "user_id", "pickup_date": "date", "pickup_time": "time", "status": "pending/confirmed"}]}
reservations = {}

# API endpoint to enable booking alerts
@app.route('/api/enable_booking_alert', methods=['POST'])
def enable_booking_alert():
    if "user" not in session:
        return jsonify({"success": False, "message": "Please log in"}), 401
    
    data = request.get_json()
    item_id = data.get('item_id')
    item_name = data.get('item_name')
    user_email = data.get('user_email')
    
    if not all([item_id, item_name]):
        return jsonify({"success": False, "message": "Missing required data"}), 400
    
    user = session['user']
    
    # Initialize user's booking alerts if not exists
    if user not in booking_alerts:
        booking_alerts[user] = {}
    
    # Save the booking alert
    booking_alerts[user][str(item_id)] = {
        "item_name": item_name,
        "email": user_email,
        "enabled": True,
        "date_created": datetime.now().isoformat()
    }
    
    # Simulate sending email confirmation (in real app, you'd use an email service)
    print(f"📧 Booking alert enabled for {user} - Item: {item_name}, Email: {user_email}")
    
    return jsonify({
        "success": True, 
        "message": f"Booking alerts enabled for {item_name}",
        "email_sent": bool(user_email)
    })

# API endpoint to create a reservation/booking
@app.route('/api/create_reservation', methods=['POST'])
def create_reservation():
    if "user" not in session:
        return jsonify({"success": False, "message": "Please log in"}), 401
    
    data = request.get_json()
    item_id = data.get('item_id')
    pickup_date = data.get('pickup_date')
    pickup_time = data.get('pickup_time')
    pickup_location = data.get('pickup_location')
    email = data.get('email')
    notes = data.get('notes', '')
    
    if not all([item_id, pickup_date, pickup_time, pickup_location, email]):
        return jsonify({"success": False, "message": "Missing required booking information"}), 400
    
    user = session['user']
    
    # Initialize reservations for this item if not exists
    if item_id not in reservations:
        reservations[item_id] = []
    
    # Create new reservation
    reservation = {
        "user": user,
        "email": email,
        "pickup_date": pickup_date,
        "pickup_time": pickup_time,
        "pickup_location": pickup_location,
        "notes": notes,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "reservation_id": f"RES{len(reservations[item_id]) + 1:03d}"
    }
    
    reservations[item_id].append(reservation)
    
    # Send email alerts to users who have enabled booking alerts for this item
    item_name = "Unknown Item"
    if 0 <= int(item_id) < len(products_list):
        item_name = products_list[int(item_id)]['name']
    
    # Get location name for email
    location_map = {
        'campus-main': 'Main Campus - Student Center',
        'campus-library': 'Campus Library - Front Entrance', 
        'campus-parking': 'Main Parking Lot - Near Entrance',
        'downtown-cafe': 'Downtown Cafe - Central Square',
        'mall-entrance': 'Shopping Mall - Main Entrance',
        'park-meetup': 'City Park - Main Pavilion',
        'other': 'Other Location (see notes)'
    }
    location_name = location_map.get(pickup_location, pickup_location)
    
    # Check all users who have booking alerts for this item
    alerts_sent = 0
    for alert_user, user_alerts in booking_alerts.items():
        if str(item_id) in user_alerts and user_alerts[str(item_id)]['enabled']:
            alert_email = user_alerts[str(item_id)]['email']
            
            # Don't send alert to the person who made the booking
            if alert_email != email:
                # Send detailed booking alert email
                print(f"📧 BOOKING ALERT EMAIL:")
                print(f"   To: {alert_email}")
                print(f"   Subject: 🔔 BOOKING ALERT: '{item_name}' has been reserved!")
                print(f"   Body:")
                print(f"   Hello!")
                print(f"   ")
                print(f"   🔔 The item you're watching has been booked by someone else:")
                print(f"   ")
                print(f"   📦 Item: {item_name}")
                print(f"   📅 Pickup Date: {pickup_date}")
                print(f"   ⏰ Pickup Time: {pickup_time}")
                print(f"   📍 Pickup Location: {location_name}")
                print(f"   🆔 Reservation ID: {reservation['reservation_id']}")
                print(f"   ")
                print(f"   ⚠️ This item is no longer available for the specified pickup time.")
                print(f"   ")
                print(f"   If you're still interested in this item, you may want to:")
                print(f"   • Contact the seller for alternative pickup times")
                print(f"   • Check if similar items are available")
                print(f"   • Set up alerts for other items you're interested in")
                print(f"   ")
                print(f"   You received this alert because you enabled booking notifications")
                print(f"   for this item. To manage your alerts, visit the notification center.")
                print(f"   ")
                print(f"   ---")
                print(f"   This is an automated notification from your booking alert system.")
                print("   " + "="*60)
                alerts_sent += 1
                
                # Mark alert as sent (optional tracking)
                user_alerts[str(item_id)]['last_alert_sent'] = datetime.now().isoformat()
    
    # Also send confirmation email to the person who made the booking
    print(f"📧 BOOKING CONFIRMATION EMAIL:")
    print(f"   To: {email}")
    print(f"   Subject: ✅ Booking Confirmed: {item_name}")
    print(f"   Body:")
    print(f"   Thank you for your reservation!")
    print(f"   ")
    print(f"   ✅ Your pickup has been successfully scheduled:")
    print(f"   ")
    print(f"   📦 Item: {item_name}")
    print(f"   📅 Pickup Date: {pickup_date}")
    print(f"   ⏰ Pickup Time: {pickup_time}")
    print(f"   📍 Pickup Location: {location_name}")
    print(f"   🆔 Reservation ID: {reservation['reservation_id']}")
    print(f"   📝 Additional Notes: {notes if notes else 'None'}")
    print(f"   ")
    print(f"   Please save this confirmation email for your records.")
    print(f"   ")
    print(f"   📋 What to bring for pickup:")
    print(f"   • Valid ID for verification")
    print(f"   • This confirmation email or reservation ID")
    print(f"   • Any agreed-upon payment")
    print(f"   ")
    print(f"   If you need to modify or cancel your reservation, please contact us")
    print(f"   as soon as possible with your reservation ID.")
    print(f"   ")
    print(f"   Thank you for choosing our service!")
    print("   " + "="*60)
    
    return jsonify({
        "success": True, 
        "message": "Reservation created successfully",
        "reservation_id": reservation['reservation_id'],
        "alerts_sent": alerts_sent,
        "pickup_details": {
            "date": pickup_date,
            "time": pickup_time,
            "location": location_name,
            "item": item_name
        }
    })

# API endpoint to get user's reservations
@app.route('/api/my_reservations')
def get_my_reservations():
    if "user" not in session:
        return jsonify({"success": False, "message": "Please log in"}), 401
    
    user = session['user']
    user_reservations = []
    
    for item_id, item_reservations in reservations.items():
        for reservation in item_reservations:
            if reservation['user'] == user:
                # Get item details
                item_name = "Unknown Item"
                if 0 <= int(item_id) < len(products_list):
                    item_name = products_list[int(item_id)]['name']
                
                user_reservations.append({
                    "item_id": item_id,
                    "item_name": item_name,
                    "pickup_date": reservation['pickup_date'],
                    "pickup_time": reservation['pickup_time'],
                    "status": reservation['status'],
                    "reservation_id": reservation['reservation_id']
                })
    
    return jsonify({
        "success": True,
        "reservations": user_reservations
    })

# API endpoint to disable booking alert
@app.route('/api/disable_booking_alert', methods=['POST'])
def disable_booking_alert():
    if "user" not in session:
        return jsonify({"success": False, "message": "Please log in"}), 401
    
    data = request.get_json()
    item_id = data.get('item_id')
    
    if not item_id:
        return jsonify({"success": False, "message": "Item ID is required"}), 400
    
    user = session['user']
    
    # Remove or disable alert for this user and item
    if user in booking_alerts and str(item_id) in booking_alerts[user]:
        del booking_alerts[user][str(item_id)]
        
        # If user has no more alerts, remove user entry
        if not booking_alerts[user]:
            del booking_alerts[user]
            
        return jsonify({
            "success": True,
            "message": "Booking alert disabled successfully"
        })
    else:
        return jsonify({
            "success": False,
            "message": "No booking alert found for this item"
        })

# API endpoint to get current user information
@app.route('/api/current_user')
def get_current_user():
    if "user" in session:
        return jsonify({
            "success": True,
            "user": session['user']
        })
    else:
        return jsonify({
            "success": False,
            "user": ""
        })


# Logout Route
@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# Reminder Route
@app.route('/reminder')
def reminder():
    if "user" not in session:
        flash("Please log in to access notifications.", "warning")
        return redirect(url_for("index"))
    return render_template('reminder.html')

# Your Listings Route
@app.route('/your-listings')
def your_listings():
    if "user" not in session:
        flash("Please log in to view your listings.", "warning")
        return redirect(url_for("index"))
    
    # For now, display all products as example
    # In a real app, you would filter products by the logged-in user
    return render_template('YourListings.html', products=products_list)

# Customer Support Route
@app.route('/customer-support')
def customer_support():
    # Ensure user session exists (auto-create if needed)
    ensure_user_session()
    return render_template('CustomerSupport.html')


if __name__ == "__main__":
    app.run(debug=True)
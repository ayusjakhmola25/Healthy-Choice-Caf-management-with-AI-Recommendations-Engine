from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os
import random
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'  # Change to a secure key in production

# Configure SQLAlchemy - Using MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ayush123@localhost:3306/cafe_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# FoodItem Model
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Integer)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String(200))  # Image ka path
    rating = db.Column(db.Float)
    protein = db.Column(db.Float)  # Protein in grams
    carbs = db.Column(db.Float)    # Carbohydrates in grams
    fats = db.Column(db.Float)     # Fats in grams
    calories = db.Column(db.Integer)  # Calories

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))

# LoginHistory Model
class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    login_time = db.Column(db.DateTime, default=db.func.current_timestamp())

# GuestOrder Model
class GuestOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    order_data = db.Column(db.Text, nullable=False)  # JSON string of cart items
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    diet_preference = db.Column(db.String(20))  # 'diet', 'non-diet', or None
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())



# In-memory storage for OTP (temporary)
otp_store = {}
login_otp_store = {}

# Generate random 4-digit OTP
def generate_otp():
    return str(random.randint(1000, 9999))

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    otp = generate_otp()
    otp_id = str(int(time.time() * 1000))

    otp_store[otp_id] = {
        'otp': otp,
        'mobile': mobile,
        'expiry': time.time() + 120  # 2 minutes
    }

    print(f"OTP for {mobile}: {otp}")

    return jsonify({
        'success': True,
        'otpId': otp_id,
        'otp': otp,  # Include OTP for testing (remove in production)
        'message': 'OTP sent successfully'
    })

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp_id = data.get('otpId')
    otp = data.get('otp')

    if not otp_id or not otp:
        return jsonify({'error': 'OTP ID and OTP are required'}), 400

    stored_otp = otp_store.get(otp_id)

    if not stored_otp:
        return jsonify({'error': 'Invalid OTP ID'}), 400

    if time.time() > stored_otp['expiry']:
        del otp_store[otp_id]
        return jsonify({'error': 'OTP expired'}), 400

    if stored_otp['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    # OTP verified successfully
    del otp_store[otp_id]
    return jsonify({'success': True, 'message': 'OTP verified successfully'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    mobile = data.get('mobile')
    email = data.get('email')

    if not name or not mobile or not email:
        return jsonify({'error': 'Name, mobile, and email are required'}), 400

    try:
        # Check if guest order already exists
        existing_guest = GuestOrder.query.filter((GuestOrder.mobile == mobile) | (GuestOrder.email == email)).first()
        if existing_guest:
            return jsonify({'error': 'You have already placed a guest order. Please login instead.'}), 400

        # Check if user already exists
        existing_user = User.query.filter((User.mobile == mobile) | (User.email == email)).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        # Create new user
        new_user = User(name=name, mobile=mobile, email=email)
        db.session.add(new_user)
        db.session.commit()

        print(f"User registered: {name}, {mobile}, {email}")

        return jsonify({'success': True, 'message': 'User registered successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error registering user: {e}")
        return jsonify({'error': 'Failed to register user'}), 500

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    try:
        user = User.query.filter_by(mobile=mobile).first()

        if user:
            user_data = {
                'id': user.id,
                'name': user.name,
                'mobile': user.mobile,
                'email': user.email,
                'dob': user.dob.isoformat() if user.dob else None,
                'gender': user.gender
            }
            return jsonify({'exists': True, 'user': user_data})
        else:
            return jsonify({'exists': False})
    except Exception as e:
        print(f"Error checking user: {e}")
        return jsonify({'error': 'Failed to check user'}), 500

@app.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    mobile = data.get('mobile')
    name = data.get('name')
    dob = data.get('dob')
    gender = data.get('gender')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    try:
        user = User.query.filter_by(mobile=mobile).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update user fields
        if name:
            user.name = name
        if dob:
            from datetime import datetime
            user.dob = datetime.strptime(dob, '%Y-%m-%d').date()
        if gender:
            user.gender = gender

        db.session.commit()

        updated_user = {
            'id': user.id,
            'name': user.name,
            'mobile': user.mobile,
            'email': user.email,
            'dob': user.dob.isoformat() if user.dob else None,
            'gender': user.gender
        }

        print(f"Profile updated for {mobile}: {name}, {dob}, {gender}")

        return jsonify({'success': True, 'message': 'Profile updated successfully', 'user': updated_user})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    try:
        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            return jsonify({'error': 'User not registered'}), 404

        otp = generate_otp()
        otp_id = str(int(time.time() * 1000))

        login_otp_store[otp_id] = {
            'otp': otp,
            'mobile': mobile,
            'expiry': time.time() + 120  # 2 minutes
        }

        print(f"Login OTP for {mobile}: {otp}")

        return jsonify({
            'success': True,
            'otpId': otp_id,
            'otp': otp,  # Include OTP for testing (remove in production)
            'message': 'Login OTP sent successfully'
        })
    except Exception as e:
        print(f"Error sending login OTP: {e}")
        return jsonify({'error': 'Failed to send login OTP'}), 500

@app.route('/verify-login-otp', methods=['POST'])
def verify_login_otp():
    data = request.get_json()
    otp_id = data.get('otpId')
    otp = data.get('otp')

    if not otp_id or not otp:
        return jsonify({'error': 'OTP ID and OTP are required'}), 400

    stored_otp = login_otp_store.get(otp_id)

    if not stored_otp:
        return jsonify({'error': 'Invalid OTP ID'}), 400

    if time.time() > stored_otp['expiry']:
        del login_otp_store[otp_id]
        return jsonify({'error': 'OTP expired'}), 400

    if stored_otp['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400

    try:
        user = User.query.filter_by(mobile=stored_otp['mobile']).first()
        user_id = user.id

        # Record login history
        login_history = LoginHistory(user_id=user_id)
        db.session.add(login_history)
        db.session.commit()

        # Store user name in session
        session['user_name'] = user.name
        session['user_id'] = user_id

        del login_otp_store[otp_id]

        print(f"User logged in: {stored_otp['mobile']}")

        return jsonify({'success': True, 'message': 'Login successful', 'userId': user_id})
    except Exception as e:
        db.session.rollback()
        print(f"Error verifying login OTP: {e}")
        return jsonify({'error': 'Failed to verify login OTP'}), 500

@app.route('/login-count', methods=['POST'])
def login_count():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    try:
        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            return jsonify({'loginCount': 0})
        login_count_value = LoginHistory.query.filter_by(user_id=user.id).count()
        return jsonify({'loginCount': login_count_value})
    except Exception as e:
        print(f"Error fetching login count: {e}")
        return jsonify({'error': 'Failed to fetch login count'}), 500

@app.route('/get-login-history', methods=['POST'])
def get_login_history():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    try:
        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            return jsonify({'loginHistory': []})

        login_history = LoginHistory.query.filter_by(user_id=user.id).order_by(LoginHistory.login_time.desc()).all()
        history_data = [{
            'id': entry.id,
            'login_time': entry.login_time.isoformat()
        } for entry in login_history]
        return jsonify({'loginHistory': history_data})
    except Exception as e:
        print(f"Error fetching login history: {e}")
        return jsonify({'error': 'Failed to fetch login history'}), 500

@app.route('/food-items', methods=['GET'])
def get_food_items():
    try:
        items = FoodItem.query.all()
        food_items = [{
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'price': item.price,
            'description': item.description,
            'image_url': item.image_url,
            'rating': item.rating,
            'protein': item.protein,
            'carbs': item.carbs,
            'fats': item.fats,
            'calories': item.calories
        } for item in items]
        return jsonify(food_items)
    except Exception as e:
        print(f"Error fetching food items: {e}")
        return jsonify({'error': 'Failed to fetch food items'}), 500

@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    data = request.get_json()
    order_items = data.get('orderItems')
    total_amount = data.get('totalAmount')
    payment_method = data.get('paymentMethod')
    customer_name = data.get('customerName')
    customer_mobile = data.get('customerMobile')

    if not order_items or not total_amount or not payment_method:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Create PDF
        filename = f"invoice_{int(time.time())}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Header
        title_style = styles['Heading1']
        title_style.alignment = 1  # Center alignment
        title = Paragraph("Cafe Zone", title_style)
        story.append(title)

        subtitle = Paragraph("Invoice", styles['Heading2'])
        story.append(subtitle)
        story.append(Spacer(1, 12))

        # Invoice details
        invoice_info = [
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Time: {datetime.now().strftime('%H:%M:%S')}",
            f"Invoice #: CZ{int(time.time() * 1000)}"
        ]

        if customer_name:
            invoice_info.append(f"Customer: {customer_name}")
        if customer_mobile:
            invoice_info.append(f"Mobile: {customer_mobile}")

        for info in invoice_info:
            story.append(Paragraph(info, styles['Normal']))
        story.append(Spacer(1, 12))

        # Order details header
        story.append(Paragraph("Order Details:", styles['Heading3']))
        story.append(Spacer(1, 6))

        # Table data
        table_data = [['Item', 'Qty', 'Price', 'Total']]
        for item in order_items:
            table_data.append([
                item['name'],
                str(item['quantity']),
                f"₹{item['price']}",
                f"₹{(item['price'] * item['quantity']):.2f}"
            ])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

        # Calculate amounts
        subtotal = float(total_amount) - 50  # Subtract delivery fee
        gst_amount = subtotal * 0.18
        delivery_fee = 50

        amounts = [
            f"Subtotal: ₹{subtotal:.2f}",
            f"GST (18%): ₹{gst_amount:.2f}",
            f"Delivery Fee: ₹{delivery_fee:.2f}",
            f"Total Amount: ₹{total_amount}"
        ]

        for amount in amounts:
            story.append(Paragraph(amount, styles['Normal']))
        story.append(Spacer(1, 6))

        story.append(Paragraph(f"Payment Method: {payment_method}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Footer
        footer_style = styles['Normal']
        footer_style.fontSize = 8
        footer_style.textColor = colors.gray
        story.append(Paragraph("Thank you for choosing Cafe Zone!", footer_style))
        story.append(Paragraph("For any queries, contact us at support@cafezone.com", footer_style))

        doc.build(story)

        # Read PDF as base64
        with open(filename, 'rb') as f:
            pdf_data = f.read()
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Clean up
        os.remove(filename)

        return jsonify({
            'success': True,
            'pdf': pdf_base64,
            'invoiceNumber': f"CZ{int(time.time() * 1000)}"
        })

    except Exception as e:
        print(f"Error generating invoice: {e}")
        return jsonify({'error': 'Failed to generate invoice'}), 500

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    if not item_id:
        return jsonify({'error': 'Item ID is required'}), 400

    # Get or create cart in session
    cart = session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + quantity
    session['cart'] = cart

    return jsonify({'success': True, 'message': 'Item added to cart', 'cart': cart})

@app.route('/save-order', methods=['POST'])
def save_order():
    data = request.get_json()
    name = data.get('name')
    mobile = data.get('mobile')
    email = data.get('email')
    order_data = data.get('order_data')  # JSON string of cart items
    total_amount = data.get('total_amount')
    payment_method = data.get('payment_method')
    diet_preference = data.get('diet_preference')  # 'diet', 'non-diet', or None

    if not name or not mobile or not email or not order_data or not total_amount or not payment_method:
        return jsonify({'error': 'All fields are required'}), 400

    try:
        # Save to GuestOrder table
        guest_order = GuestOrder(
            name=name,
            mobile=mobile,
            email=email,
            order_data=order_data,
            total_amount=total_amount,
            payment_method=payment_method,
            diet_preference=diet_preference
        )
        db.session.add(guest_order)
        db.session.commit()

        print(f"Guest order saved: {name}, {mobile}, {email}, {total_amount}, diet: {diet_preference}")

        return jsonify({'success': True, 'message': 'Order saved successfully', 'order_id': guest_order.id})
    except Exception as e:
        db.session.rollback()
        print(f"Error saving guest order: {e}")
        return jsonify({'error': 'Failed to save order'}), 500

@app.route('/get-guest-orders', methods=['POST'])
def get_guest_orders():
    data = request.get_json()
    mobile = data.get('mobile')
    email = data.get('email')

    if not mobile and not email:
        return jsonify({'error': 'Mobile or email is required'}), 400

    try:
        query = GuestOrder.query
        if mobile:
            query = query.filter_by(mobile=mobile)
        if email:
            query = query.filter_by(email=email)

        orders = query.order_by(GuestOrder.order_date.desc()).all()

        orders_data = [{
            'id': order.id,
            'name': order.name,
            'mobile': order.mobile,
            'email': order.email,
            'order_data': order.order_data,
            'total_amount': order.total_amount,
            'payment_method': order.payment_method,
            'diet_preference': order.diet_preference,
            'order_date': order.order_date.isoformat()
        } for order in orders]

        return jsonify({'success': True, 'orders': orders_data})
    except Exception as e:
        print(f"Error fetching guest orders: {e}")
        return jsonify({'error': 'Failed to fetch guest orders'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Routes for HTML pages
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/orders')
def orders_page():
    return render_template('orders.html')

@app.route('/payment')
def payment_page():
    return render_template('payment.html')

@app.route('/payment.html')
def payment_html_page():
    return render_template('payment.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    if request.method == 'POST':
        data = request.get_json()
        mobile = data.get('mobile')

        if not mobile:
            return jsonify({'error': 'Mobile number is required'}), 400

        try:
            user = User.query.filter_by(mobile=mobile).first()

            if user:
                user_data = {
                    'id': user.id,
                    'name': user.name,
                    'mobile': user.mobile,
                    'email': user.email,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'gender': user.gender
                }
                return jsonify({'exists': True, 'user': user_data})
            else:
                return jsonify({'exists': False})
        except Exception as e:
            print(f"Error getting profile: {e}")
            return jsonify({'error': 'Failed to get profile'}), 500

    return render_template('profile.html')

@app.route('/profile-data', methods=['POST'])
def get_profile_data():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile:
        return jsonify({'error': 'Mobile number is required'}), 400

    try:
        user = User.query.filter_by(mobile=mobile).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = {
            'id': user.id,
            'name': user.name,
            'mobile': user.mobile,
            'email': user.email,
            'dob': user.dob.isoformat() if user.dob else None,
            'gender': user.gender
        }

        # Get login count
        login_count_value = LoginHistory.query.filter_by(user_id=user.id).count()

        # Get login history
        login_history = LoginHistory.query.filter_by(user_id=user.id).order_by(LoginHistory.login_time.desc()).all()
        history_data = [{
            'id': entry.id,
            'login_time': entry.login_time.isoformat()
        } for entry in login_history]

        # Get orders
        orders = GuestOrder.query.filter_by(mobile=mobile).order_by(GuestOrder.order_date.desc()).all()
        orders_data = [{
            'id': order.id,
            'name': order.name,
            'mobile': order.mobile,
            'email': order.email,
            'order_data': order.order_data,
            'total_amount': order.total_amount,
            'payment_method': order.payment_method,
            'diet_preference': order.diet_preference,
            'order_date': order.order_date.isoformat()
        } for order in orders]

        # Calculate nutritional insights
        total_orders = len(orders)
        if total_orders > 0:
            total_protein = 0
            total_carbs = 0
            total_fats = 0
            total_calories = 0

            for order in orders:
                try:
                    items = eval(order.order_data)  # Assuming order_data is a string representation of list
                    for item in items:
                        total_protein += (item.get('protein', 0) * item.get('quantity', 1))
                        total_carbs += (item.get('carbs', 0) * item.get('quantity', 1))
                        total_fats += (item.get('fats', 0) * item.get('quantity', 1))
                        total_calories += (item.get('calories', 0) * item.get('quantity', 1))
                except:
                    pass

            avg_protein = total_protein / total_orders
            avg_carbs = total_carbs / total_orders
            avg_fats = total_fats / total_orders
            avg_calories = total_calories / total_orders
        else:
            avg_protein = avg_carbs = avg_fats = avg_calories = 0

        # Determine preference
        diet_orders = sum(1 for o in orders if o.diet_preference == 'diet')
        non_diet_orders = sum(1 for o in orders if o.diet_preference == 'non-diet')
        if diet_orders > non_diet_orders:
            preference = 'Diet'
        elif non_diet_orders > diet_orders:
            preference = 'Non-Diet'
        else:
            preference = 'Mixed'

        return jsonify({
            'user': user_data,
            'loginCount': login_count_value,
            'loginHistory': history_data,
            'totalOrders': total_orders,
            'avgProtein': round(avg_protein, 1),
            'avgCarbs': round(avg_carbs, 1),
            'avgFats': round(avg_fats, 1),
            'avgCalories': round(avg_calories),
            'preference': preference
        })

    except Exception as e:
        print(f"Error getting profile data: {e}")
        return jsonify({'error': 'Failed to get profile data'}), 500

@app.route('/welcome', methods=['GET'])
def welcome():
    print(f"Request received: {request.method} {request.path}")
    return jsonify({'message': 'Welcome to Cafe Zone!'})

@app.route('/cafeteria')
def cafeteria():
    # Database se saara khana fetch karein
    items = FoodItem.query.all()
    user_name = session.get('user_name', 'Guest')
    return render_template('cafeteria.html', items=items, user_name=user_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True, host='0.0.0.0', port=3000)

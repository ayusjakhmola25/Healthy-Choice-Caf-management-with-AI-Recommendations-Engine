from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
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

# Configure SQLAlchemy - Using SQLite for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe_zone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# MySQL connection
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'ayush123'),
    'database': os.environ.get('DB_NAME', 'cafe_users')
}

# FoodItem Model
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Integer)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String(200))  # Image ka path
    rating = db.Column(db.Float)

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
    name = db.Column(db.String(255))
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(255))
    login_time = db.Column(db.DateTime, default=db.func.current_timestamp())

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Initialize database
def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            mobile VARCHAR(15) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            dob DATE,
            gender VARCHAR(10)
        )
    ''')

    # Create login_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            name VARCHAR(255),
            mobile VARCHAR(15),
            email VARCHAR(255),
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

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

        # Record login history with user details
        login_history = LoginHistory(user_id=user_id, name=user.name, mobile=user.mobile, email=user.email)
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
        login_count_value = LoginHistory.query.filter_by(mobile=mobile).count()
        return jsonify({'loginCount': login_count_value})
    except Exception as e:
        print(f"Error fetching login count: {e}")
        return jsonify({'error': 'Failed to fetch login count'}), 500

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
            'rating': item.rating
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

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Routes for HTML pages
@app.route('/')
def home():
    return render_template('cafeteria.html')

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

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/cafeteria')
def cafeteria():
    # Database se saara khana fetch karein
    items = FoodItem.query.all()
    user_name = session.get('user_name', 'Guest')
    return render_template('cafeteria.html', items=items, user_name=user_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
    try:
        initialize_db()
    except Exception as e:
        print(f"Database connection failed: {e}. Running without database features.")
    app.run(debug=True, host='0.0.0.0', port=3000)

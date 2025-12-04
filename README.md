# 🍽️ Cafe Zone - Smart Café Management System

[![Flask](https://img.shields.io/badge/Flask-2.3.3-blue.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.1.0-orange.svg)](https://www.mysql.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A cutting-edge café management platform powered by AI-driven recommendations, secure OTP authentication, and seamless user experience. Revolutionize your café operations with intelligent meal suggestions tailored to health goals.

## 🌟 Overview

Cafe Zone is an innovative web application designed to streamline café operations while providing customers with personalized dining experiences. Leveraging AI technology, the system offers smart meal recommendations based on dietary preferences and health objectives, ensuring every customer finds their perfect choice.

## ✨ Key Features

### 🔐 Secure Authentication
- **OTP-Based Login**: Secure mobile verification with time-limited OTPs
- **User Registration**: Seamless onboarding with profile management
- **Session Management**: Persistent user sessions with automatic logout

### 🤖 AI-Powered Recommendations
- **Dietary Suggestions**: Personalized meal recommendations based on health goals
- **Smart Categorization**: Intelligent food item classification and tagging
- **Health-Aware Options**: Support for both diet and non-diet preferences

### 🛒 E-Commerce Functionality
- **Dynamic Menu Management**: Real-time food item updates with ratings
- **Shopping Cart**: Intuitive cart management with quantity controls
- **Order Processing**: Complete order lifecycle management

### 📊 Advanced Analytics
- **Login History Tracking**: Comprehensive user activity monitoring
- **Order Analytics**: Detailed insights into customer preferences
- **Performance Metrics**: Real-time business intelligence

### 🧾 Professional Invoicing
- **PDF Generation**: Automated invoice creation with ReportLab
- **Tax Calculations**: Built-in GST and delivery fee computations
- **Branded Templates**: Customizable invoice layouts

## 🛠️ Technology Stack

### Backend
- **Flask**: Lightweight WSGI web application framework
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapping
- **MySQL**: Robust relational database management system

### Frontend
- **HTML5/CSS3**: Modern responsive web design
- **JavaScript**: Dynamic client-side interactions
- **Jinja2**: Powerful templating engine

### Libraries & Tools
- **Pandas**: Data manipulation and analysis
- **ReportLab**: PDF generation and manipulation
- **Flask-CORS**: Cross-Origin Resource Sharing support

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/cafe-zone.git
   cd cafe-zone
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Configure MySQL connection in app.py
   # Run database initialization
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:3000`

## 📖 Usage

### For Customers
1. **Register/Login**: Create account or login with mobile OTP
2. **Browse Menu**: Explore AI-recommended food items
3. **Add to Cart**: Select items and manage quantities
4. **Checkout**: Complete payment and receive invoice

### For Administrators
- Monitor user activity through login history
- Manage menu items and categories
- View order analytics and performance metrics

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/send-otp` | POST | Send OTP for registration |
| `/verify-otp` | POST | Verify OTP |
| `/register` | POST | User registration |
| `/login` | POST | User login with OTP |
| `/food-items` | GET | Retrieve menu items |
| `/add-to-cart` | POST | Add items to cart |
| `/generate-invoice` | POST | Create PDF invoice |

## 📁 Project Structure

```
cafe-zone/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── instance/
│   └── cafe_zone.db      # SQLite database (development)
├── static/
│   ├── style.css         # Application stylesheets
│   ├── script.js         # Client-side JavaScript
│   └── images/           # Static image assets
└── templates/
    ├── cafeteria.html    # Main menu page
    ├── login.html        # User authentication
    ├── register.html     # User registration
    ├── cart.html         # Shopping cart
    ├── orders.html       # Order history
    ├── payment.html      # Payment processing
    └── profile.html      # User profile management
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Email: support@cafezone.com
- Issues: [GitHub Issues](https://github.com/your-username/cafe-zone/issues)

---

**Made with ❤️ for café lovers everywhere**

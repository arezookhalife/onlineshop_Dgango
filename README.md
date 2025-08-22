# OnlineShop - Django E-commerce Project

This project is an **E-commerce platform** built with Django and Django REST Framework (DRF).  
It includes product management, user authentication with JWT, shopping cart, order management, and payment integration with ZarinPal.

---

## Features

- User registration, login, and JWT authentication  
- Product listing and details API  
- Shopping cart management (add, update, remove items)  
- Checkout process with order creation  
- Online payment integration with **ZarinPal** (sandbox & production modes)  
- Order tracking and status updates  

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/arezookhalife/onlineshop_Django.git
cd onlineshop_Dgango
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate   # On Linux/Mac
.venv\Scripts\activate      # On Windows
```
    
3. Install dependencies:
```bash 
pip install -r requirements.txt
```
    
4. Apply database migrations:
```bash 
python manage.py migrate
```

5. Create a superuser:
```bash 
python manage.py createsuperuser
```

6. Run the development server:
```bash 
python manage.py runserver
```

---

## Database

- By default, the project uses SQLite for development and testing purposes.
- SQLite is lightweight and requires no additional setup.

*⚠️ For production deployment, it is strongly recommended to switch to PostgreSQL (or MySQL).*

- To use PostgreSQL, update the DATABASES setting in settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'onlineshop_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

- Then run:
```bash
python manage.py migrate
```

---

## Payment Gateway (ZarinPal)

###### The project is integrated with ZarinPal.

- In sandbox mode, payments are simulated for testing.
- In production mode, real transactions are processed.

###### Currently, settings.py is configured for sandbox:

```python
MERCHANT_ID = '5ba078bd-644a-4142-aa63-531e1cedefea'  
PAYMENT_REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json" 
PAYMENT_VERIFICATION_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json" 
STARTPAY_URL = "https://sandbox.zarinpal.com/pg/StartPay/"
```

###### ⚠️ Note: For production, replace the above URLs and MERCHANT_ID with the real values:

```python
MERCHANT_ID = "your-real-merchant-id"
PAYMENT_REQUEST_URL = "https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
PAYMENT_VERIFICATION_URL = "https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
STARTPAY_URL = "https://www.zarinpal.com/pg/StartPay/"
```
---

## API Endpoints
###### Some key API endpoints:

- Auth
    - POST /api/register/ → Register new user
    - POST /api/token/ → User login 
    - PUT /api/profile/{id}/ → Edit Profile

- Products
    - GET /api/products/ → List all products
    - POST /api/products/ → Add new product 
    - PUT /api/products/{id}/ → Edit product  
    - DELETE /api/products/{id}/ → Delete product  
- Cart
    - GET /api/cart/ → View current cart
    - POST /api/cart/ → Add product to cart
    - PUT /api/cart/{id}/ → Update products in cart

- Orders & Checkout
    - POST /api/orders/ → Add new order 
    - GET /api/orders/ → List all orders
    - PUT /api/orders/{id}/ → Update order
    - POST /api/orders/checkout/ → Start checkout and payment session

---

## Requirements

###### See requirements.txt for the full list.
- Main dependencies include:
- Django
- djangorestframework
- djangorestframework-simplejwt
- requests
- Pillow (for image uploads)

---

## Development Notes

- **Default database:** SQLite
- **Recommended production database:** PostgreSQL
- **Authentication:** JWT
- **Payment gateway:** ZarinPal
- **Tested with:** Python 3.12 and Django 5.2

---

## Developer
- Arezoo Khalifeh | Python Developer
- GitHub: arezookhalife
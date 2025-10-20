import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ecommerce_website.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    DOMAIN = os.environ.get('DOMAIN', 'http://127.0.0.1:5000')
    TAX_RATE_MULTIPLIER = os.environ.get('TAX_RATE_MULTIPLIER', 1.0)

    # Stripe Keys
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_TAX_RATE_ID = os.environ.get('STRIPE_TAX_RATE_ID')
    
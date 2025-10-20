from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate  
import stripe
from sqlalchemy.exc import ProgrammingError

from config import Config

# App and Extension Initialization 
app = Flask(__name__)
app.config.from_object(Config)

stripe.api_key = app.config.get('STRIPE_SECRET_KEY')

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    from models import User 
    return db.session.get(User, int(user_id))

from routes import *

with app.app_context():
    try:
        if not Product.query.first():
            print("Database is empty. Seeding with initial products...")
            from seed import seed_data
            seed_data()
        else:
            print("Database already contains products. Skipping seed.")
            
    except ProgrammingError:
        # Skips the error during building since 'flask db upgrade' has not been run yet
        pass
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
import os
from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

from .models import db
from .routes.health import blp as health_blueprint

# Import blueprints for main API endpoints
from .routes.auth import blp as auth_blp
from .routes.appointments import blp as appointments_blp
from .routes.calendar import blp as calendar_blp
from .routes.admin import blp as admin_blp


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# Load env vars for DB & JWT from .env (to be managed outside of repo)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("POSTGRES_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super_secret_for_dev")  # Use strong key in prod

app.config["API_TITLE"] = "Booking API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

api = Api(app)
api.register_blueprint(health_blueprint)
api.register_blueprint(auth_blp)
api.register_blueprint(appointments_blp)
api.register_blueprint(calendar_blp)
api.register_blueprint(admin_blp)

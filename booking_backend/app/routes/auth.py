from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, User
from ..schemas import UserRegistrationSchema, UserLoginSchema, UserSchema, JWTTokenSchema

blp = Blueprint("Authentication", "auth", url_prefix="/auth", description="User registration and authentication")

# PUBLIC_INTERFACE
@blp.route("/register")
class Register(MethodView):
    """Register a new user."""
    @blp.arguments(UserRegistrationSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        if User.query.filter_by(email=user_data['email']).first():
            abort(409, message="Email already registered.")
        user = User(
            email=user_data['email'],
            name=user_data['name'],
            is_admin=False
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.commit()
        return user

# PUBLIC_INTERFACE
@blp.route("/login")
class Login(MethodView):
    """Login and get JWT access token."""
    @blp.arguments(UserLoginSchema)
    @blp.response(200, JWTTokenSchema)
    def post(self, credentials):
        user = User.query.filter_by(email=credentials['email']).first()
        if not user or not user.check_password(credentials['password']):
            abort(401, message="Invalid email or password.")
        access_token = create_access_token(identity={'id': user.id, 'email': user.email, 'is_admin': user.is_admin})
        return {"access_token": access_token}

# PUBLIC_INTERFACE
@blp.route("/me")
class Me(MethodView):
    """Get current user (JWT-protected) info."""
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        user_id = get_jwt_identity()["id"]
        user = User.query.get(user_id)
        if not user:
            abort(404, message="User not found")
        return user

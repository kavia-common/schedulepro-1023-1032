from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# PUBLIC_INTERFACE
class User(db.Model):
    """User model for authentication and role management."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# PUBLIC_INTERFACE
class Appointment(db.Model):
    """Appointment model representing a user's booking."""
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslots.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    timeslot = db.relationship('Timeslot', backref=db.backref('appointments', lazy=True))

# PUBLIC_INTERFACE
class Timeslot(db.Model):
    """Timeslot model for the calendar/hour slots that can be booked."""
    __tablename__ = 'timeslots'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    available = db.Column(db.Boolean, default=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by_admin = db.relationship('User', backref=db.backref('created_timeslots', lazy=True), foreign_keys=[created_by_admin_id])

    def is_past(self):
        return self.end_time < datetime.utcnow()

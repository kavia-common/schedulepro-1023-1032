from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Appointment, Timeslot
from ..schemas import AdminStatsSchema, UserSchema, AppointmentSchema, TimeslotSchema
from datetime import datetime

blp = Blueprint("Admin", "admin", url_prefix="/admin", description="Admin dashboard features")

def require_admin():
    user = get_jwt_identity()
    if not user or not user.get("is_admin", False):
        abort(403, message="Admin privileges required.")
    return user

# PUBLIC_INTERFACE
@blp.route("/dashboard")
class AdminDashboard(MethodView):
    """Get statistics for the admin dashboard."""
    @jwt_required()
    @blp.response(200, AdminStatsSchema)
    def get(self):
        require_admin()
        return {
            "total_users": User.query.count(),
            "total_appointments": Appointment.query.count(),
            "total_timeslots": Timeslot.query.count(),
            "upcoming_appointments": Appointment.query.join(Timeslot).filter(
                Timeslot.end_time >= datetime.utcnow()
            ).count(),
        }

# PUBLIC_INTERFACE
@blp.route("/users")
class AdminUsers(MethodView):
    """List all registered users."""
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        require_admin()
        return User.query.order_by(User.created_at.desc()).all()

# PUBLIC_INTERFACE
@blp.route("/appointments")
class AdminAppointments(MethodView):
    """List all appointments."""
    @jwt_required()
    @blp.response(200, AppointmentSchema(many=True))
    def get(self):
        require_admin()
        return Appointment.query.order_by(Appointment.created_at.desc()).all()

# PUBLIC_INTERFACE
@blp.route("/timeslots")
class AdminTimeslots(MethodView):
    """List all timeslots (admin view)."""
    @jwt_required()
    @blp.response(200, TimeslotSchema(many=True))
    def get(self):
        require_admin()
        return Timeslot.query.order_by(Timeslot.start_time).all()

# PUBLIC_INTERFACE
@blp.route("/appointments/<int:appointment_id>", methods=["DELETE"])
class AdminDeleteAppointment(MethodView):
    """Delete any appointment (admin only, e.g. to revoke/correct)."""
    @jwt_required()
    def delete(self, appointment_id):
        require_admin()
        appt = Appointment.query.get(appointment_id)
        if not appt:
            abort(404, message="Appointment not found.")
        timeslot = appt.timeslot
        db.session.delete(appt)
        if timeslot and not any(a for a in timeslot.appointments if a.id != appt.id):
            timeslot.available = True
        db.session.commit()
        return {}, 204

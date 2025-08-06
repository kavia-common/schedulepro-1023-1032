from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Appointment, Timeslot
from ..schemas import AppointmentSchema
from datetime import datetime

blp = Blueprint("Appointments", "appointments", url_prefix="/appointments", description="Appointment management routes")

# PUBLIC_INTERFACE
@blp.route("/")
class AppointmentList(MethodView):
    """Get all bookings of the logged-in user."""
    @jwt_required()
    @blp.response(200, AppointmentSchema(many=True))
    def get(self):
        user_jwt = get_jwt_identity()
        my_appointments = Appointment.query.filter_by(user_id=user_jwt["id"]).all()
        return my_appointments

# PUBLIC_INTERFACE
@blp.route("/", methods=["POST"])
class AppointmentCreate(MethodView):
    """Book a timeslot if available."""
    @jwt_required()
    @blp.arguments(AppointmentSchema(only=("timeslot_id",)))
    @blp.response(201, AppointmentSchema)
    def post(self, data):
        user_jwt = get_jwt_identity()
        timeslot = Timeslot.query.get(data["timeslot_id"])
        if not timeslot or not timeslot.available or timeslot.is_past():
            abort(400, message="Timeslot unavailable.")
        # Prevent duplicate booking for same timeslot
        if Appointment.query.filter_by(user_id=user_jwt["id"], timeslot_id=timeslot.id).first():
            abort(409, message="Appointment already exists for this slot.")
        appt = Appointment(user_id=user_jwt["id"], timeslot_id=timeslot.id)
        timeslot.available = False
        db.session.add(appt)
        db.session.commit()
        return appt

# PUBLIC_INTERFACE
@blp.route("/<int:appointment_id>", methods=["DELETE"])
class AppointmentDelete(MethodView):
    """Cancel an upcoming appointment."""
    @jwt_required()
    def delete(self, appointment_id):
        user_jwt = get_jwt_identity()
        appt = Appointment.query.get(appointment_id)
        if not appt or appt.user_id != user_jwt["id"]:
            abort(404, message="Appointment not found or not yours.")
        timeslot = appt.timeslot
        if timeslot.end_time < datetime.utcnow():
            abort(400, message="Cannot cancel past appointments.")
        db.session.delete(appt)
        # Free up timeslot
        timeslot.available = True
        db.session.commit()
        return {}, 204

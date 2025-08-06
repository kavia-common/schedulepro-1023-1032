from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Timeslot
from ..schemas import TimeslotSchema
from datetime import datetime

blp = Blueprint("Calendar & Timeslots", "calendar", url_prefix="/calendar", description="Calendar and timeslot endpoints")

# PUBLIC_INTERFACE
@blp.route("/timeslots")
class TimeslotsList(MethodView):
    """Get all available timeslots (optionally in future). If admin, can list all."""
    @blp.response(200, TimeslotSchema(many=True))
    @jwt_required(optional=True)
    def get(self):
        user_jwt = get_jwt_identity()
        query = Timeslot.query
        # Non-admins: Only future/available
        if not (user_jwt and user_jwt.get("is_admin", False)):
            query = query.filter(Timeslot.available == True, Timeslot.end_time >= datetime.utcnow())
        return query.order_by(Timeslot.start_time).all()

# PUBLIC_INTERFACE
@blp.route("/timeslots", methods=["POST"])
class TimeslotCreate(MethodView):
    """Admin creates new timeslots (slots are bookable times)."""
    @jwt_required()
    @blp.arguments(TimeslotSchema)
    @blp.response(201, TimeslotSchema)
    def post(self, timeslot_data):
        user_jwt = get_jwt_identity()
        if not user_jwt or not user_jwt.get("is_admin"):
            abort(403, message="Admin privileges required.")
        # Prevent overlaps (simple check)
        start = timeslot_data["start_time"]
        end = timeslot_data["end_time"]
        conflicts = Timeslot.query.filter(
            Timeslot.start_time < end, Timeslot.end_time > start
        ).first()
        if conflicts:
            abort(409, message="Timeslot overlaps with an existing slot.")
        t = Timeslot(
            start_time=start,
            end_time=end,
            available=timeslot_data.get("available", True),
            created_by_admin_id=user_jwt["id"]
        )
        db.session.add(t)
        db.session.commit()
        return t

# PUBLIC_INTERFACE
@blp.route("/timeslots/<int:timeslot_id>", methods=["DELETE"])
class TimeslotDelete(MethodView):
    """Admin deletes a timeslot."""
    @jwt_required()
    def delete(self, timeslot_id):
        user_jwt = get_jwt_identity()
        if not user_jwt or not user_jwt.get("is_admin"):
            abort(403, message="Admin privileges required.")
        timeslot = Timeslot.query.get(timeslot_id)
        if not timeslot:
            abort(404, message="Timeslot not found.")
        db.session.delete(timeslot)
        db.session.commit()
        return {}, 204

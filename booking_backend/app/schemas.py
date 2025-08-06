from marshmallow import Schema, fields

# PUBLIC_INTERFACE
class UserSchema(Schema):
    """Schema for user registration and listing."""
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True, description="User email address")
    name = fields.Str(required=True, description="Name of the user")
    is_admin = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

# PUBLIC_INTERFACE
class UserRegistrationSchema(Schema):
    """Schema for user registration input."""
    email = fields.Email(required=True, description="User email address")
    name = fields.Str(required=True, description="Name of the user")
    password = fields.Str(required=True, load_only=True, description="Password")

# PUBLIC_INTERFACE
class UserLoginSchema(Schema):
    """Schema for user login input."""
    email = fields.Email(required=True, description="User email address")
    password = fields.Str(required=True, load_only=True, description="Password")

# PUBLIC_INTERFACE
class JWTTokenSchema(Schema):
    """Schema for JWT Token response."""
    access_token = fields.Str(required=True)

# PUBLIC_INTERFACE
class TimeslotSchema(Schema):
    """Schema for timeslot listing and creation."""
    id = fields.Int(dump_only=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    available = fields.Bool()
    created_by_admin_id = fields.Int(allow_none=True)

# PUBLIC_INTERFACE
class AppointmentSchema(Schema):
    """Schema for listing and creating appointments."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    timeslot_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    timeslot = fields.Nested(TimeslotSchema, dump_only=True)

# PUBLIC_INTERFACE
class AdminStatsSchema(Schema):
    """Schema for the admin dashboard statistics."""
    total_users = fields.Int()
    total_appointments = fields.Int()
    total_timeslots = fields.Int()
    upcoming_appointments = fields.Int()

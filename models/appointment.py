from database import db
from datetime import datetime, date, time

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancellation_remarks = db.Column(db.Text)  # Remarks for cancellation or rejection

    # Relationships
    patient = db.relationship('User', foreign_keys=[patient_id], backref='appointments_as_patient')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='appointments_as_doctor')

    def __repr__(self):
        return f'<Appointment {self.id}>' 
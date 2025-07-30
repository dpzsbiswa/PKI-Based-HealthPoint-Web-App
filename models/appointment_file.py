from database import db
from datetime import datetime

class AppointmentFile(db.Model):
    __tablename__ = 'appointment_files'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)  # e.g., 'prescription', 'test_result', 'medical_report'
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointment = db.relationship('Appointment', backref='files')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='shared_appointment_files')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='received_appointment_files')
    
    def __repr__(self):
        return f'<AppointmentFile {self.filename}>' 
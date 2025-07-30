from database import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    transaction_uuid = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    product_code = db.Column(db.String(50), default='EPAYTEST')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    esewa_transaction_code = db.Column(db.String(50), nullable=True)
    esewa_ref_id = db.Column(db.String(50), nullable=True)
    signature = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointment = db.relationship('Appointment', backref='payments')

    def __repr__(self):
        return f'<Payment {self.transaction_uuid}>' 
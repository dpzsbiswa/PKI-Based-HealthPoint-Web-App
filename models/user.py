from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'doctor' or 'patient'
    private_key = db.Column(db.Text, nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    specialization = db.Column(db.String(100), nullable=True)
    nmc_registration_number = db.Column(db.String(50), nullable=True)
    years_experience = db.Column(db.Integer, nullable=True)
    consultation_fee = db.Column(db.Float, nullable=True)
    available_days = db.Column(db.String(100), nullable=True)  # e.g., 'Mon,Tue,Wed'
    available_time = db.Column(db.String(50), nullable=True)   # e.g., '09:00-17:00'
    contact_number = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    
    # Relationships
    sent_files = db.relationship('File', foreign_keys='File.sender_id', backref='sender', lazy='dynamic')
    received_files = db.relationship('File', foreign_keys='File.recipient_id', backref='recipient', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'

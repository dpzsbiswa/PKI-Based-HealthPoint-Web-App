from app import app, db
from models.user import User
from models.file import File
from models.appointment import Appointment
from models.payment import Payment

with app.app_context():
    db.session.query(Payment).delete()
    db.session.query(File).delete()
    db.session.query(Appointment).delete()
    db.session.query(User).delete()
    db.session.commit()
    print("All records from users, appointments, files, and payments tables have been deleted.") 
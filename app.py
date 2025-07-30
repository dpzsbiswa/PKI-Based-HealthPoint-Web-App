from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from utils.encryption import RSAEncryption, sign_message, verify_signature
import json
from sqlalchemy import or_
from utils.esewa import ESewaPayment

# --- Appointment Booking and Management ---
from datetime import date, time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/doctorpatient')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
from database import db, init_app
db = init_app(app)
# socketio = SocketIO(app, cors_allowed_origins="*") # Removed SocketIO import

# Import models after db initialization
from models.user import User
from models.file import File
from models.appointment import Appointment
from models.payment import Payment
from models.appointment_file import AppointmentFile
# Remove chat-related imports
# from models.message import Message
# from models.chat_room import ChatRoom

def create_tables():
    """Create database tables with retry logic"""
    import time
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
                # Initialize with sample data
                from utils.database import init_db
                init_db(db, User)
                print("Database initialized successfully!")
                return
        except Exception as e:
            retry_count += 1
            print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}")
            if retry_count < max_retries:
                print("Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print("Failed to connect to database after all retries")
                raise

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        private_key_file = request.files.get('private_key')
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'error')
            return render_template('login.html')
        if not private_key_file or private_key_file.filename == '':
            flash('Private key file is required', 'error')
            return render_template('login.html')
        uploaded_key = private_key_file.read().decode()
        if uploaded_key.strip() != user.private_key.strip():
            flash('Uploaded private key does not match our records.', 'error')
            return render_template('login.html')
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')
        age = request.form.get('age')
        address = request.form.get('address')
        contact_number = request.form.get('contact_number')
        role = request.form.get('role')
        if not name or not email or not password or not role or not gender or not age or not address or not contact_number:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Generate RSA key pair for the user
        rsa_encryption = RSAEncryption()
        private_key, public_key = rsa_encryption.generate_key_pair()
        
        specialization = request.form.get('specialization') if role == 'doctor' else None
        nmc_registration_number = request.form.get('nmc_registration_number') if role == 'doctor' else None
        years_experience = request.form.get('years_experience') if role == 'doctor' else None
        consultation_fee = request.form.get('consultation_fee') if role == 'doctor' else None
        available_days = request.form.get('available_days') if role == 'doctor' else None
        available_time = request.form.get('available_time') if role == 'doctor' else None
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            private_key=private_key,
            public_key=public_key,
            specialization=specialization,
            nmc_registration_number=nmc_registration_number,
            years_experience=years_experience,
            consultation_fee=consultation_fee,
            available_days=available_days,
            available_time=available_time,
            gender=gender,
            age=age,
            address=address,
            contact_number=contact_number
        )
        
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please download your private key and then login.', 'success')
        # Render a success page that triggers download and redirects
        return render_template('registration_success.html', user_id=user.id, user_name=user.name)
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Dashboard and main functionality
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    files = File.query.filter(
        or_(File.sender_id == user.id, File.recipient_id == user.id)
    ).order_by(File.created_at.desc()).all()
    if user.role == 'doctor':
        from models.appointment import Appointment
        recent_appointments = Appointment.query.filter(
            Appointment.doctor_id == user.id,
            Appointment.status.in_(['pending', 'approved'])
        ).order_by(Appointment.date.desc(), Appointment.time.desc()).limit(5).all()
        cancelled_appointments = Appointment.query.filter(
            Appointment.doctor_id == user.id,
            Appointment.status.in_(['cancelled', 'rejected'])
        ).order_by(Appointment.date.desc(), Appointment.time.desc()).limit(5).all()
        
        # Get recent appointment files shared by the doctor
        recent_appointment_files = AppointmentFile.query.filter(
            AppointmentFile.doctor_id == user.id
        ).order_by(AppointmentFile.created_at.desc()).limit(5).all()
        
        return render_template('dashboard.html', 
                             user=user, 
                             files=files, 
                             recent_appointments=recent_appointments, 
                             cancelled_appointments=cancelled_appointments,
                             recent_appointment_files=recent_appointment_files)
    
    # For patients, get recent appointment files shared with them
    recent_appointment_files = AppointmentFile.query.filter(
        AppointmentFile.patient_id == user.id
    ).order_by(AppointmentFile.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         user=user, 
                         files=files, 
                         recent_appointment_files=recent_appointment_files)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        recipient_id = request.form['recipient_id']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
            
            # Save the original file temporarily
            file.save(file_path)
            
            # Encrypt the file
            recipient = User.query.get(recipient_id)
            sender = User.query.get(session['user_id'])
            
            rsa_encryption = RSAEncryption()
            encrypted_file_path = rsa_encryption.encrypt_file(file_path, recipient.public_key)
            
            # Remove original file
            os.remove(file_path)
            
            # Create file record
            file_record = File(
                id=file_id,
                filename=filename,
                file_path=encrypted_file_path,
                sender_id=session['user_id'],
                recipient_id=recipient_id,
                file_size=os.path.getsize(encrypted_file_path)
            )
            
            db.session.add(file_record)
            db.session.commit()
            
            flash('File uploaded and encrypted successfully!', 'success')
            return redirect(url_for('dashboard'))
    
    # Get potential recipients (doctors can send to patients and vice versa)
    current_user = User.query.get(session['user_id'])
    if current_user.role == 'doctor':
        recipients = User.query.filter_by(role='patient').all()
    else:
        recipients = User.query.filter_by(role='doctor').all()
    
    return render_template('upload.html', recipients=recipients)

@app.route('/download/<file_id>')
def download_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    file_record = File.query.get_or_404(file_id)
    
    # Check if user is authorized to download this file
    if file_record.sender_id != session['user_id'] and file_record.recipient_id != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    # Decrypt the file
    user = User.query.get(session['user_id'])
    rsa_encryption = RSAEncryption()
    
    try:
        decrypted_file_path = rsa_encryption.decrypt_file(file_record.file_path, user.private_key)
        return send_file(decrypted_file_path, as_attachment=True, download_name=file_record.filename)
    except Exception as e:
        flash('Error decrypting file', 'error')
        return redirect(url_for('dashboard'))

# --- Appointment Booking and Management ---

@app.route('/appointments', methods=['GET'])
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role == 'doctor':
        # Doctor: see all appointments where they are the doctor
        appts = Appointment.query.filter_by(doctor_id=user.id).order_by(Appointment.date, Appointment.time).all()
    else:
        # Patient: see all appointments where they are the patient
        appts = Appointment.query.filter_by(patient_id=user.id).order_by(Appointment.date, Appointment.time).all()
    return render_template('appointments.html', user=user, appointments=appts)

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'patient':
        flash('Only patients can book appointments.', 'error')
        return redirect(url_for('appointments'))
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        appt_date = request.form['date']
        appt_time_str = request.form['time']  # e.g., '18:30'
        notes = request.form.get('notes', '')
        # Convert to Python time object
        appt_time = datetime.strptime(appt_time_str, '%H:%M').time()
        # Prevent double-booking (same doctor, date, and time)
        existing = Appointment.query.filter_by(doctor_id=doctor_id, date=appt_date, time=appt_time).first()
        if existing:
            flash('This time slot is already booked for the selected doctor.', 'error')
            return redirect(url_for('book_appointment'))
        
        # Get doctor information for payment
        doctor = User.query.get(doctor_id)
        consultation_fee = doctor.consultation_fee or 0
        
        if consultation_fee <= 0:
            flash('This doctor has not set a consultation fee. Please contact the doctor.', 'error')
            return redirect(url_for('book_appointment'))
        
        # Create appointment
        appt = Appointment(
            patient_id=user.id,
            doctor_id=doctor_id,
            date=appt_date,
            time=appt_time,
            notes=notes,
            status='pending'
        )
        db.session.add(appt)
        db.session.commit()
        
        # Redirect directly to payment
        return redirect(url_for('initiate_payment', appointment_id=appt.id))
    
    # Show list of doctors
    doctors = User.query.filter_by(role='doctor').all()
    min_date = date.today().isoformat()
    return render_template('book_appointment.html', doctors=doctors, min_date=min_date)

@app.route('/appointment/<int:appt_id>/cancel', methods=['POST'])
def cancel_appointment(appt_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    appt = Appointment.query.get_or_404(appt_id)
    user = User.query.get(session['user_id'])
    if user.role == 'patient' and appt.patient_id != user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('appointments'))
    if user.role == 'doctor' and appt.doctor_id != user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('appointments'))
    remarks = request.form.get('remarks', '')
    appt.status = 'cancelled'
    appt.cancellation_remarks = remarks
    db.session.commit()
    flash('Appointment cancelled.', 'success')
    return redirect(url_for('appointments'))

@app.route('/appointment/<int:appt_id>/approve', methods=['POST'])
def approve_appointment(appt_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    appt = Appointment.query.get_or_404(appt_id)
    user = User.query.get(session['user_id'])
    if user.role != 'doctor' or appt.doctor_id != user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('appointments'))
    appt.status = 'approved'
    db.session.commit()
    flash('Appointment approved.', 'success')
    return redirect(url_for('appointments'))

@app.route('/appointment/<int:appt_id>/reject', methods=['POST'])
def reject_appointment(appt_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    appt = Appointment.query.get_or_404(appt_id)
    user = User.query.get(session['user_id'])
    if user.role != 'doctor' or appt.doctor_id != user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('appointments'))
    remarks = request.form.get('remarks', '')
    appt.status = 'rejected'
    appt.cancellation_remarks = remarks
    db.session.commit()
    flash('Appointment rejected.', 'success')
    return redirect(url_for('appointments'))

# Remove /chat/<int:room_id> route
# Remove /create_chat route
# Remove /verify_message route
# Remove all @socketio.on events

@app.route('/api/booked_slots')
def api_booked_slots():
    doctor_id = request.args.get('doctor_id')
    date_val = request.args.get('date')
    if not doctor_id or not date_val:
        return jsonify({'booked': []})
    booked = Appointment.query.filter_by(doctor_id=doctor_id, date=date_val).with_entities(Appointment.time).all()
    booked_slots = [b[0].strftime('%H:%M') for b in booked]
    return jsonify({'booked': booked_slots})

# --- Appointment File Sharing ---

@app.route('/appointment/<int:appt_id>/files')
def appointment_files(appt_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appt_id)
    user = User.query.get(session['user_id'])
    
    # Check if user is authorized to view this appointment
    if user.role == 'doctor' and appointment.doctor_id != user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('appointments'))
    if user.role == 'patient' and appointment.patient_id != user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('appointments'))
    
    files = AppointmentFile.query.filter_by(appointment_id=appt_id).order_by(AppointmentFile.created_at.desc()).all()
    
    return render_template('appointment_files.html', 
                         appointment=appointment, 
                         files=files, 
                         user=user)

@app.route('/appointment/<int:appt_id>/upload_file', methods=['GET', 'POST'])
def upload_appointment_file(appt_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appt_id)
    user = User.query.get(session['user_id'])
    
    # Only doctors can upload files for appointments
    if user.role != 'doctor' or appointment.doctor_id != user.id:
        flash('Only doctors can upload files for appointments', 'error')
        return redirect(url_for('appointments'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        file_type = request.form.get('file_type', 'medical_document')
        description = request.form.get('description', '')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
            
            # Save the original file temporarily
            file.save(file_path)
            
            # Encrypt the file for the patient
            patient = appointment.patient
            rsa_encryption = RSAEncryption()
            encrypted_file_path = rsa_encryption.encrypt_file(file_path, patient.public_key)
            
            # Remove original file
            os.remove(file_path)
            
            # Create appointment file record
            appointment_file = AppointmentFile(
                id=file_id,
                filename=filename,
                file_path=encrypted_file_path,
                appointment_id=appt_id,
                doctor_id=user.id,
                patient_id=appointment.patient_id,
                file_type=file_type,
                description=description,
                file_size=os.path.getsize(encrypted_file_path)
            )
            
            db.session.add(appointment_file)
            db.session.commit()
            
            flash('File uploaded and shared with patient successfully!', 'success')
            return redirect(url_for('appointment_files', appt_id=appt_id))
    
    return render_template('upload_appointment_file.html', appointment=appointment)

@app.route('/appointment_file/<file_id>/download')
def download_appointment_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment_file = AppointmentFile.query.get_or_404(file_id)
    user = User.query.get(session['user_id'])
    
    # Check if user is authorized to download this file
    if appointment_file.doctor_id != user.id and appointment_file.patient_id != user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('appointments'))
    
    # Decrypt the file
    rsa_encryption = RSAEncryption()
    
    try:
        decrypted_file_path = rsa_encryption.decrypt_file(appointment_file.file_path, user.private_key)
        return send_file(decrypted_file_path, as_attachment=True, download_name=appointment_file.filename)
    except Exception as e:
        flash('Error decrypting file', 'error')
        return redirect(url_for('appointment_files', appt_id=appointment_file.appointment_id))

@app.route('/appointment_file/<file_id>/delete', methods=['POST'])
def delete_appointment_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment_file = AppointmentFile.query.get_or_404(file_id)
    user = User.query.get(session['user_id'])
    
    # Only doctors can delete files they uploaded
    if user.role != 'doctor' or appointment_file.doctor_id != user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('appointments'))
    
    # Delete the encrypted file
    try:
        if os.path.exists(appointment_file.file_path):
            os.remove(appointment_file.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Delete the database record
    db.session.delete(appointment_file)
    db.session.commit()
    
    flash('File deleted successfully', 'success')
    return redirect(url_for('appointment_files', appt_id=appointment_file.appointment_id))

# --- eSewa Payment Integration ---

@app.route('/payment/<int:appointment_id>')
def initiate_payment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    user = User.query.get(session['user_id'])
    
    # Check if user is authorized to pay for this appointment
    if appointment.patient_id != user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('appointments'))
    
    # Check if appointment is pending payment
    if appointment.status != 'pending':
        flash('This appointment is not available for payment', 'error')
        return redirect(url_for('appointments'))
    
    # Check if payment already exists
    existing_payment = Payment.query.filter_by(appointment_id=appointment_id, status='completed').first()
    if existing_payment:
        flash('Payment already completed for this appointment', 'info')
        return redirect(url_for('appointments'))
    
    # Get doctor's consultation fee
    consultation_fee = appointment.doctor.consultation_fee or 0
    if consultation_fee <= 0:
        flash('No consultation fee set for this doctor', 'error')
        return redirect(url_for('appointments'))
    
    # Calculate tax (13% VAT)
    tax_amount = consultation_fee * 0.13
    total_amount = consultation_fee + tax_amount
    
    # Initialize eSewa payment
    esewa = ESewaPayment()
    form_data, transaction_uuid = esewa.create_payment_form_data(
        appointment=appointment,
        amount=consultation_fee,
        tax_amount=tax_amount
    )
    
    # Update URLs to use your domain
    base_url = request.host_url.rstrip('/')
    form_data['success_url'] = f"{base_url}/payment/success"
    form_data['failure_url'] = f"{base_url}/payment/failure"
    
    # Create payment record
    payment = Payment(
        appointment_id=appointment_id,
        transaction_uuid=transaction_uuid,
        amount=consultation_fee,
        tax_amount=tax_amount,
        total_amount=total_amount,
        signature=form_data['signature']
    )
    
    db.session.add(payment)
    db.session.commit()
    
    return render_template('payment_form.html',
                         appointment=appointment,
                         amount=consultation_fee,
                         tax_amount=tax_amount,
                         total_amount=total_amount,
                         form_data=form_data,
                         esewa_url=esewa.test_url)

@app.route('/payment/success')
def payment_success():
    # Get the encoded response from eSewa
    encoded_response = request.args.get('data')
    
    if not encoded_response:
        flash('Invalid payment response', 'error')
        return redirect(url_for('appointments'))
    
    # Initialize eSewa payment
    esewa = ESewaPayment()
    
    # Decode the response
    response_data = esewa.decode_esewa_response(encoded_response)
    
    if 'error' in response_data:
        flash(f'Error decoding response: {response_data["error"]}', 'error')
        return redirect(url_for('appointments'))
    
    # Verify the signature
    if not esewa.verify_signature(response_data, response_data.get('signature', '')):
        flash('Payment signature verification failed', 'error')
        return redirect(url_for('appointments'))
    
    # Check if payment is successful
    if response_data.get('status') != 'COMPLETE':
        flash('Payment was not completed successfully', 'error')
        return redirect(url_for('appointments'))
    
    # Find the payment record
    transaction_uuid = response_data.get('transaction_uuid')
    payment = Payment.query.filter_by(transaction_uuid=transaction_uuid).first()
    
    if not payment:
        flash('Payment record not found', 'error')
        return redirect(url_for('appointments'))
    
    # Update payment status
    payment.status = 'completed'
    payment.esewa_transaction_code = response_data.get('transaction_code')
    payment.esewa_ref_id = response_data.get('ref_id')
    
    # Update appointment status
    appointment = payment.appointment
    appointment.status = 'approved'
    
    db.session.commit()
    
    flash('Payment completed successfully!', 'success')
    return render_template('payment_success.html', payment=payment)

@app.route('/payment/failure')
def payment_failure():
    # Get the encoded response from eSewa
    encoded_response = request.args.get('data')
    
    if encoded_response:
        # Initialize eSewa payment
        esewa = ESewaPayment()
        
        # Decode the response
        response_data = esewa.decode_esewa_response(encoded_response)
        
        if 'error' not in response_data:
            # Find the payment record
            transaction_uuid = response_data.get('transaction_uuid')
            payment = Payment.query.filter_by(transaction_uuid=transaction_uuid).first()
            
            if payment:
                payment.status = 'failed'
                db.session.commit()
                
                return render_template('payment_failure.html', payment=payment, appointment=payment.appointment)
    
    # If no valid response or payment record found
    flash('Payment failed', 'error')
    return render_template('payment_failure.html', payment=None, appointment=None)

@app.route('/payment/status/<transaction_uuid>')
def check_payment_status(transaction_uuid):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    payment = Payment.query.filter_by(transaction_uuid=transaction_uuid).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Check if user is authorized
    user = User.query.get(session['user_id'])
    if payment.appointment.patient_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Check status with eSewa
    esewa = ESewaPayment()
    status_response = esewa.check_transaction_status(
        transaction_uuid=transaction_uuid,
        total_amount=payment.total_amount
    )
    
    if 'error' not in status_response:
        # Update payment status if it changed
        if status_response.get('status') != payment.status:
            payment.status = status_response.get('status', payment.status)
            payment.esewa_ref_id = status_response.get('ref_id')
            db.session.commit()
    
    return jsonify(status_response)

@app.route('/download_private_key/<int:user_id>')
def download_private_key(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))
    from io import BytesIO
    private_key_bytes = user.private_key.encode()
    private_key_file = BytesIO(private_key_bytes)
    private_key_file.seek(0)
    return send_file(
        private_key_file,
        as_attachment=True,
        download_name=f'{user.name}_private_key.pem',
        mimetype='application/x-pem-file'
    )

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    print("Starting SecureHealth application...")
    
    # Initialize database on startup
    try:
        create_tables()
        print("✓ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("The application will continue to run, but database operations may fail.")
    
    print("🚀 Starting Flask-SocketIO server...")
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    app.run(debug=True, host='0.0.0.0', port=5000)

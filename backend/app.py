from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import random
import string
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from pathlib import Path

# Initialize Flask App
# Point to frontend folders that were moved
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'database', 'civic_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for base64 photo data

# Initialize Database
db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10), unique=True, nullable=True)
    user_id = db.Column(db.String(50), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # citizen, municipal, dept, police
    name = db.Column(db.String(100))
    department = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    complaints = db.relationship('Complaint', backref='reporter', lazy=True, foreign_keys='Complaint.reporter_id')

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10), unique=True)
    otp_code = db.Column(db.String(6))
    created_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(20), unique=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    complaint_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    district = db.Column(db.String(50))
    pincode = db.Column(db.String(6))
    location = db.Column(db.String(200))
    coordinates = db.Column(db.String(50))
    status = db.Column(db.String(20), default='submitted')  # submitted, assigned, resolved
    priority = db.Column(db.String(10), default='medium')
    photo_path = db.Column(db.String(255))
    photo_data = db.Column(db.LargeBinary)
    evidence_path = db.Column(db.String(255))
    resolved_photo_path = db.Column(db.String(255))
    resolved_coordinates = db.Column(db.String(50))
    forwarded_department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.Text)
    is_fake = db.Column(db.Boolean, default=False)
    reporter_name = db.Column(db.String(100))
    fake_investigation = db.relationship('FakeInvestigation', backref='complaint', lazy=True, uselist=False)

class FakeInvestigation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), unique=True)
    investigated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    reason = db.Column(db.Text)
    evidence = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)

# ==================== AUTHENTICATION DECORATORS ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('index'))
            if session.get('role') != role:
                return jsonify({'success': False, 'message': 'Access Denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== UTILITY FUNCTIONS ====================

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_complaint_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"CMP-{timestamp}-{random_suffix}"

def get_districts():
    return [
        'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore',
        'Dharmapuri', 'Dindigul', 'Erode', 'Kallakurichi', 'Kancheepuram',
        'Kanyakumari', 'Karur', 'Krishnagiri', 'Madurai', 'Mayiladuthurai',
        'Nagapattinam', 'Namakkal', 'Nilgiris', 'Perambalur', 'Pudukkottai',
        'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga', 'Tenkasi',
        'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli',
        'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur',
        'Vellore', 'Viluppuram', 'Virudhunagar'
    ]

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html', districts=get_districts())

@app.route('/api/citizen/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    phone = data.get('phone')
    
    if not phone or len(phone) != 10 or not phone.isdigit():
        return jsonify({'success': False, 'message': 'Invalid phone number'}), 400
    
    # Check if user exists
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found. Please register first.'}), 404
    
    # Generate and store OTP
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=10)
    
    existing_otp = OTP.query.filter_by(phone=phone).first()
    if existing_otp:
        existing_otp.otp_code = otp_code
        existing_otp.expires_at = expires_at
        existing_otp.created_at = datetime.now()
    else:
        otp = OTP(phone=phone, otp_code=otp_code, expires_at=expires_at)
        db.session.add(otp)
    
    db.session.commit()
    
    # In production, send SMS via gateway
    print(f"OTP for {phone}: {otp_code}")
    
    return jsonify({'success': True, 'message': f'OTP sent. Demo OTP: {otp_code}', 'demo_otp': otp_code})

@app.route('/api/citizen/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    otp_code = data.get('otp')
    
    otp_record = OTP.query.filter_by(phone=phone, otp_code=otp_code).first()
    
    if not otp_record:
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
    
    if datetime.now() > otp_record.expires_at:
        return jsonify({'success': False, 'message': 'OTP has expired'}), 400
    
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Create session
    session['user_id'] = user.id
    session['phone'] = phone
    session['role'] = user.role
    session['name'] = user.name
    
    # Delete used OTP
    db.session.delete(otp_record)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Login successful', 'role': user.role})

@app.route('/api/official/login', methods=['POST'])
def official_login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')
    role = data.get('role')
    pincode = data.get('pincode', '')
    department = data.get('department', '')
    
    print(f"Login attempt: ID={user_id}, Role={role}, Pincode={pincode}, Dept={department}")
    user = User.query.filter_by(user_id=user_id, role=role).first()
    
    if not user:
        print(f"Login failed: User not found with ID {user_id} and role {role}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
    if not check_password_hash(user.password, password):
        print(f"Login failed: Password mismatch for {user_id}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Create session
    session['user_id'] = user.id
    session['role'] = user.role
    session['name'] = user.name
    session['pincode'] = pincode or user.pincode # Use entered pincode or default
    session['department'] = department or user.department
    
    return jsonify({'success': True, 'message': 'Login successful', 'role': user.role})

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    return render_template('dashboard.html', role=role, phone=session.get('phone'), districts=get_districts())

@app.route('/api/complaint/submit', methods=['POST'])
@login_required
def submit_complaint():
    try:
        data = request.get_json()
        print(f"Complaint Submission attempt by user {session.get('user_id')}")
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['type', 'district', 'pincode', 'location', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field.capitalize()} is required'}), 400
        
        user = db.session.get(User, session['user_id'])
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        complaint_id = generate_complaint_id()
        
        # Handle photo data if provided
        photo_data = data.get('photo')
        photo_path = None
        
        if photo_data:
            try:
                # Create uploads directory if it doesn't exist
                # Use static folder path from app config
                uploads_dir = Path(app.static_folder) / 'uploads'
                uploads_dir.mkdir(parents=True, exist_ok=True)
                
                # Decode base64 photo
                if photo_data.startswith('data:image'):
                    # Extract base64 data after the comma
                    photo_data = photo_data.split(',')[1]
                
                # Create filename
                photo_filename = f"{complaint_id}_{int(datetime.now().timestamp())}.jpg"
                photo_path = str(uploads_dir / photo_filename)
                
                # Save photo file
                photo_bytes = base64.b64decode(photo_data)
                with open(photo_path, 'wb') as f:
                    f.write(photo_bytes)
            except Exception as e:
                print(f"Error saving photo: {e}")
                photo_path = None
        
        complaint = Complaint(
            complaint_id=complaint_id,
            reporter_id=session['user_id'],
            reporter_name=data.get('name') or user.name,
            title=data.get('type'),
            complaint_type=data.get('type'),
            description=data.get('description'),
            district=data.get('district'),
            pincode=data.get('pincode'),
            location=data.get('location'),
            coordinates=data.get('coordinates', ''),
            phone=data.get('mobile_number'),
            photo_path=photo_path,
            status='submitted'
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Complaint submitted successfully',
            'complaint_id': complaint_id
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting complaint: {e}")
        return jsonify({'success': False, 'message': f'Error submitting complaint: {str(e)}'}), 500

@app.route('/api/complaints', methods=['GET'])
@login_required
def get_complaints():
    role = session.get('role')
    user_id = session['user_id']
    
    pincode = session.get('pincode')
    
    if role == 'citizen':
        complaints = Complaint.query.filter_by(reporter_id=user_id).all()
    elif role == 'municipal':
        # Municipal officer sees complaints for the pincode entered at login
        if pincode:
            complaints = Complaint.query.filter_by(pincode=pincode).all()
        else:
            complaints = Complaint.query.all()
    elif role == 'dept':
        department = session.get('department')
        query = Complaint.query
        if department:
            query = query.filter(Complaint.forwarded_department == department)
        if pincode:
            query = query.filter(Complaint.pincode == pincode)
        else:
            query = query.filter(Complaint.status.in_(['assigned', 'in_progress', 'resolved']))
        complaints = query.all()
    elif role == 'police':
        # Police only see fake reports in the entered pincode
        if pincode:
            complaints = Complaint.query.filter_by(is_fake=True, pincode=pincode).all()
        else:
            complaints = Complaint.query.filter_by(is_fake=True).all()
    else:
        complaints = []
    
    result = []
    for c in complaints:
        # Build photo URL if photo exists
        photo_url = None
        if c.photo_path:
            # We store paths like '../frontend/static/uploads/file.jpg'
            # We want URLs like '/static/uploads/file.jpg'
            filename = os.path.basename(c.photo_path)
            photo_url = f'/static/uploads/{filename}'
        
        resolved_photo_url = None
        if c.resolved_photo_path:
            filename = os.path.basename(c.resolved_photo_path)
            resolved_photo_url = f'/static/uploads/{filename}'
        
        result.append({
            'id': c.id,
            'complaint_id': c.complaint_id,
            'title': c.title or c.complaint_type,
            'type': c.complaint_type,
            'description': c.description or '',
            'district': c.district,
            'pincode': c.pincode,
            'status': c.status,
            'forwarded_department': c.forwarded_department or '',
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'location': c.location,
            'coordinates': c.coordinates or '',
            'photo_url': photo_url,
            'resolved_photo_url': resolved_photo_url,
            'reporter_name': c.reporter_name or (c.reporter.name if c.reporter else 'Anonymous'),
            'reporter_phone': c.phone or (c.reporter.phone if c.reporter else 'N/A'),
            'resolution_notes': c.resolution_notes or '',
            'resolved_coordinates': c.resolved_coordinates or ''
        })
    
    return jsonify({'complaints': result})

@app.route('/api/complaint/<int:complaint_id>/forward', methods=['POST'])
@login_required
def forward_complaint(complaint_id):
    if session.get('role') != 'municipal':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    department = data.get('department', '').strip()

    if not department:
        return jsonify({'success': False, 'message': 'Please select a department'}), 400

    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404

    complaint.status = 'assigned'
    complaint.forwarded_department = department
    complaint.verified_by = session['user_id']
    complaint.updated_at = datetime.now()
    db.session.commit()

    return jsonify({'success': True, 'message': f'Complaint forwarded to {department}'})

@app.route('/api/complaint/<int:complaint_id>/assign', methods=['POST'])
@login_required
def assign_complaint(complaint_id):
    if session.get('role') != 'municipal':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    dept_officer_id = data.get('assigned_to')
    
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    complaint.status = 'assigned'
    complaint.assigned_to = dept_officer_id
    complaint.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Complaint assigned'})

@app.route('/api/complaint/<int:complaint_id>/start-work', methods=['POST'])
@login_required
def start_work(complaint_id):
    if session.get('role') != 'dept':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    complaint.status = 'in_progress'
    complaint.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Complaint marked as In Progress'})

@app.route('/api/complaint/<int:complaint_id>/resolve', methods=['POST'])
@login_required
def resolve_complaint(complaint_id):
    if session.get('role') != 'dept':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    complaint.status = 'resolved'
    complaint.resolved_at = datetime.now()
    complaint.resolution_notes = data.get('notes')
    complaint.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Complaint resolved'})

@app.route('/api/complaint/<int:complaint_id>/update-status', methods=['POST'])
@login_required
def update_status(complaint_id):
    if session.get('role') != 'dept':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    notes = data.get('notes', '')
    
    if new_status not in ['assigned', 'in_progress', 'resolved']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
        
    complaint.status = new_status
    if notes:
        complaint.resolution_notes = notes
        
    complaint.updated_at = datetime.now()
    if new_status == 'resolved':
        complaint.resolved_at = datetime.now()
        complaint.resolved_coordinates = data.get('resolved_coordinates')
        
        # Handle resolved photo if provided
        resolved_photo_data = data.get('resolved_photo')
        if resolved_photo_data:
            try:
                # Use static folder path from app config
                uploads_dir = Path(app.static_folder) / 'uploads'
                uploads_dir.mkdir(parents=True, exist_ok=True)
                
                if resolved_photo_data.startswith('data:image'):
                    resolved_photo_data = resolved_photo_data.split(',')[1]
                
                photo_filename = f"RES_{complaint.complaint_id}_{int(datetime.now().timestamp())}.jpg"
                photo_path = str(uploads_dir / photo_filename)
                
                photo_bytes = base64.b64decode(resolved_photo_data)
                with open(photo_path, 'wb') as f:
                    f.write(photo_bytes)
                
                complaint.resolved_photo_path = photo_path
            except Exception as e:
                print(f"Error saving resolved photo: {e}")
                
    db.session.commit()
    return jsonify({'success': True, 'message': f'Status updated to {new_status}'})

@app.route('/api/complaint/<int:complaint_id>/mark-fake', methods=['POST'])
@login_required
def dept_mark_fake(complaint_id):
    if session.get('role') != 'dept':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    reason = data.get('reason', 'Marked as fake/spam by department officer')
    
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    complaint.is_fake = True
    complaint.status = 'resolved' # Mark as resolved/closed from dept view
    complaint.resolution_notes = f"REPORTED AS FAKE: {reason}"
    complaint.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Complaint marked as fake and moved to investigation'})

@app.route('/api/complaint/<int:complaint_id>/report-fake', methods=['POST'])
@login_required
def report_fake_complaint(complaint_id):
    if session.get('role') != 'police':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    complaint.is_fake = True
    investigation = FakeInvestigation(
        complaint_id=complaint_id,
        investigated_by=session['user_id'],
        reason=data.get('reason'),
        evidence=data.get('evidence', '')
    )
    
    db.session.add(investigation)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Complaint marked as fake'})

@app.route('/api/complaint/<int:complaint_id>/detail', methods=['GET'])
@login_required
def complaint_detail(complaint_id):
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    photo_url = None
    if complaint.photo_path:
        filename = os.path.basename(complaint.photo_path)
        photo_url = f'/static/uploads/{filename}'
    
    resolved_photo_url = None
    if complaint.resolved_photo_path:
        filename = os.path.basename(complaint.resolved_photo_path)
        resolved_photo_url = f'/static/uploads/{filename}'
    
    return jsonify({
        'success': True,
        'complaint': {
            'id': complaint.id,
            'complaint_id': complaint.complaint_id,
            'title': complaint.title,
            'type': complaint.complaint_type,
            'description': complaint.description or '',
            'district': complaint.district,
            'pincode': complaint.pincode,
            'location': complaint.location,
            'coordinates': complaint.coordinates or '',
            'status': complaint.status,
            'forwarded_department': complaint.forwarded_department or '',
            'created_at': complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'photo_url': photo_url,
            'resolved_photo_url': resolved_photo_url,
            'reporter_name': complaint.reporter_name or (complaint.reporter.name if complaint.reporter else 'Unknown'),
            'reporter_phone': complaint.phone or (complaint.reporter.phone if complaint.reporter else 'N/A'),
            'resolution_notes': complaint.resolution_notes or '',
            'resolved_coordinates': complaint.resolved_coordinates or ''
        }
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ==================== CREATE SAMPLE DATA ====================

def create_sample_data():
    if User.query.first() is not None:
        return  # Data already exists
    
    # Sample users
    users = [
        User(phone='9876543210', role='citizen', name='John Doe'),
        User(phone='9876543211', role='citizen', name='Jane Smith'),
        User(user_id='MUN001', password=generate_password_hash('password123'), role='municipal', name='Municipal Officer', pincode='600001'),
        User(user_id='DEPT001', password=generate_password_hash('password123'), role='dept', name='Municipal Corp Officer', department='Municipal Corporation'),
        User(user_id='DEPT002', password=generate_password_hash('password123'), role='dept', name='Electrical Board Officer', department='Electrical Board'),
        User(user_id='DEPT003', password=generate_password_hash('password123'), role='dept', name='Fire Station Officer', department='Fire Station'),
        User(user_id='POLICE001', password=generate_password_hash('password123'), role='police', name='Police Officer'),
    ]
    
    for user in users:
        db.session.add(user)
    
    db.session.commit()
    print("Sample data created successfully")

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    app.run(debug=True, port=5000)

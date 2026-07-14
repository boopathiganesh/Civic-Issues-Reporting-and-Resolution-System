Utility functions and constants for the Civic Issues Reporting and Resolution System
"""

import re
from datetime import datetime
from enum import Enum

# ==================== CONSTANTS ====================

# User Roles
class UserRole(Enum):
    CITIZEN = 'citizen'
    MUNICIPAL = 'municipal'
    DEPARTMENT = 'dept'
    POLICE = 'police'


# Complaint Status
class ComplaintStatus(Enum):
    SUBMITTED = 'submitted'
    VERIFIED = 'verified'
    ASSIGNED = 'assigned'
    RESOLVED = 'resolved'


# Complaint Priority
class ComplaintPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'


# Complaint Types
COMPLAINT_TYPES = [
    'Roads',
    'Water',
    'Garbage',
    'Drainage',
    'Streetlight',
    'Electricity',
    'Public Safety',
    'Other'
]

# Tamil Nadu Districts
TAMIL_NADU_DISTRICTS = [
    'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore',
    'Dharmapuri', 'Dindigul', 'Erode', 'Kallakurichi', 'Kancheepuram',
    'Kanyakumari', 'Karur', 'Krishnagiri', 'Madurai', 'Mayiladuthurai',
    'Nagapattinam', 'Namakkal', 'Nilgiris', 'Perambalur', 'Pudukkottai',
    'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga', 'Tenkasi',
    'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli',
    'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur',
    'Vellore', 'Viluppuram', 'Virudhunagar'
]

# Departments
DEPARTMENTS = [
    'Municipal Corporation',
    'Electricity Board (EB)',
    'Fire Station',
    'Water Supply',
    'Public Works',
    'Sanitation'
]

# ==================== VALIDATION FUNCTIONS ====================

def validate_phone(phone):
    """Validate Indian phone number format"""
    if not phone or len(phone) != 10:
        return False
    return phone.isdigit()


def validate_pincode(pincode):
    """Validate 6-digit pincode"""
    if not pincode or len(pincode) != 6:
        return False
    return pincode.isdigit()


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_user_id(user_id):
    """Validate user ID format (alphanumeric, 4-20 chars)"""
    pattern = r'^[a-zA-Z0-9_]{4,20}$'
    return re.match(pattern, user_id) is not None


def validate_password(password):
    """Validate password strength"""
    # Minimum 8 characters, at least one uppercase, one lowercase, one digit
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, "Password is strong"


# ==================== FORMATTING FUNCTIONS ====================

def format_complaint_id():
    """Generate a formatted complaint ID"""
    from random import choices
    import string
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(choices(string.digits, k=4))
    return f"CMP-{timestamp}-{random_suffix}"


def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string"""
    if isinstance(dt, datetime):
        return dt.strftime(format)
    return str(dt)


def parse_datetime(date_string, format='%Y-%m-%d %H:%M:%S'):
    """Parse datetime string to datetime object"""
    try:
        return datetime.strptime(date_string, format)
    except ValueError:
        return None


def get_relative_time(dt):
    """Get human-readable relative time (e.g., '2 hours ago')"""
    if not isinstance(dt, datetime):
        return "Unknown"
    
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"


# ==================== RESPONSE FUNCTIONS ====================

def success_response(message, data=None, status_code=200):
    """Generate a standard success response"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return response, status_code


def error_response(message, error_code=None, status_code=400):
    """Generate a standard error response"""
    response = {
        'success': False,
        'message': message
    }
    if error_code:
        response['error_code'] = error_code
    return response, status_code


# ==================== TRANSLATION DICTIONARY ====================

TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to Civic Issues Reporting and Resolution System',
        'login': 'Login',
        'logout': 'Logout',
        'submit_complaint': 'Submit Complaint',
        'my_complaints': 'My Complaints',
        'phone_number': 'Phone Number',
        'password': 'Password',
        'verify': 'Verify',
        'resolved': 'Resolved',
        'pending': 'Pending',
    },
    'ta': {
        'welcome': 'சிவிக் பிரச்சனைகள் புகார் மற்றும் தீர்வு முறைமைக்கு வரவேற்கிறோம்',
        'login': 'உள்நுழைக',
        'logout': 'வெளியேறு',
        'submit_complaint': 'புகார் சமர்பிக்க',
        'my_complaints': 'என் புகார்கள்',
        'phone_number': 'ফোன் எண்',
        'password': 'கடவுச்சொல்',
        'verify': 'சரிபார்க்க',
        'resolved': 'தீர்க்கப்பட்டது',
        'pending': 'நிலுவையில் உள்ள',
    }
}


def get_translated_text(key, language='en'):
    """Get translated text for a key"""
    if language not in TRANSLATIONS:
        language = 'en'
    return TRANSLATIONS[language].get(key, key)


# ==================== STATUS COLOR MAPPING ====================

STATUS_COLORS = {
    'submitted': 'yellow',
    'verified': 'blue',
    'assigned': 'purple',
    'resolved': 'green',
    'rejected': 'red'
}


def get_status_color(status):
    """Get color for complaint status"""
    return STATUS_COLORS.get(status, 'gray')

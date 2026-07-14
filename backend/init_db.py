"""
Database initialization and seed data for Civic Issues Reporting and Resolution System
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")


def seed_demo_data():
    """Create demo/sample data for testing"""
    with app.app_context():
        # Check if data already exists
        if User.query.first() is not None:
            print("⚠ Demo data already exists. Skipping seed operation.")
            return

        try:
            # Create citizen users
            citizen1 = User(
                phone='9876543210',
                role='citizen',
                name='Rajesh Kumar',
                created_at=datetime.now()
            )
            citizen2 = User(
                phone='9876543211',
                role='citizen',
                name='Priya Singh',
                created_at=datetime.now()
            )

            # Create municipal officer
            municipal_officer = User(
                user_id='MUN001',
                password=generate_password_hash('password123'),
                role='municipal',
                name='Municipal Officer',
                pincode='600001',
                created_at=datetime.now()
            )

            # Create department officials
            dept_officer1 = User(
                user_id='DEPT001',
                password=generate_password_hash('password123'),
                role='dept',
                name='Municipal Corp Officer',
                department='Municipal Corporation',
                pincode='600001',
                created_at=datetime.now()
            )
            dept_officer2 = User(
                user_id='DEPT002',
                password=generate_password_hash('password123'),
                role='dept',
                name='Electrical Board Officer',
                department='Electrical Board',
                pincode='600001',
                created_at=datetime.now()
            )
            dept_officer3 = User(
                user_id='DEPT003',
                password=generate_password_hash('password123'),
                role='dept',
                name='Fire Station Officer',
                department='Fire Station',
                pincode='600001',
                created_at=datetime.now()
            )

            # Create police officer
            police_officer = User(
                user_id='POLICE001',
                password=generate_password_hash('password123'),
                role='police',
                name='Police Officer',
                pincode='600001',
                created_at=datetime.now()
            )

            # Create some sample complaints
            from app import Complaint
            
            complaint1 = Complaint(
                complaint_id='COM600001001',
                phone='9876543210',
                reporter=citizen1,
                reporter_name='Rajesh Kumar',
                title='Pothole',
                complaint_type='Roads',
                description='Large pothole in the middle of the road near the market.',
                district='Chennai',
                pincode='600001',
                location='Market Road, Central Street',
                coordinates='13.0827, 80.2707',
                status='submitted',
                created_at=datetime.now()
            )

            complaint2 = Complaint(
                complaint_id='COM600001002',
                phone='9876543211',
                reporter=citizen2,
                reporter_name='Priya Singh',
                title='Street Light',
                complaint_type='Electricity',
                description='Street light not working for a week, causing safety issues at night.',
                district='Chennai',
                pincode='600001',
                location='Subway Lane, Block B',
                coordinates='13.0850, 80.2750',
                status='in_progress',
                forwarded_department='Electrical Board',
                resolution_notes='Work started. Replacing the bulb and fixing wiring.',
                created_at=datetime.now()
            )

            # Add all users and complaints to session
            db.session.add_all([
                citizen1, citizen2, municipal_officer, 
                dept_officer1, dept_officer2, dept_officer3, 
                police_officer, complaint1, complaint2
            ])
            db.session.commit()

            print("✓ Demo data created successfully!")
            print("\nDemo Credentials:")
            print("\n--- CITIZEN USERS ---")
            print("Phone: 9876543210 | Name: Rajesh Kumar")
            print("Phone: 9876543211 | Name: Priya Singh")
            print("(Use these for OTP-based login)")
            
            print("\n--- MUNICIPAL OFFICER ---")
            print("User ID: MUN001")
            print("Password: password123")
            print("Pincode: 600001")
            
            print("\n--- DEPARTMENT OFFICIAL ---")
            print("User ID: DEPT001")
            print("Password: password123")
            print("Department: Municipal Corporation")
            print("Pincode: 600001")
            
            print("\n--- POLICE OFFICER ---")
            print("User ID: POLICE001")
            print("Password: password123")
            print("Pincode: 600001")

        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating demo data: {e}")


def clear_database():
    """Clear all data from database (USE WITH CAUTION)"""
    with app.app_context():
        if input("Are you sure you want to delete all data? (yes/no): ").lower() == 'yes':
            db.drop_all()
            print("✓ Database cleared")
        else:
            print("Operation cancelled")


def reset_database():
    """Reset database: drop all tables and recreate"""
    with app.app_context():
        if input("Are you sure you want to reset the database? (yes/no): ").lower() == 'yes':
            db.drop_all()
            db.create_all()
            seed_demo_data()
            print("✓ Database reset complete")
        else:
            print("Operation cancelled")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'init':
            init_db()
        elif command == 'seed':
            seed_demo_data()
        elif command == 'reset':
            reset_database()
        elif command == 'clear':
            clear_database()
        else:
            print("Unknown command. Available commands:")
            print("  python init_db.py init   - Initialize database")
            print("  python init_db.py seed   - Create demo data")
            print("  python init_db.py reset  - Reset database")
            print("  python init_db.py clear  - Clear all data")
    else:
        print("Initializing database and creating demo data...")
        init_db()
        seed_demo_data()

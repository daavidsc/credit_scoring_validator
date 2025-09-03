"""
User authentication and management module
Uses bcrypt for secure password hashing
"""
import bcrypt
import os
import json
from datetime import datetime, timedelta
from flask_login import UserMixin
import secrets

class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, user_id, username, password_hash, created_at=None, last_login=None, is_admin=False):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.last_login = last_login
        self.is_admin = is_admin
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow().isoformat()
        UserManager.save_user(self)
    
    def to_dict(self):
        """Convert user to dictionary for storage"""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_admin': self.is_admin
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        return cls(
            user_id=data['id'],
            username=data['username'],
            password_hash=data['password_hash'],
            created_at=data.get('created_at'),
            last_login=data.get('last_login'),
            is_admin=data.get('is_admin', False)
        )

class UserManager:
    """Manages user authentication and storage"""
    
    USERS_FILE = 'auth/users.json'
    
    @staticmethod
    def _ensure_auth_dir():
        """Ensure auth directory exists"""
        os.makedirs('auth', exist_ok=True)
    
    @staticmethod
    def _load_users():
        """Load users from JSON file"""
        UserManager._ensure_auth_dir()
        if not os.path.exists(UserManager.USERS_FILE):
            return {}
        
        try:
            with open(UserManager.USERS_FILE, 'r') as f:
                data = json.load(f)
                return {uid: User.from_dict(user_data) for uid, user_data in data.items()}
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return {}
    
    @staticmethod
    def _save_users(users):
        """Save users to JSON file"""
        UserManager._ensure_auth_dir()
        data = {uid: user.to_dict() for uid, user in users.items()}
        with open(UserManager.USERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def create_user(username, password, is_admin=False):
        """Create a new user with hashed password"""
        users = UserManager._load_users()
        
        # Check if username already exists
        for user in users.values():
            if user.username.lower() == username.lower():
                return None, "Username already exists"
        
        # Generate unique user ID
        user_id = secrets.token_hex(8)
        while user_id in users:
            user_id = secrets.token_hex(8)
        
        # Hash password
        password_hash = UserManager.hash_password(password)
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            is_admin=is_admin
        )
        
        # Save user
        users[user_id] = user
        UserManager._save_users(users)
        
        return user, "User created successfully"
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password"""
        users = UserManager._load_users()
        
        for user in users.values():
            if user.username.lower() == username.lower():
                if user.check_password(password):
                    user.update_last_login()
                    return user
                return None
        
        return None
    
    @staticmethod
    def get_user(user_id):
        """Get user by ID"""
        users = UserManager._load_users()
        return users.get(user_id)
    
    @staticmethod
    def save_user(user):
        """Save/update a user"""
        users = UserManager._load_users()
        users[user.id] = user
        UserManager._save_users(users)
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        return list(UserManager._load_users().values())
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        users = UserManager._load_users()
        if user_id in users:
            del users[user_id]
            UserManager._save_users(users)
            return True
        return False
    
    @staticmethod
    def setup_default_admin():
        """Setup default admin user if no users exist"""
        users = UserManager._load_users()
        if not users:
            # Create default admin user
            admin_password = secrets.token_urlsafe(16)  # Generate secure random password
            user, message = UserManager.create_user("admin", admin_password, is_admin=True)
            
            if user:
                print(f"🔑 Default admin user created!")
                print(f"   Username: admin")
                print(f"   Password: {admin_password}")
                print(f"   ⚠️  Please save this password and change it after first login!")
                return admin_password
            else:
                print(f"❌ Failed to create admin user: {message}")
                return None
        return None

# Initialize default admin on import if needed
if __name__ == "__main__":
    UserManager.setup_default_admin()

"""
Authentication forms with CSRF protection
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from auth.user_manager import UserManager

class LoginForm(FlaskForm):
    """Login form with validation"""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=50, message="Username must be between 3 and 50 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=6, message="Password must be at least 6 characters")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateUserForm(FlaskForm):
    """Form for creating new users (admin only)"""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=50, message="Username must be between 3 and 50 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm the password")
    ])
    is_admin = BooleanField('Admin User')
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        """Check if username already exists"""
        users = UserManager.get_all_users()
        for user in users:
            if user.username.lower() == username.data.lower():
                raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_confirm_password(self, confirm_password):
        """Check if passwords match"""
        if self.password.data != confirm_password.data:
            raise ValidationError('Passwords do not match.')

class ChangePasswordForm(FlaskForm):
    """Form for changing password"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message="Current password is required")
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required"),
        Length(min=8, message="Password must be at least 8 characters")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm the new password")
    ])
    submit = SubmitField('Change Password')
    
    def validate_confirm_password(self, confirm_password):
        """Check if passwords match"""
        if self.new_password.data != confirm_password.data:
            raise ValidationError('Passwords do not match.')

"""
Authentication module for Credit Scoring Validator
Provides secure user authentication with bcrypt password hashing
"""

from .user_manager import UserManager, User
from .forms import LoginForm, CreateUserForm, ChangePasswordForm

__all__ = ['UserManager', 'User', 'LoginForm', 'CreateUserForm', 'ChangePasswordForm']

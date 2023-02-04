from apps import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hashed = db.Column(db.String(128), nullable=False)

    def __init__(self, employee_id: str, username: str, email: str, password_plaintext: str):
        """
        Creating new User object using the email address and hashing the plaintext password using
        the Werkzeug.Security.
        """
        self.employee_id = employee_id
        self.username = username
        self.email = email
        self.password_hashed = self._generate_password_hash(password_plaintext)

    @staticmethod
    def _generate_password_hash(password_plaintext: str):
        return generate_password_hash(password_plaintext)
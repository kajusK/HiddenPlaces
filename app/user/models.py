from datetime import datetime
from app.database import DBItem, db
from app.extensions import bcrypt
from flask_login import UserMixin


class User(DBItem, UserMixin):
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    # hashed password
    password = db.Column(db.LargeBinary(128), nullable=False)
    date_created = db.Column(db.DateTime(), default=db.func.now())
    last_login = db.Column(db.DateTime(), default=datetime.fromtimestamp(0))
    active = db.Column(db.Boolean(), default=True)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        super().__init__(username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        ret = bcrypt.check_password_hash(self.password, password)
        if ret:
            self.last_login = db.func.now()
            self.commit()
        return ret

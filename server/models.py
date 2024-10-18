from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt
from config import db

bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    _password_hash = Column('password_hash', String, nullable=False)
    image_url = Column(String)
    bio = Column(String)

    # Relationship: One user can have many recipes
    recipes = relationship('Recipe', back_populates='user', lazy=True)

    @property
    def password(self):
        raise AttributeError("Password is not accessible")

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    @property
    def password_hash(self):
        raise AttributeError("Password hash is not accessible") 

    @password_hash.setter
    def password_hash(self, value):
        # If a plain password is passed, hash it before storing
        if not value.startswith("$2b$"):  # bcrypt hashes start with $2b$
            self._password_hash = bcrypt.generate_password_hash(value).decode('utf-8')
        else:
            self._password_hash = value

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
    
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    instructions = Column(String, nullable=False)
    minutes_to_complete = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Not null constraint

    # Relationship: A recipe belongs to a user
    user = relationship("User", back_populates="recipes")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.user_id:
            # Get the first user in the database as the default user
            default_user = db.session.query(User).first()
            if default_user:
                self.user_id = default_user.id
            else:
                pass


    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions

    @validates('user_id')
    def validate_user_id(self, key, user_id):
        if not user_id:
            # Set a default user if none is provided
            default_user = db.session.query(User).first()
            if default_user:
                return default_user.id
            else:
                # Raise an exception or handle it in a way that suits your application
                raise ValueError("No users available to assign as default.")
        return user_id
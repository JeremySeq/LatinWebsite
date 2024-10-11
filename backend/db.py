# db.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

def setup_db(app):
    db.init_app(app)
    return db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    reputation = db.Column(db.Integer, default=0)  # Optional field to track reputation
    translations = db.relationship('Translation', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'reputation': self.reputation
        }


class PassageCollection(db.Model):
    __tablename__ = "passage_collections"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)

class Passage(db.Model):
    __tablename__ = 'passages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    latin_text = db.Column(db.Text, nullable=False)
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ForeignKey can be added later for Users table
    collection = db.Column(db.Integer, db.ForeignKey('passage_collections.id'), nullable=True)

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "latin_text": self.latin_text,
            "submitted_by_user_id": self.submitted_by_user_id,
            "collection": self.collection
        }

class Translation(db.Model):
    __tablename__ = 'translations'
    id = db.Column(db.Integer, primary_key=True)
    passage_id = db.Column(db.Integer, db.ForeignKey('passages.id'), nullable=False)
    english_text = db.Column(db.Text, nullable=False)
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    is_approved_official = db.Column(db.Boolean, default=False)

    # Add a column for translation type (piece by piece or full)
    translation_type = db.Column(Enum('piece_by_piece', 'full_translation', name='translation_type'), nullable=False)

    # For piece-by-piece translation, you can add a relationship or field to store the parts
    parts = db.relationship('TranslationPart', backref='translation', lazy=True, cascade="all, delete")


    def to_json(self):
        if self.translation_type == 'piece_by_piece':
            return {
                "id": self.id,
                "passage_id": self.passage_id,
                "translation_type": self.translation_type,
                "parts": [part.to_json() for part in self.parts],
                "submitted_by_user_id": self.submitted_by_user_id,
                "is_approved_official": self.is_approved_official
            }
        else:  # Full translation
            return {
                "id": self.id,
                "passage_id": self.passage_id,
                "translation_type": self.translation_type,
                "english_text": self.english_text,
                "submitted_by_user_id": self.submitted_by_user_id,
                "is_approved_official": self.is_approved_official
            }

class TranslationPart(db.Model):
    __tablename__ = 'translation_parts'
    id = db.Column(db.Integer, primary_key=True)
    translation_id = db.Column(db.Integer, db.ForeignKey('translations.id'), nullable=False)
    latin_section = db.Column(db.Text, nullable=False)
    english_section = db.Column(db.Text, nullable=False)

    def to_json(self):
        return {
            "latin_section": self.latin_section,
            "english_section": self.english_section
        }

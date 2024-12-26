import logging
import json
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger()

db = SQLAlchemy()


def commit_db_changes():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error committing changes: {e}")
        db.session.rollback()
        return False
    return True

class Uploads(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_owner = db.Column(db.String(100), nullable=False)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, user_name, user_upload_amount, user_upload_limit, user_files):
        self.name = user_name
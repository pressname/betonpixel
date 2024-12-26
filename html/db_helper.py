"""
@file db_user_helper.py
@brief This module provides helper functions to interact with the 'Users' table in the database.

@details This module includes functions to retrieve user information, add new users,
            and remove users from the database. SQLAlchemy is used for database interaction,
            and exceptions are handled with proper logging.

@dependencies
- SQLAlchemy for database ORM
- Environment variables for configuration
- Users model from db_models

@author Pressname, Inflac
@date 2024
"""

import os
import logging

from typing import Union

from models import Users, db
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger()

def get_user_from_users(user_name: str) -> Union[Users, bool]:
    """
    Retrieve a user from the users table by username.

    This function queries the database for a user with the specified username.
    If the user exists, it returns the Users object; otherwise, it returns False.

    @param user_name The username to look for.
    @return The Users object if found, False otherwise.

    @exception SQLAlchemyError If there is an error while querying the database.
    """
    try:
        user = db.session.query(Users).filter(Users.name == user_name).first()
        if user:
            logger.debug(f"User '{user_name}' found in the users table.")
            return user
        else:
            logger.debug(f"User '{user_name}' not found in the users table.")
            return False
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while retrieving a user from the users table: {e}")
        return False

def add_user_to_users(user_name: str) -> bool:
    """
    Add a new user to the users table.

    This function adds a user with specified attributes to the users table. 
    If a user with the same username already exists, it will not add a duplicate.

    @param user_name The username to add.

    @return True if the user is added successfully, False otherwise.

    @exception SQLAlchemyError If there is an error while adding the user to the database.
    """

    if get_user_from_users(user_name):
        logger.warning(f"User '{user_name}' already exists in the users table.")
        return False

    try:
        user = Users(user_name=user_name)
        db.session.add(user)
        db.session.commit()
        logger.info(f"User '{user_name}' added to the users table successfully.")
        return True
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while adding a user to the users table: {e}")
    return False
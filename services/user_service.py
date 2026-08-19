from database.db import SessionLocal

from database.models import (
    User,
    Leaderboard
)


# =====================================================
# GET USER BY USERNAME
# =====================================================

def get_user_by_username(username):

    db = SessionLocal()

    try:

        return (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

    finally:

        db.close()


# =====================================================
# GET USER BY ID
# =====================================================

def get_user_by_id(user_id):

    db = SessionLocal()

    try:

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    finally:

        db.close()


# =====================================================
# VALIDATE LOGIN
# =====================================================

def login(username, password):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if not user:
            return None

        if user.password != password:
            return None

        return user

    finally:

        db.close()


# =====================================================
# CREATE USER
# =====================================================

def create_user(
    username,
    password,
    is_admin=False
):

    db = SessionLocal()

    try:

        existing_user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing_user:
            return None

        user = User(
            username=username,
            password=password,
            is_admin=is_admin
        )

        db.add(user)

        db.commit()

        db.refresh(user)

        leaderboard = Leaderboard(
            user_id=user.id,
            total_points=0,
            weekly_wins=0,
            correct_picks=0,
            total_picks=0,
            rank=0
        )

        db.add(leaderboard)

        db.commit()

        return user

    except Exception:

        db.rollback()

        return None

    finally:

        db.close()


# =====================================================
# GET ALL USERS
# =====================================================

def get_all_users():

    db = SessionLocal()

    try:

        return (
            db.query(User)
            .order_by(User.username)
            .all()
        )

    finally:

        db.close()


# =====================================================
# DELETE USER
# =====================================================

def delete_user(user_id):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return False

        db.delete(user)

        db.commit()

        return True

    except Exception:

        db.rollback()

        return False

    finally:

        db.close()


# =====================================================
# ADMIN CHECK
# =====================================================

def is_admin(user_id):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return False

        return user.is_admin

    finally:

        db.close()


# =====================================================
# USER EXISTS
# =====================================================

def user_exists(username):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        return user is not None

    finally:

        db.close()
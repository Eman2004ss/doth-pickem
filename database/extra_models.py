"""Additional tables for tiebreakers and long-range prediction pools.

These are intentionally kept in a separate module so the existing production
models do not need destructive schema edits.  Import this module before
Base.metadata.create_all() and SQLAlchemy will create only the missing tables.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from database.db import Base


class TiebreakerPick(Base):
    __tablename__ = "tiebreaker_picks"
    __table_args__ = (
        UniqueConstraint("user_id", "week_id", name="uq_tiebreaker_user_week"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_id = Column(Integer, ForeignKey("weeks.id"), nullable=False)
    predicted_total = Column(Integer, nullable=False)
    locked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SpecialPick(Base):
    __tablename__ = "special_picks"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "category", "period", "slot",
            name="uq_special_pick_user_category_period_slot",
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    period = Column(String, nullable=False)
    slot = Column(String, nullable=False)
    selection = Column(String, nullable=False)
    rank = Column(Integer)
    points_awarded = Column(Integer, default=0, nullable=False)
    locked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SpecialOutcome(Base):
    __tablename__ = "special_outcomes"
    __table_args__ = (
        UniqueConstraint("category", "key", name="uq_special_outcome_category_key"),
    )

    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    key = Column(String, nullable=False)
    result = Column(String, nullable=False)
    had_bye = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SpecialLock(Base):
    __tablename__ = "special_locks"
    __table_args__ = (
        UniqueConstraint("category", "period", name="uq_special_lock_category_period"),
    )

    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    period = Column(String, nullable=False)
    lock_at = Column(DateTime)
    force_locked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SpecialBonus(Base):
    __tablename__ = "special_bonuses"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "category", "bonus_key",
            name="uq_special_bonus_user_category_key",
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    bonus_key = Column(String, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlayoffGame(Base):
    __tablename__ = "playoff_games"
    __table_args__ = (
        UniqueConstraint(
            "sport", "round_key", "slot",
            name="uq_playoff_game_sport_round_slot",
        ),
    )

    id = Column(Integer, primary_key=True)
    sport = Column(String, nullable=False)       # "cfb" or "nfl"
    round_key = Column(String, nullable=False)    # e.g. "first_round", "wild_card"
    slot = Column(Integer, nullable=False)        # game number within the round, 1-indexed
    team1 = Column(String, default="TBD", nullable=False)
    team2 = Column(String, default="TBD", nullable=False)
    winner = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlayoffPick(Base):
    __tablename__ = "playoff_picks"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "sport", "round_key", "slot",
            name="uq_playoff_pick_user_sport_round_slot",
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sport = Column(String, nullable=False)
    round_key = Column(String, nullable=False)
    slot = Column(Integer, nullable=False)
    selection = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

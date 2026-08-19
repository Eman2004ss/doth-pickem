from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database.db import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    is_admin = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    picks = relationship(
        "Pick",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Team(Base):

    __tablename__ = "teams"

    id = Column(
        Integer,
        primary_key=True
    )

    team_name = Column(
        String,
        unique=True,
        nullable=False
    )

    espn_team_id = Column(
        String
    )

    abbreviation = Column(
        String
    )

    conference = Column(
        String
    )

    sport = Column(
        String,
        default="ncaa"
    )

    source = Column(
        String,
        default="manual"
    )

    logo_path = Column(
        String
    )

    primary_color = Column(
        String
    )

    secondary_color = Column(
        String
    )

    record = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Week(Base):

    __tablename__ = "weeks"

    id = Column(
        Integer,
        primary_key=True
    )

    week_number = Column(
        Integer,
        unique=True,
        nullable=False
    )

    active = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    games = relationship(
        "Game",
        back_populates="week",
        cascade="all, delete-orphan"
    )


class Game(Base):

    __tablename__ = "games"

    id = Column(
        Integer,
        primary_key=True
    )

    week_id = Column(
        Integer,
        ForeignKey("weeks.id"),
        nullable=False
    )

    game_number = Column(
        Integer,
        nullable=False
    )

    tier = Column(
        String,
        nullable=False
    )

    sport = Column(
        String,
        default="ncaa"
    )

    source = Column(
        String,
        default="espn"
    )

    espn_event_id = Column(
        String
    )

    kickoff_time = Column(
        DateTime
    )

    locked = Column(
        Boolean,
        default=False
    )

    home_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False
    )

    away_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False
    )

    home_score = Column(
        Integer,
        default=0
    )

    away_score = Column(
        Integer,
        default=0
    )

    game_status = Column(
        String,
        default="Scheduled"
    )

    quarter = Column(
        String
    )

    game_clock = Column(
        String
    )

    winner_team_id = Column(
        Integer,
        ForeignKey("teams.id")
    )

    completed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    week = relationship(
        "Week",
        back_populates="games"
    )

    home_team = relationship(
        "Team",
        foreign_keys=[home_team_id]
    )

    away_team = relationship(
        "Team",
        foreign_keys=[away_team_id]
    )

    winner_team = relationship(
        "Team",
        foreign_keys=[winner_team_id]
    )

    picks = relationship(
        "Pick",
        back_populates="game",
        cascade="all, delete-orphan"
    )


class Pick(Base):

    __tablename__ = "picks"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    game_id = Column(
        Integer,
        ForeignKey("games.id"),
        nullable=False
    )

    selected_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False
    )

    locked = Column(
        Boolean,
        default=False
    )

    is_correct = Column(
        Boolean
    )

    points_awarded = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="picks"
    )

    game = relationship(
        "Game",
        back_populates="picks"
    )

    selected_team = relationship(
        "Team"
    )


class Leaderboard(Base):

    __tablename__ = "leaderboard"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    total_points = Column(
        Integer,
        default=0
    )

    weekly_wins = Column(
        Integer,
        default=0
    )

    correct_picks = Column(
        Integer,
        default=0
    )

    total_picks = Column(
        Integer,
        default=0
    )

    rank = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User"
    )


class WeeklyWinner(Base):

    __tablename__ = "weekly_winners"

    id = Column(
        Integer,
        primary_key=True
    )

    week_id = Column(
        Integer,
        ForeignKey("weeks.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    bonus_points = Column(
        Integer,
        default=5
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    week = relationship(
        "Week"
    )

    user = relationship(
        "User"
    )


class Setting(Base):

    __tablename__ = "settings"

    id = Column(
        Integer,
        primary_key=True
    )

    setting_name = Column(
        String,
        unique=True,
        nullable=False
    )

    setting_value = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class SystemLog(Base):

    __tablename__ = "system_logs"

    id = Column(
        Integer,
        primary_key=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    log_type = Column(
        String
    )

    message = Column(
        String
    )
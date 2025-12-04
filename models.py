"""
Database models for the Telegram AI Bot
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language = Column(String(10), default='ru', nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    premium_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    service_usage = relationship("ServiceUsage", back_populates="user", cascade="all, delete-orphan")
    request_logs = relationship("RequestLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username}, is_premium={self.is_premium})>"


class ServiceUsage(Base):
    """Service usage tracking for rate limiting"""
    __tablename__ = 'service_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    service_name = Column(String(50), nullable=False, index=True)
    request_count = Column(Integer, default=0, nullable=False)
    last_reset = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="service_usage")
    
    def __repr__(self):
        return f"<ServiceUsage(user_id={self.user_id}, service={self.service_name}, count={self.request_count})>"


class RequestLog(Base):
    """Detailed request logging for admin analytics"""
    __tablename__ = 'request_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    service_name = Column(String(50), nullable=False, index=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False)  # success, error, rate_limited
    error_message = Column(Text, nullable=True)
    processing_time = Column(Integer, nullable=True)  # in milliseconds
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="request_logs")
    
    def __repr__(self):
        return f"<RequestLog(user_id={self.user_id}, service={self.service_name}, status={self.status})>"

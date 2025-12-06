"""
Database models for the Telegram AI Bot
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()

class User(Base):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default='ru', nullable=False)
    
    # Premium Fields
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    premium_expiry: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Package tracking
    package_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('premium_packages.id'), nullable=True)
    
    # Time stamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    package: Mapped["PremiumPackage"] = relationship("PremiumPackage", back_populates="users")
    service_usage: Mapped[list["ServiceUsage"]] = relationship("ServiceUsage", back_populates="user", cascade="all, delete-orphan")
    request_logs: Mapped[list["RequestLog"]] = relationship("RequestLog", back_populates="user", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    user_limits: Mapped[list["UserLimit"]] = relationship("UserLimit", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username}, package_id={self.package_id})>"


class PremiumPackage(Base):
    """Defines different subscription packages (Basic, Pro, VIP)"""
    __tablename__ = 'premium_packages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    package_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # e.g., 'pro', 'basic'
    name_uz: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="package")

    def __repr__(self):
        return f"<PremiumPackage(key={self.package_key}, price={self.price})>"


class UserLimit(Base):
    """Stores the current daily/monthly limit usage for a specific user and service."""
    __tablename__ = 'user_limits'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g., 'image_generation'
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    limit_type: Mapped[str] = mapped_column(String(10), nullable=False) # 'daily', 'monthly', 'unlimited'
    last_reset: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_limits")

    def __repr__(self):
        return f"<UserLimit(user_id={self.user_id}, service={self.service_name}, count={self.usage_count})>"


class Payment(Base):
    """Records payment transactions, especially for manual confirmation"""
    __tablename__ = 'payments'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    package_id: Mapped[int] = mapped_column(Integer, ForeignKey('premium_packages.id'), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False) # pending, confirmed, failed
    payment_method: Mapped[str] = mapped_column(String(50), default='card_transfer', nullable=False)
    transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True) # Optional external ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")
    package: Mapped["PremiumPackage"] = relationship("PremiumPackage")

    def __repr__(self):
        return f"<Payment(user_id={self.user_id}, package={self.package_id}, status={self.status}, amount={self.amount})>"


class PromoCode(Base):
    """Manages promotional codes for discounts or bonuses"""
    __tablename__ = 'promo_codes'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    discount_percent: Mapped[int | None] = mapped_column(Integer, nullable=True) # e.g., 20%
    bonus_days: Mapped[int | None] = mapped_column(Integer, nullable=True) # e.g., +7 days
    max_uses: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PromoCode(code={self.code}, discount={self.discount_percent}%, active={self.is_active})>"


class ServiceUsage(Base):
    """(Kept for compatibility, though limit checking moved to UserLimit)"""
    __tablename__ = 'service_usage'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reset: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="service_usage")
    
    def __repr__(self):
        return f"<ServiceUsage(user_id={self.user_id}, service={self.service_name}, count={self.request_count})>"


class RequestLog(Base):
    """Detailed request logging for admin analytics"""
    __tablename__ = 'request_logs'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    request_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, error, rate_limited
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_time: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in milliseconds
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="request_logs")
    
    def __repr__(self):
        return f"<RequestLog(user_id={self.user_id}, service={self.service_name}, status={self.status})>"

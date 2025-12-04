"""
Database manager for handling all database operations
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func, and_
from .models import Base, User, ServiceUsage, RequestLog
import config

class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, database_url: str = config.DATABASE_URL):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_or_create_user(self, telegram_id: int, username: str = None, 
                                  first_name: str = None, last_name: str = None) -> User:
        """Get existing user or create new one"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            else:
                # Update last active time
                user.last_active = datetime.utcnow()
                await session.commit()
            
            return user
    
    async def get_user_language(self, telegram_id: int) -> str:
        """Get user's preferred language"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User.language).where(User.telegram_id == telegram_id)
            )
            language = result.scalar_one_or_none()
            return language if language else 'ru'
    
    async def set_user_language(self, telegram_id: int, language: str):
        """Set user's preferred language"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.language = language
                await session.commit()
    
    async def is_user_premium(self, telegram_id: int) -> bool:
        """Check if user has active premium subscription"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_premium:
                return False
            
            if user.premium_expiry and user.premium_expiry < datetime.utcnow():
                user.is_premium = False
                await session.commit()
                return False
            
            return True
    
    async def check_rate_limit(self, telegram_id: int, service_name: str) -> tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit for a service
        Returns: (is_allowed, used_count, limit)
        """
        # Premium users have no limits
        if await self.is_user_premium(telegram_id):
            return True, 0, -1
        
        limit = config.RATE_LIMITS.get(service_name, 10)
        
        async with self.async_session() as session:
            # Get user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False, 0, limit
            
            # Get or create service usage record
            result = await session.execute(
                select(ServiceUsage).where(
                    and_(
                        ServiceUsage.user_id == user.id,
                        ServiceUsage.service_name == service_name
                    )
                )
            )
            usage = result.scalar_one_or_none()
            
            # Reset if last reset was more than 24 hours ago
            now = datetime.utcnow()
            if usage and (now - usage.last_reset) > timedelta(days=1):
                usage.request_count = 0
                usage.last_reset = now
                await session.commit()
            
            if not usage:
                usage = ServiceUsage(
                    user_id=user.id,
                    service_name=service_name,
                    request_count=0
                )
                session.add(usage)
                await session.commit()
            
            # Check limit
            if usage.request_count >= limit:
                return False, usage.request_count, limit
            
            return True, usage.request_count, limit
    
    async def increment_usage(self, telegram_id: int, service_name: str):
        """Increment service usage count"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return
            
            result = await session.execute(
                select(ServiceUsage).where(
                    and_(
                        ServiceUsage.user_id == user.id,
                        ServiceUsage.service_name == service_name
                    )
                )
            )
            usage = result.scalar_one_or_none()
            
            if usage:
                usage.request_count += 1
            else:
                usage = ServiceUsage(
                    user_id=user.id,
                    service_name=service_name,
                    request_count=1
                )
                session.add(usage)
            
            await session.commit()
    
    async def log_request(self, telegram_id: int, service_name: str, 
                         request_data: Dict[str, Any], status: str,
                         response_data: Optional[Dict[str, Any]] = None,
                         error_message: Optional[str] = None,
                         processing_time: Optional[int] = None):
        """Log a service request"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return
            
            log = RequestLog(
                user_id=user.id,
                service_name=service_name,
                request_data=request_data,
                response_data=response_data,
                status=status,
                error_message=error_message,
                processing_time=processing_time
            )
            session.add(log)
            await session.commit()
    
    async def get_admin_stats(self) -> Dict[str, Any]:
        """Get statistics for admin panel"""
        async with self.async_session() as session:
            # Total users
            result = await session.execute(select(func.count(User.id)))
            total_users = result.scalar()
            
            # Active users (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            result = await session.execute(
                select(func.count(User.id)).where(User.last_active >= week_ago)
            )
            active_users = result.scalar()
            
            # Premium users
            result = await session.execute(
                select(func.count(User.id)).where(User.is_premium == True)
            )
            premium_users = result.scalar()
            
            # Service usage stats
            result = await session.execute(
                select(
                    ServiceUsage.service_name,
                    func.sum(ServiceUsage.request_count).label('total')
                ).group_by(ServiceUsage.service_name)
            )
            service_stats = {row[0]: row[1] for row in result}
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "premium_users": premium_users,
                "service_stats": service_stats
            }

# Global database manager instance
db_manager = DatabaseManager()

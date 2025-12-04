"""
Premium Service - Subscription management
"""
from telegram import Update
from telegram.ext import ContextTypes
from database import db_manager
from locales import get_text
from utils.keyboards import get_main_menu_keyboard

class PremiumService:
    """Premium subscription service"""
    
    @staticmethod
    async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show premium information and status"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        # Check if user has premium
        is_premium = await db_manager.is_user_premium(user.id)
        
        if is_premium:
            # Get premium expiry date
            async with db_manager.async_session() as session:
                from sqlalchemy import select
                from database.models import User
                
                result = await session.execute(
                    select(User).where(User.telegram_id == user.id)
                )
                user_obj = result.scalar_one_or_none()
                
                expiry = user_obj.premium_expiry.strftime("%Y-%m-%d") if user_obj.premium_expiry else "Unlimited"
            
            message = get_text(language, "premium_active", expiry=expiry)
        else:
            message = get_text(language, "premium_inactive")
        
        # Show premium features
        premium_info = get_text(language, "premium_start")
        full_message = f"{premium_info}\n\n{message}"
        
        await update.message.reply_text(
            full_message,
            reply_markup=get_main_menu_keyboard(language)
        )
    
    @staticmethod
    async def activate_premium(telegram_id: int, days: int = 30):
        """
        Activate premium subscription for a user
        
        This method should be called by admin or payment system
        
        Args:
            telegram_id: User's Telegram ID
            days: Number of days for premium subscription
        """
        from datetime import datetime, timedelta
        
        async with db_manager.async_session() as session:
            from sqlalchemy import select
            from database.models import User
            
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.is_premium = True
                user.premium_expiry = datetime.utcnow() + timedelta(days=days)
                await session.commit()
                return True
        
        return False
    
    @staticmethod
    async def deactivate_premium(telegram_id: int):
        """
        Deactivate premium subscription for a user
        
        Args:
            telegram_id: User's Telegram ID
        """
        async with db_manager.async_session() as session:
            from sqlalchemy import select
            from database.models import User
            
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.is_premium = False
                user.premium_expiry = None
                await session.commit()
                return True
        
        return False

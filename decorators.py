"""
Decorators for rate limiting and premium checks
"""
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from database import db_manager
from locales import get_text
import config

def rate_limit(service_name: str):
    """
    Decorator to check rate limits before executing a service, based on user package.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            language = await db_manager.get_user_language(user.id)
            
            # 1. Check rate limit using the new package-based logic
            is_allowed, used, limit = await db_manager.check_rate_limit(user.id, service_name)
            
            # If limit is -1 (unlimited) or allowed
            if is_allowed or limit == -1:
                # Execute the function
                result = await func(update, context, *args, **kwargs)
                
                # Increment usage counter (only if limit is not -1)
                if limit != -1:
                    await db_manager.increment_usage(user.id, service_name)
                
                return result
            
            # 2. If rate limit exceeded
            else:
                await update.message.reply_text(
                    get_text(language, "rate_limit_exceeded", used=used, limit=limit)
                )
                return
        
        return wrapper
    return decorator

def premium_required(func):
    """
    Decorator to check if user has premium subscription (for exclusive features)
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        # Check premium status
        is_premium = await db_manager.is_user_premium(user.id)
        
        if not is_premium:
            await update.message.reply_text(
                get_text(language, "premium_required_feature")
            )
            return
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper

def admin_only(func):
    """
    Decorator to restrict access to admin users only
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        # Import here to avoid circular dependency
        import config
        
        if user.id not in config.ADMIN_IDS:
            await update.message.reply_text(
                get_text(language, "admin_unauthorized")
            )
            return
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper

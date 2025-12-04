"""
Admin Panel - User and service management
"""
from telegram import Update
from telegram.ext import ContextTypes
from database import db_manager
from locales import get_text
from utils.decorators import admin_only
from services.premium import PremiumService

class AdminPanel:
    """Admin panel for bot management"""
    
    @staticmethod
    @admin_only
    async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        # Get statistics
        stats = await db_manager.get_admin_stats()
        
        # Format service stats
        service_stats_text = ""
        for service, count in stats['service_stats'].items():
            service_stats_text += f"  • {service}: {count}\n"
        
        if not service_stats_text:
            service_stats_text = "  No usage data yet"
        
        # Send statistics
        await update.message.reply_text(
            get_text(
                language, 
                "admin_stats",
                total_users=stats['total_users'],
                active_users=stats['active_users'],
                premium_users=stats['premium_users'],
                service_stats=service_stats_text
            )
        )
    
    @staticmethod
    @admin_only
    async def grant_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Grant premium to a user
        Usage: /grant_premium <user_id> <days>
        """
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        try:
            # Parse arguments
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(
                    "Usage: /grant_premium <user_id> <days>\n\nExample: /grant_premium 123456789 30"
                )
                return
            
            target_user_id = int(args[0])
            days = int(args[1])
            
            # Grant premium
            success = await PremiumService.activate_premium(target_user_id, days)
            
            if success:
                await update.message.reply_text(
                    f"✅ Premium granted to user {target_user_id} for {days} days"
                )
            else:
                await update.message.reply_text(
                    f"❌ User {target_user_id} not found"
                )
        
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid arguments. Usage: /grant_premium <user_id> <days>"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    @staticmethod
    @admin_only
    async def revoke_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Revoke premium from a user
        Usage: /revoke_premium <user_id>
        """
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        try:
            # Parse arguments
            args = context.args
            if len(args) < 1:
                await update.message.reply_text(
                    "Usage: /revoke_premium <user_id>\n\nExample: /revoke_premium 123456789"
                )
                return
            
            target_user_id = int(args[0])
            
            # Revoke premium
            success = await PremiumService.deactivate_premium(target_user_id)
            
            if success:
                await update.message.reply_text(
                    f"✅ Premium revoked from user {target_user_id}"
                )
            else:
                await update.message.reply_text(
                    f"❌ User {target_user_id} not found"
                )
        
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid arguments. Usage: /revoke_premium <user_id>"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    @staticmethod
    @admin_only
    async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        List recent users
        Usage: /list_users [limit]
        """
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        try:
            # Parse limit
            limit = 10
            if context.args and len(context.args) > 0:
                limit = int(context.args[0])
            
            # Get users
            async with db_manager.async_session() as session:
                from sqlalchemy import select
                from database.models import User
                
                result = await session.execute(
                    select(User).order_by(User.created_at.desc()).limit(limit)
                )
                users = result.scalars().all()
            
            if not users:
                await update.message.reply_text("No users found")
                return
            
            # Format user list
            user_list = f"📋 Recent Users (showing {len(users)}):\n\n"
            for u in users:
                premium_badge = "⭐" if u.is_premium else ""
                user_list += f"{premium_badge} ID: {u.telegram_id}\n"
                user_list += f"   Username: @{u.username or 'N/A'}\n"
                user_list += f"   Name: {u.first_name or ''} {u.last_name or ''}\n"
                user_list += f"   Language: {u.language}\n"
                user_list += f"   Joined: {u.created_at.strftime('%Y-%m-%d')}\n\n"
            
            await update.message.reply_text(user_list)
        
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid limit. Usage: /list_users [limit]"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    @staticmethod
    @admin_only
    async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Broadcast message to all users
        Usage: /broadcast <message>
        """
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        try:
            # Get message
            if not context.args:
                await update.message.reply_text(
                    "Usage: /broadcast <message>\n\nExample: /broadcast Hello everyone!"
                )
                return
            
            message = " ".join(context.args)
            
            # Get all users
            async with db_manager.async_session() as session:
                from sqlalchemy import select
                from database.models import User
                
                result = await session.execute(select(User))
                users = result.scalars().all()
            
            # Send message to all users
            success_count = 0
            fail_count = 0
            
            for target_user in users:
                try:
                    await context.bot.send_message(
                        chat_id=target_user.telegram_id,
                        text=f"📢 Broadcast Message:\n\n{message}"
                    )
                    success_count += 1
                except Exception:
                    fail_count += 1
            
            await update.message.reply_text(
                f"✅ Broadcast complete!\n\n"
                f"Sent: {success_count}\n"
                f"Failed: {fail_count}"
            )
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

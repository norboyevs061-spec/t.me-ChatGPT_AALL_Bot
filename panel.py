"""
Admin Panel - User and service management
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db_manager
from locales import get_text
from utils.decorators import admin_only
from services.premium import PremiumService
import config
from datetime import datetime, timedelta

# Conversation states for Admin flow
ADMIN_MENU, ADMIN_PROMO_CODE_CREATE = range(200, 202)

class AdminPanel:
    """Admin panel for bot management"""
    
    @staticmethod
    @admin_only
    async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics and revenue data (4, 9-bandlar)"""
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
                service_stats=service_stats_text,
                total_revenue=f"{stats['total_revenue']:,.0f} UZS",
                monthly_revenue=f"{stats['monthly_revenue']:,.0f} UZS",
                pending_payments_count=stats['pending_payments_count']
            )
        )
    
    @staticmethod
    @admin_only
    async def grant_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Grant premium to a user (Admin buyrug'i)
        Usage: /grant_premium <user_id> <days> [package_key]
        """
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(get_text(language, "grant_premium_usage"))
                return
            
            target_user_id = int(args[0])
            days = int(args[1])
            package_key = args[2] if len(args) > 2 else 'pro'
            
            # Grant premium (using updated logic in PremiumService)
            success = await PremiumService.activate_premium(target_user_id, days, package_key)
            
            if success:
                await update.message.reply_text(
                    f"✅ Premium granted to user {target_user_id} for {days} days ({package_key})"
                )
            else:
                await update.message.reply_text(
                    f"❌ User {target_user_id} not found or package error"
                )
        
        except ValueError:
            await update.message.reply_text(get_text(language, "grant_premium_usage"))
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
            args = context.args
            if len(args) < 1:
                await update.message.reply_text(get_text(language, "revoke_premium_usage"))
                return
            
            target_user_id = int(args[0])
            
            # Revoke premium (using updated logic in PremiumService)
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
            await update.message.reply_text(get_text(language, "revoke_premium_usage"))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    @staticmethod
    @admin_only
    async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        List recent users (Updated to show package)
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
                from database.models import User, PremiumPackage
                
                result = await session.execute(
                    select(User, PremiumPackage.package_key)
                    .outerjoin(PremiumPackage, User.package_id == PremiumPackage.id)
                    .order_by(User.created_at.desc()).limit(limit)
                )
                
                user_list_text = f"📋 Recent Users (showing {limit} max):\n\n"
                for u, package_key in result.all():
                    premium_badge = "⭐" if u.is_premium else ""
                    package_name = package_key if package_key else 'N/A'
                    user_list_text += (
                        f"{premium_badge} ID: {u.telegram_id}\n"
                        f"   Username: @{u.username or 'N/A'}\n"
                        f"   Package: {package_name}\n"
                        f"   Joined: {u.created_at.strftime('%Y-%m-%d')}\n\n"
                    )

            await update.message.reply_text(user_list_text)
        
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
        Broadcast message to all users (Unchanged)
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

    # --- YANGI ADMIN FUNKSIYALARI: TO'LOVLARNI BOSHQARISH ---

    @staticmethod
    @admin_only
    async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Confirm pending payment and activate premium
        Usage: /confirm_payment <payment_id>
        """
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        try:
            if not context.args or len(context.args) < 1:
                await update.message.reply_text("Usage: /confirm_payment <payment_id>")
                return
            
            payment_id = int(context.args[0])
            
            # Confirm payment and activate premium
            success, target_user_id = await db_manager.confirm_payment_and_activate_premium(
                payment_id, user.id
            )
            
            if success:
                await update.message.reply_text(f"✅ Payment {payment_id} confirmed. Premium activated for user {target_user_id}.")
                
                # Send confirmation to user
                if target_user_id:
                    user_language = await db_manager.get_user_language(target_user_id)
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=get_text(user_language, "premium_activated_user_msg")
                    )
            else:
                await update.message.reply_text(f"❌ Payment {payment_id} not found or already confirmed/failed.")
        
        except ValueError:
            await update.message.reply_text("❌ Invalid payment ID.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    @staticmethod
    @admin_only
    async def list_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all pending payments for manual review"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        payments = await db_manager.get_pending_payments()
        
        if not payments:
            await update.message.reply_text("✅ No pending payments found.")
            return

        payment_list_text = "💰 Kutilayotgan To'lovlar:\n\n"
        for p in payments:
            payment_list_text += (
                f"**ID**: `{p['id']}`\n"
                f"**User**: `{p['telegram_id']}`\n"
                f"**Paket**: {p['package_name']}\n"
                f"**Miqdor**: {p['amount']:,.0f} UZS\n"
                f"**Vaqt**: {p['created_at']}\n"
                f"**Tasdiqlash**: `/confirm_payment {p['id']}`\n\n"
            )
            
        await update.message.reply_text(payment_list_text, parse_mode='Markdown')

    # --- YANGI ADMIN FUNKSIYALARI: PROMO KODLAR ---
    
    @staticmethod
    @admin_only
    async def create_promo_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Create a promo code
        Usage: /create_promo <code> <discount%> [max_uses] [expiry_days]
        """
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(get_text(language, "create_promo_usage"))
                return
            
            code = args[0].upper()
            discount = int(args[1]) if args[1].isdigit() else None
            max_uses = int(args[2]) if len(args) > 2 and args[2].isdigit() else 0 # 0 = Unlimited
            expiry_days = int(args[3]) if len(args) > 3 and args[3].isdigit() else None
            
            expiry_date = datetime.utcnow() + timedelta(days=expiry_days) if expiry_days else None
            
            success = await db_manager.create_promo_code(
                code=code,
                discount=discount,
                max_uses=max_uses,
                expiry_date=expiry_date
            )
            
            if success:
                expiry_text = expiry_date.strftime("%Y-%m-%d") if expiry_date else "Cheksiz"
                await update.message.reply_text(
                    f"✅ Promo code **{code}** created successfully:\n"
                    f"Discount: {discount}%\n"
                    f"Max Uses: {max_uses if max_uses != 0 else 'Cheksiz'}\n"
                    f"Expires: {expiry_text}"
                , parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Error creating promo code. Code **{code}** may already exist.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    @staticmethod
    @admin_only
    async def list_promo_codes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all active and inactive promo codes"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        promos = await db_manager.list_promo_codes()
        
        if not promos:
            await update.message.reply_text("✅ No promo codes found.")
            return

        promo_list_text = "🏷️ Promo Codes:\n\n"
        for p in promos:
            status = "✅ Active" if p.is_active else "❌ Inactive"
            expiry = p.expiry_date.strftime("%Y-%m-%d") if p.expiry_date else "N/A"
            uses = f"{p.current_uses}/{p.max_uses if p.max_uses != 0 else '∞'}"
            
            promo_list_text += (
                f"**CODE**: `{p.code}` ({status})\n"
                f"**Discount**: {p.discount_percent}%\n"
                f"**Uses**: {uses}\n"
                f"**Expires**: {expiry}\n\n"
            )
            
        await update.message.reply_text(promo_list_text, parse_mode='Markdown')

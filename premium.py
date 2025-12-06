"""
Premium Service - Subscription management
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db_manager
from locales import get_text
from utils.keyboards import get_main_menu_keyboard, get_premium_packages_keyboard, get_back_keyboard, get_payment_keyboard
from datetime import datetime, timedelta
import config
import logging

logger = logging.getLogger(__name__)

# Conversation states for Premium flow
SELECTING_PACKAGE, ENTERING_PROMO, WAITING_FOR_PAYMENT = range(100, 103)

class PremiumService:
    """Premium subscription service and user flow"""
    
    @staticmethod
    async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show premium information and status"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        # 1. Get user status and current package
        user_obj = await db_manager.get_user(user.id)
        package_key = await db_manager.get_user_package_key(user.id)
        
        is_premium_active = await db_manager.is_user_premium(user.id)
        
        if is_premium_active:
            expiry = user_obj.premium_expiry.strftime("%Y-%m-%d %H:%M:%S") if user_obj.premium_expiry else "Cheksiz"
            current_package_name = config.PREMIUM_PACKAGES.get(package_key, {}).get(f"name_{language}", get_text(language, "free"))
            
            message = get_text(language, "premium_active", expiry=expiry, package_name=current_package_name)
        else:
            message = get_text(language, "premium_inactive")
        
        # 2. Get packages to display
        packages = await db_manager.get_all_packages()
        package_list_text = ""
        
        for pkg in packages:
            pkg_data = config.PREMIUM_PACKAGES.get(pkg.package_key)
            if not pkg_data:
                continue

            # Assuming price is stored correctly in config
            
            features_text = "\n".join([f"  • {f}" for f in pkg_data['features']])
            
            package_list_text += get_text(
                language, 
                "premium_package_info",
                name=getattr(pkg, f"name_{language}"),
                price=f"{pkg.price:,.0f} UZS" if pkg.price > 0 else get_text(language, "free"),
                duration_days=pkg.duration_days,
                features=features_text,
                package_key=pkg.package_key # Used for selection
            )
        
        full_message = get_text(language, "premium_start_main", current_status=message, package_list=package_list_text)
        
        # 3. Show package selection keyboard
        await update.message.reply_text(
            full_message,
            reply_markup=await get_premium_packages_keyboard(language),
            parse_mode='Markdown'
        )
        
        return SELECTING_PACKAGE # Start premium purchase flow
    
    @staticmethod
    async def select_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle package selection"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        # Extract package key from button text (Name | Price)
        package_input = update.message.text
        if '|' in package_input:
            # Find which package name matches the input
            selected_package_name = package_input.split(' | ')[0]
            package_key = next(
                (k for k, v in config.PREMIUM_PACKAGES.items() if v.get(f"name_{language}") == selected_package_name),
                None
            )
        else:
            package_key = package_input.lower()
        
        # Check for back button
        if package_input.lower() == get_text(language, "back").lower():
            await update.message.reply_text(
                get_text(language, "main_menu"),
                reply_markup=get_main_menu_keyboard(language)
            )
            return ConversationHandler.END

        # Get package details
        package_config = config.PREMIUM_PACKAGES.get(package_key)
        
        if not package_config:
            await update.message.reply_text(get_text(language, "invalid_package"))
            return SELECTING_PACKAGE

        # Free packages bypass payment
        if package_config['is_free']:
            await update.message.reply_text(
                get_text(language, "free_package_selected"),
                reply_markup=get_main_menu_keyboard(language)
            )
            return ConversationHandler.END

        # Store selected package
        context.user_data['selected_package_key'] = package_key
        context.user_data['original_price'] = package_config['price']
        
        # Ask for promo code (Optional step)
        await update.message.reply_text(
            get_text(language, "premium_ask_promo"),
            reply_markup=get_back_keyboard(language)
        )
        
        return ENTERING_PROMO
    
    @staticmethod
    async def enter_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle promo code entry or skip to payment"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        promo_input = update.message.text.strip().upper()
        
        package_key = context.user_data.get('selected_package_key')
        original_price = context.user_data.get('original_price')

        # Check for back button
        if promo_input.lower() == get_text(language, "back").lower():
            await PremiumService.show_info(update, context) # Go back to package selection
            return SELECTING_PACKAGE
        
        # Check if user wants to skip promo code (Check both hardcoded skip and localized button)
        skip_words = [get_text(language, "premium_skip_promo").upper()]
        
        if promo_input in skip_words or update.message.text.lower() == get_text(language, "premium_skip_promo").lower():
            final_price = original_price
            promo_used = False
        else:
            # Try to validate and apply promo code
            promo_code_obj = await db_manager.get_promo_code(promo_input)
            
            if promo_code_obj and promo_code_obj.discount_percent:
                discount_percent = promo_code_obj.discount_percent
                discount_amount = original_price * (discount_percent / 100)
                final_price = original_price - discount_amount
                context.user_data['promo_code'] = promo_input
                
                await update.message.reply_text(
                    get_text(language, "promo_applied", discount=discount_percent, final_price=f"{final_price:,.0f} UZS")
                )
                # Increment promo usage here before payment is confirmed? No, confirm_payment should handle it.
                promo_used = True
            else:
                final_price = original_price
                promo_used = False
                await update.message.reply_text(get_text(language, "promo_invalid_skip"))

        # Proceed to payment page
        context.user_data['final_price'] = final_price
        
        package_name = config.PREMIUM_PACKAGES[package_key][f'name_{language}']
        card_number = config.MANUAL_CARD_NUMBER
        
        # Create pending payment record
        payment = await db_manager.create_pending_payment(user.id, package_key, final_price)
        
        if not payment:
            await update.message.reply_text(get_text(language, "error"))
            return ConversationHandler.END
        
        context.user_data['pending_payment_id'] = payment.id
        
        payment_text = get_text(
            language,
            "payment_page",
            package_name=package_name,
            amount=f"{final_price:,.0f} UZS",
            card_number=card_number,
            payment_id=payment.id
        )
        
        # Replace reply keyboard with payment confirmation keyboard
        await update.message.reply_text(
            payment_text,
            reply_markup=get_payment_keyboard(language),
            parse_mode='Markdown'
        )
        
        return WAITING_FOR_PAYMENT

    @staticmethod
    async def payment_confirmation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """User sends message to confirm payment and notifies admin"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        # Check for back button
        if update.message.text.lower() == get_text(language, "back").lower():
             # Go back to promo entry stage
            await update.message.reply_text(
                get_text(language, "premium_ask_promo"),
                reply_markup=get_back_keyboard(language)
            )
            return ENTERING_PROMO


        # Only proceed if the button text matches the confirmation button
        if update.message.text != get_text(language, "payment_confirm_btn"):
             await update.message.reply_text(get_text(language, "invalid_input"))
             return WAITING_FOR_PAYMENT
             
        
        payment_id = context.user_data.get('pending_payment_id')
        final_price = context.user_data.get('final_price')
        package_key = context.user_data.get('selected_package_key')
        
        if not payment_id:
            await update.message.reply_text(get_text(language, "payment_id_missing"))
            return ConversationHandler.END
        
        # 1. Notify user
        await update.message.reply_text(
            get_text(language, "payment_confirmation_sent"),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        # 2. Notify admin for manual review
        admin_message = f"""
🚨 **Yangi To'lov So'rovi Kutishda** 🚨

**To'lov ID**: `{payment_id}`
**Foydalanuvchi**: {user.first_name} (@{user.username} | `{user.id}`)
**Paket**: {config.PREMIUM_PACKAGES[package_key][f'name_{language}']}
**Miqdor**: {final_price:,.0f} UZS
**Status**: Kutilmoqda

**Tasdiqlash uchun:** `/confirm_payment {payment_id}`
"""
        try:
            await context.bot.send_message(
                chat_id=config.PAYMENT_ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Admin notification failed: {e}")
            
        # Clear context data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    @staticmethod
    async def activate_premium(telegram_id: int, days: int = 30, package_key: str = 'pro'):
        """
        Activate premium subscription for a user (Called by admin or automated system)
        """
        package_config = config.PREMIUM_PACKAGES.get(package_key)
        
        if not package_config:
            # Fallback to Pro package config if key is unknown
            package_config = config.PREMIUM_PACKAGES['pro'] 
            
        async with db_manager.async_session() as session:
            from sqlalchemy import select
            from database.models import User, PremiumPackage
            
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            package_result = await session.execute(
                select(PremiumPackage).where(PremiumPackage.package_key == package_key)
            )
            package = package_result.scalar_one_or_none()

            if user and package:
                user.is_premium = True
                user.package_id = package.id
                
                # Calculate expiry date (Admin grant uses explicit 'days' parameter)
                user.premium_expiry = datetime.utcnow() + timedelta(days=days)
                
                # Reset/Update Limits for User
                await db_manager.reset_user_limits(session, user.id, package_key)
                
                await session.commit()
                return True
        
        return False
    
    @staticmethod
    async def deactivate_premium(telegram_id: int):
        """
        Deactivate premium subscription for a user
        """
        return await db_manager.deactivate_premium(telegram_id)

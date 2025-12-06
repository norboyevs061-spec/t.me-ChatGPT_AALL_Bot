"""
Uzbek language translations
"""

TRANSLATIONS = {
    # Welcome and General
    "welcome": "👋 Salom! Telegram AI Botga xush kelibsiz!\n\nTilni tanlang / Выберите язык:",
    "language_selected": "✅ Til tanlandi: O'zbek tili",
    "main_menu": "🏠 Asosiy menyu\n\nXizmatni tanlang:",
    "back": "⬅️ Orqaga",
    "cancel": "❌ Bekor qilish",
    "processing": "⏳ Qayta ishlanmoqda...",
    "error": "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
    "success": "✅ Muvaffaqiyatli!",
    "free": "BEPUL",
    
    # Services
    "service_chat": "💬 Chat",
    "service_translation": "🌐 Tarjima",
    "service_text_gen": "📝 Matn yaratish",
    "service_video": "🎬 Video yaratish",
    "service_image": "🎨 Rasm yaratish",
    "service_voice": "🎵 Ovoz va Musiqa",
    "service_premium": "⭐ Premium",
    
    # Chat Service (unchanged)
    "chat_start": "💬 Chat xizmati\n\nSavolingizni yozing:",
    "chat_response": "💬 Javob:\n\n{response}",
    
    # Translation Service (unchanged)
    "translation_start": "🌐 Tarjima xizmati\n\nTarjima qilish uchun matnni yuboring:",
    "translation_select_source": "Manba tilini tanlang:",
    "translation_select_target": "Maqsad tilini tanlang:",
    "translation_result": "🌐 Tarjima:\n\n{translation}",
    
    # Text Generation Service (unchanged)
    "textgen_start": "📝 Matn yaratish xizmati",
    "textgen_select_type": "Kontent turini tanlang:",
    "textgen_enter_topic": "Mavzuni kiriting:",
    "textgen_select_length": "Matn uzunligini tanlang:",
    "textgen_select_tone": "Matn ohangini tanlang:",
    "textgen_result": "📝 Yaratilgan matn:\n\n{text}",
    
    # Video Creation Service (unchanged)
    "video_start": "🎬 Video yaratish xizmati",
    "video_enter_description": "Video tavsifini kiriting:",
    "video_select_length": "Video uzunligini tanlang:",
    "video_select_style": "Video stilini tanlang:",
    "video_select_ratio": "Nisbatni tanlang:",
    "video_processing": "🎬 Video yaratilmoqda... Bu bir necha daqiqa davom etishi mumkin.",
    "video_result": "🎬 Videongiz tayyor!",
    
    # Image Generation Service (unchanged)
    "image_start": "🎨 Rasm yaratish xizmati",
    "image_enter_prompt": "Rasm tavsifini kiriting (prompt):",
    "image_select_size": "Rasm o'lchamini tanlang:",
    "image_select_style": "Rasm stilini tanlang:",
    "image_select_quantity": "Rasmlar sonini tanlang:",
    "image_processing": "🎨 Rasm yaratilmoqda...",
    "image_result": "🎨 Rasmingiz tayyor!",
    
    # Voice & Music Service (unchanged)
    "voice_start": "🎵 Ovoz va Musiqa xizmati",
    "voice_select_mode": "Rejimni tanlang:",
    "voice_mode_tts": "🗣 Matndan ovozga",
    "voice_mode_music": "🎵 Musiqa yaratish",
    "voice_enter_text": "Matnni kiriting:",
    "voice_select_style": "Ovoz stilini tanlang:",
    "voice_select_language": "Tilni tanlang:",
    "music_enter_prompt": "Musiqa tavsifini kiriting:",
    "music_select_style": "Musiqa stilini tanlang:",
    "voice_processing": "🎵 Yaratilmoqda...",
    "voice_result": "🎵 Audio tayyor!",
    
    # --- YANGI PREMIUM TEXTS ---
    "premium_start_main": "⭐ Premium Paketlar\n\n{current_status}\n\nQuyidagi paketlardan birini tanlang:\n\n{package_list}",
    "premium_package_info": "🌟 **{name}** ({price})\n\nAfzalliklari:\n{features}\n\nPaketni tanlash uchun ustiga bosing.",
    
    "premium_active": "✅ Sizda **{package_name}** obuna mavjud!\n\nAmal qilish muddati: {expiry}",
    "premium_inactive": "❌ Sizda pullik Premium obuna yo'q. Hozirda **Bepul** paketdagi cheklangan xizmatlardan foydalanmoqdasiz.",
    "free_package_selected": "Siz allaqachon bepul paketdasiz. Boshqa bepul paketga o'tish shart emas.",
    "invalid_package": "❌ Bunday paket mavjud emas.",
    
    "premium_ask_promo": "🏷️ Agar Promo kodingiz bo'lsa, uni kiriting. Agar yo'q bo'lsa, to'lov sahifasiga o'tish uchun **'O'TKAZISH'** tugmasini bosing.",
    "premium_skip_promo": "O'TKAZISH", # Text to skip promo code
    "promo_invalid_skip": "❌ Noto'g'ri promo kod. To'lov sahifasiga o'tilmoqda.",
    "promo_applied": "✅ Promo kod muvaffaqiyatli qo'llandi! **{discount}%** chegirma.\n\nYakuniy narx: **{final_price}**",
    
    # Payment Page
    "payment_page": "💳 To'lov sahifasi: **{package_name}**\n\n**Narxi**: {amount}\n**To'lov ID**: `{payment_id}`\n\nSotib olish uchun quyidagi kartaga pul o'tkazing va keyin **'TO'LOVNI TASDIQLASH'** tugmasini bosing.\n\n**Karta Raqami**: `{card_number}`",
    "payment_confirm_btn": "TO'LOVNI TASDIQLASH",
    "payment_confirmation_sent": "⏳ To'lov so'rovi administratorga yuborildi. Tez orada Premiumingiz faollashadi. E'tiboringiz uchun rahmat!",
    "premium_activated_user_msg": "🎉 Premium obunangiz faollashdi! Endi cheksiz imkoniyatlardan foydalanishingiz mumkin.",
    "payment_id_missing": "❌ To'lov ID topilmadi. Iltimos, boshidan urinib ko'ring.",

    # Rate Limiting
    "rate_limit_exceeded": "⚠️ Kunlik limitga yetdingiz! ({used}/{limit})\n\nCheksiz so'rovlar uchun Premium obunasiga o'ting!",
    "premium_required_feature": "⚠️ Bu xizmat faqat Premium foydalanuvchilar uchun mavjud. Iltimos, Premium paket sotib oling.",
    "requests_remaining": "📊 Qolgan so'rovlar: {remaining}/{limit}",
    
    # --- ADMIN PANEL TEXTS ---
    "admin_panel": "👨‍💼 Admin Panel",
    "admin_stats": "📊 Statistika:\n\n👥 Jami foydalanuvchilar: {total_users}\n✅ Faol foydalanuvchilar: {active_users}\n⭐ Premium foydalanuvchilar: {premium_users}\n\n**💰 Daromadlar**:\n• Jami daromad: {total_revenue}\n• Oylik daromad: {monthly_revenue}\n• Kutilayotgan to'lovlar: {pending_payments_count}\n\n📈 Xizmat foydalanish:\n{service_stats}",
    "admin_unauthorized": "❌ Sizda admin huquqlari yo'q.",
    "admin_stats_btn": "📊 Statistika",
    "admin_payments_btn": "💰 To'lovlar (Kutish)",
    "admin_promo_btn": "🏷️ Promo Kodlar",
    "admin_broadcast_btn": "📢 Xabar Tarqatish",
    "grant_premium_usage": "Foydalanish: /grant_premium <user_id> <days> [package_key]",
    "revoke_premium_usage": "Foydalanish: /revoke_premium <user_id>",
    "create_promo_usage": "Foydalanish: /create_promo <code> <discount%> [max_uses] [expiry_days]",
    
    # Errors (unchanged)
    "invalid_input": "❌ Noto'g'ri kiritish. Iltimos, qaytadan urinib ko'ring.",
    "service_unavailable": "❌ Xizmat hozirda mavjud emas. Keyinroq urinib ko'ring.",
    "api_error": "❌ API xatolik. Iltimos, keyinroq urinib ko'ring.",
}

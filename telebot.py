import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "Enter your bot token"
bot = telebot.TeleBot(API_TOKEN)

group_messages = {}
default_message = "_"
auto_reply_enabled = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == "private":
        markup = InlineKeyboardMarkup()
        button_add_bot = InlineKeyboardButton("➕ Click group .", url=f"https://t.me/{bot.get_me().username}?startgroup=true")
        button_contact_dev = InlineKeyboardButton("👤", url="https://t.me/rr8r9")
        markup.add(button_add_bot)
        markup.add(button_contact_dev)
        bot.send_message(message.chat.id, "👇🏻.", reply_markup=markup)

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            markup = InlineKeyboardMarkup()
            button_set_text = InlineKeyboardButton("تعيين كلمة محددة", callback_data="set_custom_text")
            button_stop = InlineKeyboardButton("إيقاف التفعيل التلقائي", callback_data="stop_group")
            markup.add(button_set_text)
            markup.add(button_stop)
            bot.send_message(message.chat.id, "- تم تفعيل البوت تلقائيًا .\n- لاتنسى يمكنك تحديد كلمة مخصصة من الأسفل .", reply_markup=markup)

            auto_reply_enabled[message.chat.id] = True
            group_messages.setdefault(message.chat.id, default_message)

@bot.callback_query_handler(func=lambda call: call.data == "set_custom_text")
def set_custom_text(call):
    user_id = call.from_user.id
    admins = bot.get_chat_administrators(call.message.chat.id)
    admin_ids = [admin.user.id for admin in admins]
    if user_id in admin_ids:
        msg = bot.send_message(call.message.chat.id, "أرسل الكلمة الآن .")
        bot.register_next_step_handler(msg, save_custom_text, call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "فقط مالك المجموعة أو أحد المشرفين يمكنه تعيين الكلمة .")

def save_custom_text(message, chat_id):
    group_messages[chat_id] = message.text
    auto_reply_enabled[chat_id] = True  
    bot.send_message(chat_id, "تم تعيين الكلمة بنجاح !")

@bot.callback_query_handler(func=lambda call: call.data == "stop_group")
def stop_group(call):
    user_id = call.from_user.id
    admins = bot.get_chat_administrators(call.message.chat.id)
    admin_ids = [admin.user.id for admin in admins]
    if user_id in admin_ids:
        auto_reply_enabled[call.message.chat.id] = False
        bot.answer_callback_query(call.id, "تم إيقاف التفعيل التلقائي .")
    else:
        bot.answer_callback_query(call.id, "فقط مالك المجموعة أو أحد المشرفين يمكنه إيقاف التفعيل التلقائي .")

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def auto_reply(message):
    if auto_reply_enabled.get(message.chat.id, False):
        if message.from_user.id != bot.get_me().id:
            bot.send_message(message.chat.id, group_messages.get(message.chat.id, default_message))

bot.infinity_polling()

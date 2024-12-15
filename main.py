import os
import telebot
from dotenv import load_dotenv
from telebot import types
from telebot.types import InputMediaPhoto

load_dotenv()

api = os.getenv("API_KEY")

bot = telebot.TeleBot(api)

print("Bot started")
user_states = {}

about_us_info = """
🎉 **Assalomu alaykum! Muslima Cakes Botimizga xush kelibsiz.** 🎊

👰‍♀️💍 **To'y**, 🎈 **Fotixa**, 🎂 **Tug'ilgan kun**, va boshqa **marosimlar** uchun 
eng yuqori sifatli **Tort, Pirojniy va Uy sharoitida tayyorlangan pechenelar**ga buyurtma qabul qilamiz! 🍰🍪✨

🍃 **Bizning mahsulotlarimiz:**
- **Halol va ishonchli masalliqlardan** tayyorlanadi. ✅
- Mazali va sifatli bo'lib, sizni va mehmonlaringizni xursand qiladi. 😋
- Har bir mahsulotimizda sevgi va mehr bor. 💕

💡 **Nima uchun bizni tanlash kerak?**
- Bayramlaringizni yanada **shirin va unutilmas** qilamiz! 🥳
- Shirinliklarimiz har doim **barkamol va yangidan tayyorlanadi.** 🏡✨

Sizning maxsus kunlaringiz bizning shirinliklarimiz bilan yanada zavqli bo'lsin! 🎂💕
"""

contacts_info = """
📞 **Bog'lanish uchun:**
- Telefon: +998 91 029 09 49 📱
- Bizning jamoamiz: [@shirinliklarrrri](https://t.me/shirinliklarrrri) 📸

Ushbu guruhda bizning shirinliklarimizning ko'proq suratlarini topishingiz mumkin! 🍰✨

"""


MENU_MAPPING = {
    "Biz Xaqimizda":"about_us",
    "Kantaktlar":"contacts",
    "Katalog":"catalogs",
}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_about_us = types.KeyboardButton("Biz Xaqimizda")
    btn_contacts = types.KeyboardButton("Kantaktlar")
    btn_catalogs = types.KeyboardButton("Katalog")
    markup.add(btn_about_us, btn_contacts, btn_catalogs)

    return markup


def catalog_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_birthday = types.KeyboardButton("Tug'ulgan kun uchun")
    btn_wedding = types.KeyboardButton("To'y uchun")
    btn_children = types.KeyboardButton("Farzand uchun")
    btn_back = types.KeyboardButton("Ortga")

    markup.add(btn_birthday,btn_wedding, btn_children)
    markup.add(btn_back)

    return markup


@bot.message_handler(commands=['start'])
def start(message):
    print(f"Current user: {message.chat.first_name}")

    user_states[message.chat.id] = "main_menu"
    bot.send_message(
        message.chat.id,
        f"Salom, {message.chat.first_name}, pastdagi tortlarni turini tanlag",
        reply_markup=main_menu()
    )


@bot.message_handler(content_types=['text'])
def on_click(message):
    chat_id = message.chat.id
    current_state = user_states.get(chat_id, "main_menu")

    if current_state == "main_menu":
        menu_name = MENU_MAPPING.get(message.text)
        if menu_name:
            if menu_name == "about_us":
                bot.send_message(chat_id, about_us_info)
            elif menu_name == "contacts":
                bot.send_message(chat_id, contacts_info)
            elif menu_name == "catalogs":
                user_states[chat_id] = "catalog_menu"
                bot.send_message(chat_id, "Tort katalogini tanlang: ", reply_markup=catalog_menu())
            else:
                user_states[chat_id] = "main_menu"
                bot.send_message(chat_id, "Iltimos, menyudan bittasini tanlang.")
        else:
            bot.reply_to(message, "Iltimos, menyudan bittasini tanlang.")

    elif current_state == "catalog_menu":
        if message.text == "Ortga":
            user_states[chat_id] = "main_menu"
            bot.send_message(chat_id, "Bosh menyuga qaytdingiz.", reply_markup=main_menu())
        elif message.text in ["Tug'ulgan kun uchun", "To'y uchun", "Farzand uchun"]:
            bot.reply_to(message, f"Yaxshi, xozir biz sizga {message.text} uchun katalogni ko'rsatamiz")
            group_name = {
                "Tug'ulgan kun uchun": "birthday",
                "To'y uchun": "wedding",
                "Farzand uchun": "children"
            }.get(message.text)

            all_photos = get_photo_groups(group_name)
            if not all_photos:
                bot.send_message(chat_id, f"{message.text} uchun rasmlar mavjud emas")
            else:
                send_photos_in_batches(chat_id, all_photos)
        else:
            user_states[chat_id] = "main_menu"
            bot.send_message(chat_id, "Iltimos, mentudan birini tanlang.", reply_markup=main_menu())




def get_photo_groups(group_name):
    folder_path = f'./photos/{group_name}'
    all_photos = []

    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        return None

    for photos in os.listdir(folder_path):
        current_image = open(f'{folder_path}/{photos}', 'rb')
        media_photo = InputMediaPhoto(current_image)
        all_photos.append(media_photo)

    return all_photos

def send_photos_in_batches(chat_id, photos):
    BATCH_SIZE = 10
    for i in range(0, len(photos), BATCH_SIZE):
        bot.send_media_group(chat_id, photos[i:i + BATCH_SIZE])



bot.infinity_polling()

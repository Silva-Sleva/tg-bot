import telebot
from datetime import datetime, timedelta
import threading
from telebot import types

# Ваш токен бота
API_TOKEN = '7839517122:AAH0zdxFuoGDOWswOzmqZr-_CUigO-FuVf8'
bot = telebot.TeleBot(API_TOKEN)

# Пользовательские данные для хранения
users_subscriptions = {}

# Номера и суммы для разных типов подписок
payment_details = {
    '3_months': {'number': '2200700770011574', 'amount': 349, 'photo': '3.jpg'},  # Укажите путь к изображению для 3 месяцев
    '6_months': {'number': '2200700770011574', 'amount': 590, 'photo': '6.jpg'},  # Укажите путь к изображению для 6 месяцев
    '12_months': {'number': '2200700770011574', 'amount': 890, 'photo': '12.jpg'},  # Укажите путь к изображению для 12 месяцев
    '24_months': {'number': '2200700770011574', 'amount': 1190, 'photo': '24.jpg'},  # Укажите путь к изображению для 24 месяцев
}


# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_3_months = types.KeyboardButton("на 3 месяца")
    btn_6_months = types.KeyboardButton("на 6 месяцев")
    btn_12_months = types.KeyboardButton("на 12 месяцев")
    btn_24_months = types.KeyboardButton("на 24 месяца")
    markup.add(btn_3_months, btn_6_months, btn_12_months, btn_24_months)
    first_name = message.from_user.first_name

    bot.send_message(message.chat.id, f"👋 Здравствуйте, {first_name}! Выберите тип подписки на Яндекс Плюс:", reply_markup=markup)
    bot.register_next_step_handler(message, choose_subscription)


# Функция для выбора подписки
def choose_subscription(message):
    subscription = message.text.strip().lower()

    # Привязываем ввод пользователя к правильным ключам словаря
    if subscription == "на 3 месяца":
        subscription_type = '3_months'
    elif subscription == "на 6 месяцев":
        subscription_type = '6_months'
    elif subscription == "на 12 месяцев":
        subscription_type = '12_months'
    elif subscription == "на 24 месяца":
        subscription_type = '24_months'
    else:
        bot.send_message(message.chat.id,
                         "Извините, я не понял ваш запрос. Пожалуйста, выберите: Подписка на 3 месяца, 6 месяцев, 12 месяцев или 24 месяца.")
        return

    # Сохраняем информацию о подписке
    users_subscriptions[message.chat.id] = {
        'subscription': subscription_type,
        'payment_link': f"https://t.me/stariysilva",  # Ссылка на аккаунт для оплаты
        'purchase_date': datetime.now()
    }

    # Получаем номер и сумму для выбранной подписки
    payment_info = payment_details[subscription_type]
    number = payment_info['number']
    amount = payment_info['amount']
    photo_path = payment_info['photo']  # Путь к фото .jpg

    # Убираем клавиатуру после выбора
    markup = types.ReplyKeyboardRemove()

    # Отправляем номер и сумму для оплаты с фото
    bot.send_message(message.chat.id,
                     f"🔴 Вы выбрали подписку {subscription}. Для оплаты переведите {amount} рублей по этим реквизитам {number}.",
                     reply_markup=markup)

    # Отправляем фото (путь к файлу .jpg)
    with open(photo_path, 'rb') as photo_file:
        bot.send_photo(message.chat.id, photo_file)

    bot.send_message(message.chat.id, "🔴 Пришлите скрин оплаты администратору(@Yandex_Family_Assistant) и после подтверждения оплаты, администратор пришлет вам ссылку на подписку. Инструкция по использованию в комментариях последнего поста в канале")

    # Настроим оповещения о конце подписки
    schedule_subscription_expiry(message.chat.id)

    # Предложим начать новый диалог
    bot.send_message(message.chat.id, "➡️ Для начала нового диалога, используйте команду /start.")


# Функция для уведомлений об окончании подписки
def schedule_subscription_expiry(user_id):
    if user_id not in users_subscriptions:
        return

    subscription_data = users_subscriptions[user_id]
    subscription_type = subscription_data['subscription']
    purchase_date = subscription_data['purchase_date']

    if subscription_type == '3_months':
        expiry_date = purchase_date + timedelta(days=90)
    elif subscription_type == '6_months':
        expiry_date = purchase_date + timedelta(days=180)
    elif subscription_type == '12_months':
        expiry_date = purchase_date + timedelta(days=365)
    elif subscription_type == '24_months':
        expiry_date = purchase_date + timedelta(days=730)

    # Вычисляем время до окончания подписки (за неделю)
    reminder_time = expiry_date - timedelta(days=7)

    # Уведомление за неделю до окончания подписки
    now = datetime.now()
    time_to_reminder = (reminder_time - now).total_seconds()

    if time_to_reminder > 0:
        threading.Timer(time_to_reminder, send_expiry_reminder, [user_id, expiry_date]).start()


# Функция для отправки напоминания об окончании подписки
def send_expiry_reminder(user_id, expiry_date):
    bot.send_message(user_id,
                     f"Внимание! Ваша подписка на Яндекс Плюс закончится через неделю ({expiry_date.strftime('%d-%m-%Y')}). Пожалуйста, продлите ее!")


# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)

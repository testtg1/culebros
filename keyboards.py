from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from models import *

from app import kassa

back_button = KeyboardButton('🔙Назад')

start_button1 = KeyboardButton('💎 Подписка')
start_button2 = KeyboardButton('🍬 Бонусная программа')
start_button3 = KeyboardButton('🆘 Тех.Поддержка')
start_button4 = KeyboardButton('📈 Статистика')
start_button5 = KeyboardButton('🤖 О боте ')
start_button6 = KeyboardButton('💡Совет')
start_button7 = KeyboardButton('⚡️ Актуальная ставка')
start_button8 = KeyboardButton('📱 Калькулятор банка')

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
start_keyboard.add(*[start_button1, start_button4, start_button2, start_button5, start_button3, start_button6])
start_keyboard.row(start_button8)

paymented_start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
paymented_start_keyboard.row(start_button7)
paymented_start_keyboard.add(
    *[start_button1, start_button4, start_button2, start_button5, start_button3, start_button6])
paymented_start_keyboard.row(start_button8)

sportstats_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

sportstats_button1 = KeyboardButton('🎾 Теннис')
sportstats_button2 = KeyboardButton('⚽️ Футбол')
sportstats_button3 = KeyboardButton('🏒 Хоккей')
sportstats_button4 = KeyboardButton('🏀 Баскетбол')
sportstats_keyboard.add(*[sportstats_button1, sportstats_button2, sportstats_button3, sportstats_button4])
sportstats_keyboard.row(back_button)

bonus_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
bonus_button1 = KeyboardButton('💰Баланс')
bonus_button2 = KeyboardButton('💸Вывод')
bonus_button3 = KeyboardButton('👥Рефералы')
bonus_button4 = KeyboardButton('📌Реф. ссылка')
bonus_keyboard.add(*[bonus_button1, bonus_button2, bonus_button3, bonus_button4])
bonus_keyboard.row(back_button)

change_risk_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
cr_first = KeyboardButton('ВЫСОКИЙ УРОВЕНЬ РИСКА И ДОХОДНОСТИ')
cr_second = KeyboardButton('СРЕДНИЙ УРОВЕНЬ РИСКА И ДОХОДНОСТИ')
cr_thirt = KeyboardButton('НИЗКИЙ УРОВЕНЬ РИСКА И ДОХОДНОСТИ')
change_risk_keyboard.add(*[cr_first, cr_second, cr_thirt])

admin_keyboard = InlineKeyboardMarkup(row_width=1)
admin_button1 = InlineKeyboardButton(text='Рассылка для купивших', callback_data='admin|messages')
admin_button2 = InlineKeyboardButton(text='Добавление статистики', callback_data='admin|sportstats')
admin_button3 = InlineKeyboardButton(text='Добавить срок подписки', callback_data='admin|subscribe')
admin_button4 = InlineKeyboardButton(text='Редактирование награды для рефералов', callback_data='admin|editref')
admin_button5 = InlineKeyboardButton(text='Рассылка для всех', callback_data='admin|msgforall')
admin_button6 = InlineKeyboardButton(text='Добавить подписку', callback_data='admin|addsubus')
admin_button7 = InlineKeyboardButton(text='Редактировать рассылку', callback_data='admin|editmsgs')
admin_button8 = InlineKeyboardButton(text='Убрать подписку', callback_data='admin|deleteuspro')

admin_keyboard.add(
    *[admin_button1, admin_button2, admin_button3, admin_button4, admin_button5, admin_button6, admin_button7])


def generate_sportstats_keyboard(category):
    stats = SportStats.query.filter_by(category=category).all()
    if stats:
        buttons = []
        keyboard = InlineKeyboardMarkup(row_width=3)
        for stat in stats:
            button = InlineKeyboardButton(text=stat.name, url=stat.link)
            buttons.append(button)

        keyboard.add(*buttons)
        return keyboard

    if not stats:
        return None


def generate_output_keyboard(id, amount):
    keyboard = InlineKeyboardMarkup(row_width=2)
    accept_button = InlineKeyboardButton(text='Вывод сделан', callback_data=f'admins|output|accept|{id}|{amount}')
    denied_button = InlineKeyboardButton(text='Отказать в выводе', callback_data=f'admins|output|denied|{id}')
    keyboard.add(*[accept_button, denied_button])
    return keyboard


def generate_subscribe_vars_keyboard():
    subscribes = Subscribes.query.all()
    print(subscribes)
    if subscribes:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []
        for sub in subscribes:
            button = KeyboardButton(sub.name)
            buttons.append(button)

        keyboard.add(*buttons)
        keyboard.row(back_button)
        return keyboard

    if not subscribes:
        return None


def generate_buy_keyboard(sid, user_id):
    sub = Subscribes.query.get(sid)
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text='Купить', url=kassa.generate_link(sub.price, user_id, f'us_tariff={sid}'))
    keyboard.add(button)
    return keyboard


def generate_editref_keyboard(subs):
    keyboard = InlineKeyboardMarkup()
    for sub in subs:
        button = InlineKeyboardButton(text=sub.name, callback_data=f'admin|editref|{sub.sid}')
        keyboard.row(button)

    return keyboard

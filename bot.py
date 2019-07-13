from time import sleep
from flask import request
from telebot import types

from app import *
from models import *

from texts import texts as messages
from keyboards import *

import time
import flask
import telebot

from sqlalchemy import desc

states = {}

back_states = {}


def get_state(id):
    return states.get(id)


def update_state(id, state):
    global states
    states[id] = state


def get_back_state(id):
    update_state(id, '')
    return back_states.get(id)


def update_back_state(id, state):
    global back_states
    back_states[id] = state


def admin(fn):
    def wrapped(m):
        if m.from_user.id in admins:
            return fn(m)

    return wrapped


def generate_bugdet(count, budget):
    stavki = []
    if count == 3:
        stavki.append((budget / 100) * 15.8)
        stavki.append((budget / 100) * 23.7)
        stavki.append((budget / 100) * 59.92)

    if count == 4:
        stavki.append((budget / 100) * 6.2)
        stavki.append((budget / 100) * 9.3)
        stavki.append((budget / 100) * 23.25)
        stavki.append((budget / 100) * 58.13)

    if count == 5:
        stavki.append((budget / 100) * 2.5)
        stavki.append((budget / 100) * 3.75)
        stavki.append((budget / 100) * 9.38)
        stavki.append((budget / 100) * 23.45)
        stavki.append((budget / 100) * 58.62)

    if count == 6:
        stavki.append((budget / 100) * 1)
        stavki.append((budget / 100) * 1.5)
        stavki.append((budget / 100) * 3.75)
        stavki.append((budget / 100) * 9.38)
        stavki.append((budget / 100) * 23.45)
        stavki.append((budget / 100) * 58.62)

    if count == 7:
        stavki.append((budget / 100) * 0.4)
        stavki.append((budget / 100) * 0.6)
        stavki.append((budget / 100) * 1.5)
        stavki.append((budget / 100) * 3.75)
        stavki.append((budget / 100) * 9.38)
        stavki.append((budget / 100) * 23.45)
        stavki.append((budget / 100) * 58.62)

    if count == 8:
        stavki.append((budget / 100) * 0.15)
        stavki.append((budget / 100) * 0.23)
        stavki.append((budget / 100) * 0.57)
        stavki.append((budget / 100) * 1.43)
        stavki.append((budget / 100) * 3.57)
        stavki.append((budget / 100) * 8.93)
        stavki.append((budget / 100) * 22.32)
        stavki.append((budget / 100) * 55.8)

    return stavki


def accept_payment(amount, user_id, tariff_id):
    subscribe = Subscribes.query.get(int(tariff_id))
    if subscribe:
        Payments.new(user_id, amount, int(time.time()), tariff_id)

        user = Users.query.get(int(user_id))

        referal_owner = Referals.get_owner(user.id)
        if referal_owner:
            referal_owner_user = Users.query.get(referal_owner.owner_id)
            if referal_owner_user:
                referal_owner_user.balance = referal_owner_user.balance + int(subscribe.to_ref_money)

        user_subscribe = Subscribers.query.get(user.id)
        if user_subscribe:
            if user_subscribe.date_to_payment >= time.time():
                user_subscribe.date_to_payment = user_subscribe.date_to_payment + subscribe.time
            else:
                user_subscribe.date_to_payment = int(time.time()) + subscribe.time

        if not user_subscribe:
            user_subscribe = Subscribers(id=user.id, payment_date=int(time.time()),
                                         date_to_payment=int(time.time()) + subscribe.time)

        session.add(user_subscribe)
        session.add(user)
        session.add(referal_owner)
        session.commit()

    if not subscribe:
        for adm in admins:
            bot.send_message(adm, 'Поступил неизвестный платеж: {amount}|{user_id}|{tariff_id}')


@app.route('/bot/<token_f>', methods=['POST'])
def hooking_webhooks(token_f):
    if bot.token == token_f:
        if request.headers.get('content-type') == 'application/json':
            return '', 200
        else:
            flask.abort(403)


@app.route('/payment')
def accept_payment_flask():
    amount = request.args.get('AMOUNT')
    user_id = request.args.get('MERCHANT_ORDER_ID')
    plane = request.args.get('us_tariff')
    accept_payment(amount, user_id, plane)
    return ''


@bot.message_handler(func=lambda msg: msg.text == '🔙Назад')
def back_function(msg):
    back_state = get_back_state(msg.from_user.id)
    if back_state:
        int_back_funcs[back_state](msg)

    if not back_state:
        start(msg)


@bot.message_handler(commands=['start'])
def start(msg):
    referal_args = msg.text.replace('/start', '').replace(' ', '')
    if referal_args != '':
        Referals.new(referal_args, msg.from_user.id)

    Users.new(msg.from_user.id)
    keyboardtosend = start_keyboard

    user_sub = Subscribers.query.get(msg.from_user.id)
    if user_sub:
        if user_sub.date_to_payment > time.time():
            keyboardtosend = paymented_start_keyboard
        else:
            keyboardtosend = start_keyboard
    if not user_sub:
        keyboardtosend = start_keyboard

    bot.send_message(
        msg.from_user.id,
        messages['start'].format(first_name=msg.from_user.first_name),
        reply_markup=keyboardtosend
    )


@bot.message_handler(commands=['admin'])
@admin
def admin_interface(msg):
    bot.send_message(msg.from_user.id, 'Выберите действие.', reply_markup=admin_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'admin|messages')
def send_messages_to_subs(call):
    bot.send_message(call.from_user.id, 'Отправьте тип спорта: хоккей, теннис, футбол, баскетболл')
    update_state(call.from_user.id, 'admin|messages|sport')


@bot.message_handler(func=lambda msg: get_state(msg.from_user.id) == 'admin|messages|sport')
def send_messages_to_subs_sport(msg):
    if msg.text.lower() in ['хоккей', 'теннис', 'футбол', 'баскетболл']:
        sport = ''
        if msg.text.lower() == 'хоккей':
            sport = 'hokkey'
        if msg.text.lower() == 'теннис':
            sport = 'tennis'
        if msg.text.lower() == 'футбол':
            sport = 'football'
        if msg.text.lower() == 'баскетболл':
            sport = 'basketboll'

        update_state(msg.from_user.id, f'admin|messages|text|{sport}')

        bot.send_message(msg.from_user.id, 'Отправьте текст для рассылки.')

    else:
        bot.send_message(msg.from_user.id, 'Отправьте еще раз, ошибка.')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|messages|text'))
def send_messages_to_subs_text(msg):
    adm, ms, t, sport = get_state(msg.from_user.id).split('|')

    all_subs = Subscribers.query.all()
    for sub in all_subs:
        if sub.date_to_payment > int(time.time()):
            try:
                bot.send_message(sub.id, msg.text)
            except:
                pass

    newsletter = NewsLetters(sport_category=sport, text=msg.text)
    session.add(newsletter)
    session.commit()
    bot.send_message(msg.from_user.id, 'Рассылка отправлена.')
    update_state(msg.from_user.id, '')


@bot.callback_query_handler(func=lambda call: call.data == 'admin|sportstats')
def add_sportstats(call):
    bot.send_message(call.from_user.id, 'Отправьте название спорта: хоккей, теннис, футбол, баскетболл')
    update_state(call.from_user.id, 'admin|sportstats|sport')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|sportstats|sport'))
def add_sportstats(msg):
    if msg.text.lower() in ['хоккей', 'теннис', 'футбол', 'баскетболл']:
        sport = ''
        if msg.text.lower() == 'хоккей':
            sport = 'hokkey'
        if msg.text.lower() == 'теннис':
            sport = 'tennis'
        if msg.text.lower() == 'футбол':
            sport = 'football'
        if msg.text.lower() == 'баскетболл':
            sport = 'basketboll'

        bot.send_message(msg.from_user.id, 'Отправьте название кнопки')
        update_state(msg.from_user.id, f'admin|sportstats|name|{sport}')

    else:
        bot.send_message(msg.from_user.id, 'Отправьте еще раз, ошибка.')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|sportstats|name'))
def add_sportstats_name(msg):
    adm, ss, n, sport = get_state(msg.from_user.id).split('|')
    bot.send_message(msg.from_user.id, 'Имя принято. Отправьте ссылку для статистики.')
    update_state(msg.from_user.id, f'admin|sportstats|link|{sport}|{msg.text}')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|sportstats|link'))
def add_sportstats_link(msg):
    ad, sp, li, sport, name = get_state(msg.from_user.id).split('|')
    link = msg.text

    sportstats = SportStats(category=sport, name=name, link=link)
    session.add(sportstats)
    session.commit()
    bot.send_message(msg.from_user.id, 'Добавлено.')
    update_state(msg.from_user.id, '')


@bot.callback_query_handler(func=lambda call: call.data == 'admin|subscribe')
def add_subscribes(call):
    bot.send_message(call.from_user.id, 'Отправьте имя для подписки')
    update_state(call.from_user.id, 'admin|subscribe|name')


@bot.message_handler(func=lambda msg: get_state(msg.from_user.id) == 'admin|subscribe|name')
def add_subscribes_name(msg):
    name = msg.text
    bot.send_message(msg.from_user.id, 'Отправьте цену подписки в рублях')
    update_state(msg.from_user.id, f'admin|subscribe|price|{name}')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|subscribe|price'))
def add_subscribes_price(msg):
    ad, sub, p, name = get_state(msg.from_user.id).split('|')
    price = msg.text
    bot.send_message(msg.from_user.id, 'Отправьте время подписки в секундах (1 сутки - 86400сек)')
    update_state(msg.from_user.id, f'admin|subscribe|time|{name}|{price}')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|subscribe|time'))
def add_subscribes_time(msg):
    ad, sub, p, name, price = get_state(msg.from_user.id).split('|')
    time = msg.text
    bot.send_message(msg.from_user.id, 'Отправьте фикс сумму в цифрах для владельцев рефералов, если они будут')
    update_state(msg.from_user.id, f'admin|subscribe|to_ref|{name}|{price}|{time}')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|subscribe|to_ref'))
def add_subscribes_toref(msg):
    ad, sub, p, name, price, time = get_state(msg.from_user.id).split('|')
    to_ref = msg.text

    subscribe = Subscribes(
        name=name,
        price=price,
        time=time,
        to_ref_money=to_ref
    )

    session.add(subscribe)
    session.commit()
    update_state(msg.from_user.id, '')

    bot.send_message(msg.from_user.id, 'Подписка добавлена.')


@bot.callback_query_handler(func=lambda call: call.data == 'admin|editref')
def admin_editref(call):
    subscribes = Subscribes.query.all()
    if subscribes:
        keyboard = generate_editref_keyboard(subscribes)
        bot.send_message(call.from_user.id,
                         'Выберите подписку, для которой хотите отредактировать награду для владельцев реферералов',
                         reply_markup=keyboard)

    if not subscribes:
        bot.send_message(call.from_user.id, 'Типов подписки нет.')


@bot.callback_query_handler(func=lambda call: call.data.startswith('admin|editref|'))
def admin_editref_sub(call):
    d, er, sid = call.data.split('|')
    sub = Subscribes.query.get(int(sid))
    if sub:
        bot.send_message(call.from_user.id, 'Отправьте фикс сумму в рублях')
        update_state(call.from_user.id, f'admin|editref|{sid}')

    if not sub:
        bot.send_message(call.from_user.id, 'Такой подписки нет.')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'admin|editref'))
def admin_editref_toref(msg):
    ad, er, sid = get_state(msg.from_user.id).split('|')
    sub = Subscribes.query.get(int(sid))
    sub.to_ref_money = int(msg.text)
    session.add(sub)

    session.commit()

    bot.send_message(msg.from_user.id, 'Награда отредактирована.')
    update_state(msg.from_user.id, '')


@bot.callback_query_handler(func=lambda call: call.data == 'admin|msgforall')
def msgs_for_all(msg):
    bot.send_message(msg.from_user.id, 'Отправьте текст сообщения для рассылки')
    update_state(msg.from_user.id, 'admin|mfa')


@bot.message_handler(func=lambda msg: get_state(msg.from_user.id) == 'admin|mfa')
def msgs_for_all_text(msg):
    users = Users.query.all()

    bot.send_message(msg.from_user.id, 'Рассылка запускается.')

    for user in users:
        try:
            bot.send_message(user.id, msg.text)
        except:
            pass

    bot.send_message(msg.from_user.id, 'Рассылка выполнена.')
    update_state(msg.from_user.id, '')


@bot.callback_query_handler(func=lambda call: call.data == 'admin|addsubus')
def admin_usbaausand(call):
    update_state(call.from_user.id, 'admin|usbusadd')
    bot.send_message(call.from_user.id, 'Пришлите ID человека.')


@bot.message_handler(func=lambda msg: get_state(msg.from_user.id) == 'admin|usbusadd')
def admin_adduspro2(msg):
    id = int(msg.text)
    update_state(msg.from_user.id, f'admin|usbusadd|{id}')
    subs = Subscribes.query.all()
    markup = InlineKeyboardMarkup()
    for i in subs:
        markup.row(InlineKeyboardButton(text=i.name, callback_data=f'admin|usbusadd|{i.sid}'))
    bot.send_message(msg.from_user.id, 'Выберите подписку.', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('admin|usbusadd|'))
def admin_addsubpro3(call):
    sid = call.data.split('|')[-1]
    uid = get_state(call.from_user.id).split('|')[-1]
    sub = Subscribes.query.get(int(sid))
    accept_payment(sub.price, int(uid), int(sid))
    bot.send_message(call.from_user.id, 'Выдано')
    update_state(call.from_user.id, '')


# @bot.callback_query_handler(func = lambda call: call.data == 'admin|editmsgs')
# def
#
# @bot.callback_query_handler(func = lambda call: call.data == 'admin|deleteuspro')


@bot.message_handler(func=lambda msg: msg.text == '⚡️ Актуальная ставка')
def actual_bet_function(msg):
    user_sub = Subscribers.query.get(msg.from_user.id)
    if user_sub:
        if user_sub.date_to_payment >= int(time.time()):
            bot.send_message(msg.from_user.id, 'Выберите вид спорта.', reply_markup=sportstats_keyboard)
            update_back_state(msg.from_user.id, 1)
            update_state(msg.from_user.id, 'actualbets')

        else:
            bot.send_message(msg.from_user.id, 'Ваша подписка истекла.')
    else:
        bot.send_message(msg.from_user.id, 'У вас нет подписки.')


@bot.message_handler(func=lambda msg: msg.text == '🎾 Теннис' and get_state(msg.from_user.id) == 'actualbets')
def actual_bets_tennis(msg):
    last_bet = NewsLetters.query.order_by(desc(NewsLetters.nlid)).filter_by(sport_category='tennis').limit(1).first()
    if last_bet:
        bot.send_message(msg.from_user.id, last_bet.text)

    if not last_bet:
        bot.send_message(msg.from_user.id, 'Последней ставки на данный вид спорта нет.')


@bot.message_handler(func=lambda msg: msg.text == '⚽️ Футбол' and get_state(msg.from_user.id) == 'actualbets')
def actual_bets_tennis(msg):
    last_bet = NewsLetters.query.order_by(desc(NewsLetters.nlid)).filter_by(sport_category='football').limit(1).first()
    if last_bet:
        bot.send_message(msg.from_user.id, last_bet.text)

    if not last_bet:
        bot.send_message(msg.from_user.id, 'Последней ставки на данный вид спорта нет.')


@bot.message_handler(func=lambda msg: msg.text == '🏒 Хоккей' and get_state(msg.from_user.id) == 'actualbets')
def actual_bets_tennis(msg):
    last_bet = NewsLetters.query.order_by(desc(NewsLetters.nlid)).filter_by(sport_category='hokkey').limit(1).first()
    if last_bet:
        bot.send_message(msg.from_user.id, last_bet.text)

    if not last_bet:
        bot.send_message(msg.from_user.id, 'Последней ставки на данный вид спорта нет.')


@bot.message_handler(func=lambda msg: msg.text == '🏀 Баскетбол' and get_state(msg.from_user.id) == 'actualbets')
def actual_bets_bb(msg):
    last_bet = NewsLetters.query.order_by(desc(NewsLetters.nlid)).filter_by(sport_category='basketboll').limit(1).first()
    if last_bet:
        bot.send_message(msg.from_user.id, last_bet.text)

    if not last_bet:
        bot.send_message(msg.from_user.id, 'Последней ставки на данный вид спорта нет.')


@bot.message_handler(func=lambda msg: msg.text == '💎 Подписка')
def subscribing_function(msg):
    keyboard = generate_subscribe_vars_keyboard()
    print(keyboard)
    if keyboard:
        bot.send_message(msg.from_user.id, '''💳Цены на подписку указаны в рублях. При оплате другой валютой, происходит конвертация по актуальному курсу. Если у вас возникли проблемы с оплатой пишите мне @alex_rico

Выберите тип подписки:''', reply_markup=keyboard)
        update_back_state(msg.from_user.id, 1)
        update_state(msg.from_user.id, 'subscribe')

    if not keyboard:
        bot.send_message(msg.from_user.id, 'В данный момент типов подписки нет.')


@bot.message_handler(func=lambda msg: get_state(msg.from_user.id) == 'subscribe')
def generate_url_for_buy_subscribe(msg):
    sub = Subscribes.query.filter_by(name=msg.text).first()
    if sub:
        bot.send_message(msg.from_user.id, msg.text, reply_markup=generate_buy_keyboard(sub.sid, msg.from_user.id))

    if not sub:
        bot.send_message(msg.from_user.id, 'Такого вида подписки не найдено.')


@bot.message_handler(func=lambda msg: msg.text == '🍬 Бонусная программа')
def bonusprogramm_function(msg):
    bot.send_message(msg.from_user.id, '''Благодаря нашей бонусной программе и своим друзьям, ты сможешь построить себе хороший пассивный доход за счет высокого процента повторных покупок (85% повторных покупок). Циклы постоянно заходят и пользователи продолжают активно двигаться с нами.👌

💰 Текущий процент дохода с приглашенных: 50%
⚡️ Твой статус: обычный резидент (если кол-во купивших подписку рефералов превышает цифру 10 - то ты получаешь статус VIP, мы повышаем твой процент на 60%!)
📤 Минимальная сумма вывода: 2000 руб.''', reply_markup=bonus_keyboard)
    update_back_state(msg.from_user.id, 1)


@bot.message_handler(func=lambda msg: msg.text == '💰Баланс')
def balance_function(msg):
    user = Users.get(msg.from_user.id)
    bot.send_message(msg.from_user.id, f'Ваш баланс: {user.balance} рублей.\nКоличество рефералов: {len(Referals.get_by_owner(msg.from_user.id))}')


@bot.message_handler(func=lambda msg: msg.text == '💸Вывод')
def outputmoney_function(msg):
    user = Users.get(msg.from_user.id)
    if user.balance >= 2000:
        bot.send_message(msg.from_user.id, 'Укажите сумму для вывода.')
        update_state(msg.from_user.id, 'balance|1|amount')

    if user.balance <= 2000:
        bot.send_message(msg.from_user.id, 'Минимальная сумма вывода: 2000 руб.')


@bot.message_handler(func=lambda msg: get_state(msg.from_user.id) == 'balance|1|amount')
def outputamount_function(msg):
    to_output = msg.text
    try:
        to_output = int(to_output)
        bot.send_message(msg.from_user.id, 'Отправьте реквизиты на которые хотите получить деньги.')
        update_state(msg.from_user.id, f'balance|2|amount|{to_output}')
    except Exception as e:
        print(e)
        bot.send_message(msg.from_user.id, 'Пришлите сумму для вывода цифрами.')


@bot.message_handler(
    func=lambda msg: type(get_state(msg.from_user.id)) == str and get_state(msg.from_user.id).startswith(
        'balance|2|amount|'))
def output_data_function(msg):
    bal, se, am, amount = get_state(msg.from_user.id)
    bot.send_message(msg.from_user.id, 'Заявка на вывод отправлена.')

    adm_notify_text = f'''Заявка на вывод

Пользователь: <a href="tg://user?id={msg.from_user.id}">{msg.from_user.first_name}</a>
Сумма вывода: {amount}
Реквизиты: {msg.text}'''

    for adm in admins:
        bot.send_message(adm, adm_notify_text, reply_markup=generate_output_keyboard(msg.from_user.id, amount))


@bot.message_handler(func=lambda msg: msg.text == '👥Рефералы')
def referalsee_function(msg):
    user = Users.get(msg.from_user.id)
    bot.send_message(msg.from_user.id, f'Количество рефералов: {len(Referals.get_by_owner(msg.from_user.id))}')


@bot.message_handler(func=lambda msg: msg.text == '📌Реф. ссылка')
def referallink_function(msg):
    username = bot.get_me().username
    link = f'Ваша реферальная ссылка: t.me/{username}?start={msg.from_user.id}'
    bot.send_message(msg.from_user.id, link)


@bot.message_handler(func=lambda msg: msg.text == '📈 Статистика')
def sportstats_function(msg):
    bot.send_message(msg.from_user.id, 'Выберите категорию.', reply_markup=sportstats_keyboard)
    update_back_state(msg.from_user.id, 1)


@bot.message_handler(func=lambda msg: msg.text == '🎾 Теннис')
def tennis_ss_func(msg):
    keyboard = generate_sportstats_keyboard('tennis')
    if keyboard:
        bot.send_message(msg.from_user.id, 'Выберите месяц.', reply_markup=keyboard)

    if not keyboard:
        bot.send_message(msg.from_user.id, 'По данному виду спорта статистика отсутствует.')


@bot.message_handler(func=lambda msg: msg.text == '⚽️ Футбол')
def football_ss_func(msg):
    keyboard = generate_sportstats_keyboard('football')
    if keyboard:
        bot.send_message(msg.from_user.id, 'Выберите месяц.', reply_markup=keyboard)

    if not keyboard:
        bot.send_message(msg.from_user.id, 'По данному виду спорта статистика отсутствует.')


@bot.message_handler(func=lambda msg: msg.text == '🏒 Хоккей')
def hokkey_ss_func(msg):
    keyboard = generate_sportstats_keyboard('hokkey')
    if keyboard:
        bot.send_message(msg.from_user.id, 'Выберите месяц.', reply_markup=keyboard)

    if not keyboard:
        bot.send_message(msg.from_user.id, 'По данному виду спорта статистика отсутствует.')


@bot.message_handler(func=lambda msg: msg.text == '🏀 Баскетбол')
def bb_ss_func(msg):
    keyboard = generate_sportstats_keyboard('basketboll')
    if keyboard:
        bot.send_message(msg.from_user.id, 'Выберите месяц.', reply_markup=keyboard)

    if not keyboard:
        bot.send_message(msg.from_user.id, 'По данному виду спорта статистика отсутствует.')


@bot.message_handler(func=lambda msg: msg.text == '🆘 Тех.Поддержка')
def support_function(msg):
    bot.send_message(msg.from_user.id, messages['tech_help'])


@bot.message_handler(func=lambda msg: msg.text == '🤖 О боте')
def about_function(msg):
    bot.send_message(msg.from_user.id, messages['about_bot'])


@bot.message_handler(func=lambda msg: msg.text == '💡Совет')
def advice_function(msg):
    bot.send_message(msg.from_user.id, messages['advice'], parse_mode='Markdown', disable_web_page_preview=True)


@bot.message_handler(func=lambda msg: msg.text == '📱 Калькулятор банка')
def calc_budget(msg):
    update_state(msg.from_user.id, 'calc|budget')
    bot.send_message(msg.from_user.id,
                     'Отправьте сумму вашего банка, к которому вы хотите рассчитать стратегию. Минимум 1000₽.')


@bot.message_handler(func=lambda msg: get_state(msg.from_user.id) == 'calc|budget')
def calc_bugdet_second(msg):
    try:
        budget = int(msg.text)
        if budget >= 1000:
            update_state(msg.from_user.id, f'calc|chooset|{budget}')
            bot.send_message(msg.from_user.id, '''*3-4 СТАВОК. ВЫСОКИЙ УРОВЕНЬ РИСКА И ДОХОДНОСТИ.*
Стратегия позволяет получать быстрый прирост банка, но риск очень большой. Доходность от 500%.

*5-6 СТАВОК. СРЕДНИЙ УРОВЕНЬ РИСКА И ДОХОДНОСТИ.*
Самая оптимальная стратегия. Риск в этом случае окупает свои вложения. Доходность от 200%.

*7-8 СТАВОК. НИЗКИЙ УРОВЕНЬ РИСКА И ДОХОДНОСТИ.*
Самая безопасная и низко доходная стратегия. Тише едешь - дальше будешь. Доходность от 100%.

Напишите нужное вам количество ставок''', parse_mode='Markdown')
        else:
            bot.send_message(msg.from_user.id, 'Минимум 1к.')
    except Exception as e:
        print(e)
        bot.send_message(msg.from_user.id, 'Отправьте ваш бюджет в цифрах.')


@bot.message_handler(
    func=lambda msg: get_state(msg.from_user.id) is not None and get_state(msg.from_user.id).startswith('calc|chooset'))
def calc_budget_calc(msg):
    try:
        count = int(msg.text)
        budget = get_state(msg.from_user.id).split('|')[-1]
        if count in range(3, 9):
            text = ''
            stavki = generate_bugdet(count, int(budget))
            for s in range(len(stavki)):
                text = text + f'{s + 1} ставка: {int(stavki[s])}руб.\n'

            bot.send_message(msg.from_user.id, text)
            bot.send_message(msg.from_user.id, 'Рассчитано.')
            update_state(msg.from_user.id, '')

        else:
            bot.send_message(msg.from_user.id, 'Возможное количество ставок - от 3 до 8. Отправьте в цифрах.')
    except Exception as e:
        print(e)
        bot.send_message(msg.from_user.id, 'Отправьте количество ставок в  цифрах.')


int_back_funcs = {
    1: start
}

bot.remove_webhook()
time.sleep(2)
bot.set_webhook(WEBHOOK_URL)

app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, debug=True)
'''while True:
    try:
        bot.polling()
    except Exception as e:
        bot.stop_polling()
        sleep(0.5)'''

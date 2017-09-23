import telebot
from config import api_token
from telebot import types
from msg_consts import *
import re

# TODO: хорошо бы тут всё закомментировать, а то я уже путаюсь
# TODO: нужно добавить обработчики телефона и локации


bot = telebot.TeleBot(api_token)


def main_keyboard(need_reg=False):
    """
    Данная функция возвращает клавиатуру главного меню
    :param need_reg: С кнопкой регистрации / редактирования данных
    :type need_reg: bool
    :return: ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(NEW_DONOR if need_reg else EDIT_DONOR,
                 FIND_DONOR)
    if not need_reg:
        add_geophone_keyboard(keyboard)
    return keyboard


def add_back_to_main_inline(keyboard=None):
    """
    Данная функция добавляет инлайн-кнопку "Назад в главное меню"
    в отправляемую клавиатуру сообщения и возвращает ее
    :param keyboard: передаваемая клавиатура
    :type keyboard: InlineKeyboardMarkup
    :param need_reg: в главное меню с кнопкой регистрации / без
    :type need_reg: bool
    :return: InlineKeyboardMarkup
    """
    if not keyboard:
        keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(TO_MAIN_MENU, callback_data=BACK_TO_MAIN)
    keyboard.add(back_btn)
    return keyboard


@bot.message_handler(commands=['start'])
@bot.callback_query_handler(func=lambda call: call.data == BACK_TO_MAIN)
def main_handler(msg_call):
    chat_id = msg_call.chat.id if isinstance(msg_call, types.Message) else msg_call.message.chat.id
    # TODO: Здесь должна быть проверка на зарегистрированность пользователя
    donor_exist = False
    keyboard = main_keyboard(not donor_exist)
    bot.send_message(chat_id, MAIN_MSG, reply_markup=keyboard)


# region: Обработчики сообщений по регистрации / изменению данных донора

def birth_bt_data_check(call):
    return bool(re.match(DATE_BT_DATA_REGEXP, call.data))


def birth_bt_rh_data_check(call):
    return bool(re.match(DATE_BT_RH_DATA_REGEXP, call.data))


def bt_data_change_check(call):
    return bool(re.match(BT_DATA_CHANGE_REGEXP, call.data))


def rh_data_change_check(call):
    return bool(re.match(RH_DATA_CHANGE_REGEXP, call.data))


def birth_changer(call):
    return bool(re.match(BIRTH_CHANGER_REGEXP, call.data))


def bt_changer(call):
    return bool(re.match(BT_CHANGER_REGEXP, call.data))


def rh_changer(call):
    return bool(re.match(RH_CHANGER_REGEXP, call.data))


def add_geophone_keyboard(keyboard=None, phone=True, geo=True):
    if not keyboard:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    if phone:
        phone_btn = types.KeyboardButton(SHARE_PHONE, request_contact=True)
        keyboard.add(phone_btn)
    if geo:
        geo_btn = types.KeyboardButton(SHARE_LOCATION, request_location=True)
        keyboard.add(geo_btn)
    return keyboard


@bot.message_handler(regexp=NEW_DONOR)
def start_reg_handler(msg: types.Message):
    bot.send_message(msg.chat.id, START_REG, reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(msg.chat.id, HOW_OLD, reply_markup=add_back_to_main_inline())


@bot.callback_query_handler(func=birth_changer)
def birth_changer_handler(call: types.CallbackQuery):
    bot.edit_message_text(HOW_OLD,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=add_back_to_main_inline())


@bot.message_handler(regexp=DATE_REGEXP)
def birth_handler(msg: types.Message):
    """Функция, обрабатывающая дату рождения пользователя"""
    import datetime
    raw_birth_date = msg.text
    try:
        raw_birth_date = raw_birth_date.replace('/', '.')
        birth_date = datetime.datetime.strptime(raw_birth_date, '%d.%m.%Y').date()
        age = (datetime.date.today() - birth_date).days / 365
        # До 18 лет нельзя быть донором
        # TODO: Здесь должна быть проверка на зарегистрированность пользователя
        user_exist = False
        if age < 18:
            bot.send_message(msg.chat.id, AGE_YOUNG, reply_markup=main_keyboard(True))
        if False:
            # TODO: Здесь должно быть обновление даты рождения пользователя
            user_id = msg.chat.id
            # TODO: Продумать изменение предыдущего сообщения с инлайн-кнопками!
            bot.send_message(user_id,
                             BIRTH_CHANGE_SUCCESS,
                             reply_markup=main_keyboard())
        else:
            blood_group_keyboard = types.InlineKeyboardMarkup()
            # Запишем возраст в inline-кнопку
            inline_data_tmpl = 'birth:{},bt:{}'.format(raw_birth_date, '{}')
            for bt, desc in BLOOD_TYPES.items():
                inline_data = inline_data_tmpl.format(bt)
                btn = types.InlineKeyboardButton(text=desc, callback_data=inline_data)
                blood_group_keyboard.add(btn)
            add_back_to_main_inline(blood_group_keyboard)
            bot.send_message(msg.chat.id, text=CHOOSE_BLOOD_TYPE, reply_markup=blood_group_keyboard)
    except ValueError:
        bot.send_message(msg.chat.id, text=BIRTH_DATE_ERROR, reply_markup=add_back_to_main_inline())


@bot.callback_query_handler(func=birth_bt_data_check)
def blood_type_handler(call: types.CallbackQuery):
    inline_data_tmpl = '{},rh:{}'.format(call.data, '{}')
    rh_keyboard = types.InlineKeyboardMarkup()
    for rht, desc in RH_TYPES.items():
        inline_data = inline_data_tmpl.format(rht)
        btn = types.InlineKeyboardButton(text=desc, callback_data=inline_data)
        rh_keyboard.add(btn)
    add_back_to_main_inline(rh_keyboard)
    bot.edit_message_text(CHOOSE_RH_TYPE,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=rh_keyboard)


@bot.callback_query_handler(func=birth_bt_rh_data_check)
def rh_factor_handler(call: types.CallbackQuery):
    # Разберём данные из кнопки
    birth_dt, blood_type, rh = call.data.split(',')
    birth_dt = birth_dt.split(':')[1]
    blood_type = int(blood_type.split(':')[1])
    rh = int(rh.split(':')[1])
    # TODO: Здесь должен создаваться новый пользователь
    bot.edit_message_text(SUCCESS_REG,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=None)
    bot.send_message(call.message.chat.id,
                     NEED_GEOPHONE,
                     reply_markup=main_keyboard())


@bot.message_handler(regexp=EDIT_DONOR)
def main_changer(msg: types.Message):
    change_list = types.InlineKeyboardMarkup()
    # TODO: Здесь имеет смысл сделать запрос в БД за данными пользователя
    # FIXME: Заглушка с данными
    # Префикс с_ обозначает current (текущие) данные
    user_raw_data = {'birth': 'dd.mm.yyyy',
                     'bt': 1,
                     'rh': 0}
    # Вместе с выводом пользовательских данных удалим клавиатуру главного меню
    bot.send_message(msg.chat.id,
                     USER_INFO_TMPL.format(birth_fmt=user_raw_data['birth'],
                                           bt_fmt=BLOOD_TYPES[user_raw_data['bt']],
                                           rh_fmt=RH_TYPES[user_raw_data['rh']]),
                     reply_markup=types.ReplyKeyboardRemove())
    for inline_id, desc in MAIN_CHANGER[1:]:
        btn = types.InlineKeyboardButton(text=desc, callback_data=inline_id)
        change_list.add(btn)
    add_back_to_main_inline(change_list)
    bot.send_message(msg.chat.id,
                     MAIN_CHANGER[0],
                     reply_markup=change_list)


@bot.callback_query_handler(func=bt_changer)
def bt_changer_handler(call: types.CallbackQuery):
    blood_group_keyboard = types.InlineKeyboardMarkup()
    # Шаблон для инлайн-данных
    inline_data_tmpl = 'bt:{}'
    # Сформируем инлайн-кнопки
    for bt, desc in BLOOD_TYPES.items():
        inline_data = inline_data_tmpl.format(bt)
        btn = types.InlineKeyboardButton(text=desc, callback_data=inline_data)
        blood_group_keyboard.add(btn)
    # Добавим кнопку возврата
    add_back_to_main_inline(blood_group_keyboard)
    bot.edit_message_text(CHOOSE_BLOOD_TYPE,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=blood_group_keyboard)


@bot.callback_query_handler(func=bt_data_change_check)
def blood_type_change_handler(call: types.CallbackQuery):
    user_id = call.message.chat.id
    blood_type = int(call.data.split(':')[1])
    # TODO: Здесь должна быть запись в БД измененной группы крови
    bot.send_message(user_id, BT_CHANGE_SUCCESS, reply_markup=main_keyboard())


@bot.callback_query_handler(func=rh_changer)
def rh_changer_handler(call):
    rh_keyboard = types.InlineKeyboardMarkup()
    # Шаблон для инлайн-данных
    inline_data_tmpl = 'rh:{}'
    # Сформируем инлайн-кнопки
    for rht, desc in RH_TYPES.items():
        inline_data = inline_data_tmpl.format(rht)
        btn = types.InlineKeyboardButton(text=desc, callback_data=inline_data)
        rh_keyboard.add(btn)
    add_back_to_main_inline(rh_keyboard)
    bot.edit_message_text(CHOOSE_RH_TYPE,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=rh_keyboard)


@bot.callback_query_handler(func=rh_data_change_check)
def rh_factor_change_handler(call: types.CallbackQuery):
    user_id = call.message.chat.id
    rh = int(call.data.split(':')[1])
    # TODO: Здесь должна быть запись в БД измененного резус-фактора
    bot.send_message(user_id, RH_CHANGE_SUCCESS, reply_markup=main_keyboard())


# endregion


bot.polling(none_stop=True)

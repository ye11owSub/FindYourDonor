# region: Добавление пути поиска модулей
import sys
from os.path import realpath, dirname, join
libs_path = join(dirname(realpath(__file__)), 'llibs')
sys.path.append(libs_path)
# endregion

from llibs import telebot
from llibs.telebot import types
from config import api_token
from msg_consts import *

from dbworker import Donor, Request

import re
import json

# TODO: хорошо бы тут всё закомментировать, а то я уже путаюсь
# TODO: стоит ли пересмотреть инлайн-данные: убрать префиксы birth, bt и rh, где ясна их позиция


bot = telebot.TeleBot(api_token, threaded=False)


def add_geophone_keyboard(keyboard=None, phone=False, geo=False):
    if not keyboard:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    if phone:
        phone_btn = types.KeyboardButton(SHARE_PHONE, request_contact=True)
        keyboard.add(phone_btn)
    if geo:
        geo_btn = types.KeyboardButton(SHARE_LOCATION, request_location=True)
        keyboard.add(geo_btn)
    return keyboard


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
    return keyboard


def add_back_to_main_inline(keyboard=None):
    """
    Данная функция добавляет инлайн-кнопку "Назад в главное меню"
    в отправляемую клавиатуру сообщения и возвращает ее
    :param keyboard: передаваемая клавиатура
    :type keyboard: InlineKeyboardMarkup
    :return: InlineKeyboardMarkup
    """
    if not keyboard:
        keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(TO_MAIN_MENU, callback_data=BACK_TO_MAIN)
    keyboard.add(back_btn)
    return keyboard


def reply_to_validation(msg: types.Message):
    if msg.reply_to_message and msg.reply_to_message.text:
        return msg.reply_to_message.text
    return None


@bot.message_handler(content_types=['location'])
def geo_change_handler(msg: types.Message):
    user_id = msg.chat.id
    # В зависимости от сообщения, к которому будет прикреплено местоположение
    # Будем считать, изменяется местоположения пользователя или заявки на поиск донора
    replied_to = reply_to_validation(msg)
    if replied_to == RQ_GEO_REPLY:
        bot.send_message(user_id,
                         RQ_PHONE_REQUIRE,
                         reply_markup=add_back_to_main_inline())
        Request.update_request({'longitude': msg.location.longitude,
                                'latitude': msg.location.latitude},
                               user_id)
        rq_phone_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        add_geophone_keyboard(rq_phone_keyboard, phone=True)
        skip_button = types.KeyboardButton(RQ_SKIP_PHONE)
        rq_phone_keyboard.add(skip_button)
        bot.send_message(user_id,
                         RQ_PHONE_ACTIONS,
                         reply_markup=rq_phone_keyboard)
    elif replied_to == REG_GEO_REPLY:
        bot.send_message(user_id,
                         SUCCESS_REG,
                         reply_markup=main_keyboard())
        Donor.update_with_data(user_id, {'longitude': msg.location.longitude,
                                         'latitude': msg.location.latitude})
    else:
        # Местоположение пользователя
        bot.send_message(user_id, GEO_USER_CHANGE_SUCCESS, reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(user_id, MAIN_MSG, reply_markup=main_keyboard())
        Donor.update_with_data(user_id, {'longitude': msg.location.longitude,
                                         'latitude': msg.location.latitude})


@bot.message_handler(commands=['start'])
@bot.callback_query_handler(func=lambda call: call.data == BACK_TO_MAIN)
def main_handler(msg_call):
    user_id = None
    if isinstance(msg_call, types.CallbackQuery):
        bot.edit_message_text(BACK_TO_MAIN_DECISION,
                              msg_call.message.chat.id,
                              msg_call.message.message_id)
        user_id = msg_call.message.chat.id
    else:
        user_id = msg_call.chat.id
    # chat_id совпадает с TelegramID
    donor_exist = Donor.try_exist(user_id)
    keyboard = main_keyboard(not donor_exist)
    bot.send_message(user_id, MAIN_MSG, reply_markup=keyboard)


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


def geo_changer(call):
    return bool(re.match(GEO_CHANGER_REGEXP, call.data))


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
        user_id = msg.chat.id
        donor_exist = Donor.try_exist(user_id)
        # До 18 лет нельзя быть донором
        if age < 18:
            bot.send_message(msg.chat.id, AGE_YOUNG, reply_markup=main_keyboard(True))
        if donor_exist:
            Donor.update_with_data(user_id, {'birth_date': birth_date})
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
    raw_birth_dt, raw_blood_type, raw_rh = call.data.split(',')
    birth_dt = raw_birth_dt.split(':')[1]
    blood_type = int(raw_blood_type.split(':')[1])
    rh_factor = int(raw_rh.split(':')[1])
    Donor.new_donor({'id': call.message.chat.id,
                     'birth_date': birth_dt,
                     'blood_type': blood_type,
                     # В БД резус хранится в виде  TRUE (+), FALSE (-) и NULL (Не знаю)
                     'rhesus': (False, True, None)[rh_factor]})
    bot.edit_message_text(REG_GEO_REQUIRE,
                          call.message.chat.id,
                          call.message.message_id,
                          parse_mode='Markdown',  # т.к в данном сообщении используется разметка, используем эту опцию
                          reply_markup=None)
    bot.send_message(call.message.chat.id,
                     REG_GEO_REPLY,
                     reply_markup=add_geophone_keyboard(geo=True))


@bot.message_handler(regexp=EDIT_DONOR)
def main_changer(msg: types.Message):
    change_list = types.InlineKeyboardMarkup()
    user_raw_data = Donor.get_donor_data(msg.chat.id)
    # Разберем сырые данные и выведем их в сообщении
    # Вместе с выводом пользовательских данных удалим клавиатуру главного меню
    bot.send_message(msg.chat.id,
                     USER_INFO_TMPL.format(birth_fmt=user_raw_data[3].strftime('%d.%m.%Y'),
                                           bt_fmt=BLOOD_TYPES[user_raw_data[1]],
                                           # В БД резус хранится в виде  TRUE (+), FALSE (-) и NULL (Не знаю)
                                           rh_fmt=RH_TYPES[{False: 0, True: 1, None: 2}[user_raw_data[2]]]),
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
    Donor.update_with_data(user_id, {'blood_type': blood_type})
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


@bot.callback_query_handler(func=geo_changer)
def geo_changer_handler(call):
    bot.edit_message_text(GEO_INFO,
                          call.message.chat.id,
                          call.message.message_id,
                          parse_mode='Markdown',  # т.к в данном сообщении используется разметка, используем эту опцию
                          reply_markup=add_back_to_main_inline())
    bot.send_message(call.message.chat.id,
                     GEO_CHANGE_REPLY,
                     reply_markup=add_geophone_keyboard(geo=True))


@bot.callback_query_handler(func=rh_data_change_check)
def rh_factor_change_handler(call: types.CallbackQuery):
    user_id = call.message.chat.id
    rh = int(call.data.split(':')[1])
    # В БД храним резус-фактор как TRUE (+), FALSE (-) и NULL (Не знаю)
    bot.send_message(user_id, RH_CHANGE_SUCCESS, reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(user_id, MAIN_MSG, reply_markup=main_keyboard())
    Donor.update_with_data(user_id, {'rhesus': (False, True, None)[rh]})


# endregion


# region: Обработчики сообщений по регистрации заявки на поиск доноров


def rq_init_check(call):
    return call.data == RQ_INIT


def rq_bt_check(call):
    return bool(re.match(RQ_BT_REGEXP, call.data))


def rq_bt_rh_check(call):
    return bool(re.match(RQ_BT_RH_REGEXP, call.data))


def rq_comment_check(msg: types.Message):
    return reply_to_validation(msg) == RQ_COMMENT_REPLY


def rq_phone_skip_check(msg: types.Message):
    return msg.text == RQ_SKIP_PHONE


def rq_applied(call: types.CallbackQuery):
    return call.data == RQ_APPLY


def rq_phone_try_again(user_id):
    bot.send_message(user_id,
                     RQ_PHONE_TRY_AGAIN,
                     reply_markup=add_back_to_main_inline())
    rq_phone_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    add_geophone_keyboard(rq_phone_keyboard, phone=True)
    skip_button = types.KeyboardButton(RQ_SKIP_PHONE)
    rq_phone_keyboard.add(skip_button)
    bot.send_message(user_id,
                     RQ_PHONE_ACTIONS,
                     reply_markup=rq_phone_keyboard)


@bot.message_handler(regexp=FIND_DONOR)
def start_request_handler(msg: types.Message):
    user_id = msg.chat.id
    bot.send_message(user_id, MAIN_REQUEST, reply_markup=types.ReplyKeyboardRemove())
    bop_keyboard = types.InlineKeyboardMarkup()
    proceed_btn = types.InlineKeyboardButton(REQUEST_PROCEED, callback_data=RQ_INIT)
    bop_keyboard.add(proceed_btn)
    add_back_to_main_inline(bop_keyboard)
    bot.send_message(user_id, BACK_OR_PROCEED, reply_markup=bop_keyboard)


@bot.callback_query_handler(func=rq_init_check)
def init_request_handler(call: types.CallbackQuery):
    # Шаблон для инлайн-данных
    inline_data_tmpl = 'rq!bt:{}'
    blood_group_keyboard = types.InlineKeyboardMarkup()
    for bt, desc in BLOOD_TYPES.items():
        inline_data = inline_data_tmpl.format(bt)
        btn = types.InlineKeyboardButton(text=desc, callback_data=inline_data)
        blood_group_keyboard.add(btn)
    add_back_to_main_inline(blood_group_keyboard)
    bot.edit_message_text(RQ_CHOOSE_BT,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=blood_group_keyboard)


@bot.callback_query_handler(func=rq_bt_check)
def bt_request_handler(call: types.CallbackQuery):
    # Шаблон для инлайн-данных
    inline_data_tmpl = '{},rh:{}'.format(call.data, '{}')
    rh_keyboard = types.InlineKeyboardMarkup()
    for rht, desc in RH_TYPES.items():
        inline_data = inline_data_tmpl.format(rht)
        btn = types.InlineKeyboardButton(text=desc, callback_data=inline_data)
        rh_keyboard.add(btn)
    add_back_to_main_inline(rh_keyboard)
    bot.edit_message_text(RQ_CHOOSE_RH,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=rh_keyboard)


@bot.callback_query_handler(func=rq_bt_rh_check)
def bt_rh_request_handler(call: types.CallbackQuery):
    # Распарсим инлайн-данные
    raw_bt, raw_rh = call.data.split('!')[1].split(',')
    blood_type = int(raw_bt.split(':')[1])
    rh_factor = int(raw_rh.split(':')[1])
    Request.upsert_request({'user_id': call.message.chat.id,
                            'need_blood_type': blood_type,
                            # В БД резус хранится в виде  TRUE (+), FALSE (-) и NULL (Не знаю)
                            'need_rhesus': (False, True, None)[rh_factor]})
    bot.edit_message_text(RQ_COMMENT_REQUIRE,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=add_back_to_main_inline(),
                          )
    bot.send_message(call.message.chat.id,
                     RQ_COMMENT_REPLY,
                     reply_markup=types.ForceReply())


@bot.message_handler(func=rq_comment_check)
def comment_request_handler(msg: types.Message):
    bot.send_message(msg.chat.id,
                     RQ_GEO_REQUIRE,
                     parse_mode='Markdown',  # т.к в данном сообщении используется разметка, используем эту опцию
                     reply_markup=add_back_to_main_inline())
    bot.send_message(msg.chat.id,
                     RQ_GEO_REPLY,
                     reply_markup=add_geophone_keyboard(geo=True))
    Request.update_request({'message': msg.text}, msg.chat.id)


@bot.message_handler(content_types=['contact'])
def phone_request_handler(msg: types.Message):
    user_id = msg.chat.id
    if msg.contact.user_id:
        if user_id != msg.contact.user_id:
            bot.send_message(user_id, RQ_PHONE_CHEATING, reply_markup=types.ReplyKeyboardRemove())
            rq_phone_try_again(user_id)
        else:
            bot.send_message(user_id, RQ_PHONE_SUCCESS, reply_markup=types.ReplyKeyboardRemove())
            Request.update_request({'phone_number': msg.contact.phone_number}, user_id)
            # Инлайн-клавиатура с кнопкой применения изменения
            # TODO: Возможно стоит сделать здесь предпросмотр заявки
            search_apply_keyboard = types.InlineKeyboardMarkup()
            rq_apply_button = types.InlineKeyboardButton(RQ_START_DONOR_SEARCH,
                                                         callback_data=RQ_APPLY)
            search_apply_keyboard.add(rq_apply_button)
            add_back_to_main_inline(search_apply_keyboard)
            bot.send_message(user_id, RQ_FINAL_STEP, reply_markup=search_apply_keyboard)

    else:
        bot.send_message(user_id, RQ_PHONE_NEED_TELEGRAM, reply_markup=types.ReplyKeyboardRemove())
        rq_phone_try_again(user_id)


@bot.message_handler(regexp=RQ_SKIP_PHONE)
def skip_phone_request_handler(msg: types.Message):
    user_id = msg.chat.id
    bot.send_message(user_id, RQ_PHONE_SKIPPED, reply_markup=types.ReplyKeyboardRemove())
    # Инлайн-клавиатура с кнопкой применения изменения
    # TODO: Возможно стоит сделать здесь предпросмотр заявки
    search_apply_keyboard = types.InlineKeyboardMarkup()
    rq_apply_button = types.InlineKeyboardButton(RQ_START_DONOR_SEARCH,
                                                 callback_data=RQ_APPLY)
    search_apply_keyboard.add(rq_apply_button)
    add_back_to_main_inline(search_apply_keyboard)
    bot.send_message(user_id, RQ_FINAL_STEP, reply_markup=search_apply_keyboard)


@bot.callback_query_handler(func=rq_applied)
def apply_request_handler(call: types.CallbackQuery):
    user_id = call.message.chat.id
    bot.edit_message_text(RQ_SEARCH_START,
                          user_id,
                          call.message.message_id,
                          reply_markup=None)
    Request.update_request({'registration_flag': True}, user_id)
    donor_exist = Donor.try_exist(user_id)
    bot.send_message(user_id,
                     MAIN_MSG,
                     reply_markup=main_keyboard(not donor_exist))
# endregion


def ep(content):
    print(type(content))
    bot.process_new_updates([telebot.types.Update.de_json(json.dumps(content))])

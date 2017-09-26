from collections import OrderedDict

# region: Сообщения, связанные с главной клавиатурой
NEW_DONOR = 'Готов стать донором'
EDIT_DONOR = 'Изменить мои данные'
FIND_DONOR = 'Найти донора'
# endregion

# region: Сообщения, связанные с регистрацией / изменением данных донора
START_REG = 'Спасибо, что Вы приняли смелое решение. Вы спасаете чью-то жизнь.'
HOW_OLD = 'Введите дату Вашего рождения в формате ДД/ММ/ГГГГ или ДД.ММ.ГГГГ:'
DATE_REGEXP = r'^\d{1,2}[/.]\d{1,2}[/.]\d{4}$'
AGE_YOUNG = 'К сожалению, Вы еще не достигли совершеннолетия. ' \
            'Тем не менее, Вы можете воспользоваться поиском донора.'
CHOOSE_BLOOD_TYPE = 'Выберите Вашу группу крови:'
BLOOD_TYPES = OrderedDict([(1, '0 (I)'),
                           (2, 'A (II)'),
                           (3, 'B (III)'),
                           (4, 'AB (VI)')])
DATE_BT_DATA_REGEXP = r'^birth:\d{1,2}\.\d{1,2}\.\d{4},bt:\d$'
CHOOSE_RH_TYPE = 'Выберите Ваш резус-фактор:'
RH_TYPES = OrderedDict([(0, 'Rh- (Отрицательный)'),
                        (1, 'Rh+ (Положительный)'),
                        (2, 'Не знаю')])
DATE_BT_RH_DATA_REGEXP = r'^birth:\d{1,2}\.\d{1,2}\.\d{4},bt:\d,rh:\d$'
SUCCESS_REG = 'Вы успешно зарегистрированы!'
NEED_GEOPHONE = 'Нам также полезно было бы знать Ваш номер телефона и обычное местоположение.\n' \
                'Если у Вас есть возможность, сообщите их нам.'

MAIN_CHANGER = ['Что вы хотите изменить?',
                ('birth', 'Дата рождения'),
                ('bt', 'Группа крови'),
                ('rh', 'Резус-фактор')]

USER_INFO_TMPL = 'Ваши текущие данные:\n' \
                 'Дата рождения: {birth_fmt}\n' \
                 'Группа крови: {bt_fmt}\n' \
                 'Резус-фактор: {rh_fmt}'

SHARE_PHONE = 'Поделиться номером телефона'
SHARE_LOCATION = 'Поделиться местоположением'

BIRTH_CHANGER_REGEXP = r'^birth$'
BT_CHANGER_REGEXP = r'^bt$'
RH_CHANGER_REGEXP = r'^rh$'

BIRTH_CHANGE_SUCCESS = 'Ваша дата рождения успешно обновлена.'
BT_DATA_CHANGE_REGEXP = r'^bt:\d$'
BT_CHANGE_SUCCESS = 'Ваша группа крови успешно обновлена.'
RH_DATA_CHANGE_REGEXP = r'^rh:\d$'
RH_CHANGE_SUCCESS = 'Ваш резус-фактор успешно обновлен.'
GEO_USER_CHANGE_SUCCESS = 'Спасибо, теперь мы сможем сообщать Вам только о релевантных поисках донора.'
PHONE_CHANGE_SUCCESS = 'Теперь мы сможем связаться с Вами.'
PHONE_CHANGE_CHEATING = 'Пожалуйста, отнеситесь к этому ответственно.\n' \
                        'Поделитесь тем номером телефона, который в действительности Вам принадлежит.'
PHONE_CHANGE_NEED_TELEGRAM = 'Пожалуйста, поделитесь тем номером телефона, к которому привязан ваш Telegram-аккаунт.'
# endregion

MAIN_MSG = 'Выберите интересующую Вас опцию:'
TO_MAIN_MENU = 'Назад в главное меню'
BACK_TO_MAIN = 'BACK'
BIRTH_DATE_ERROR = 'Кажется, ваша дата рождения имеет неверный формат. ' \
                   'Проверьте формат (ДД/ММ/ГГГГ или ДД.ММ.ГГГГ) и попробуйте еще раз:'

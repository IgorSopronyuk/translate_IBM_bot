import telebot
import config
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
from telebot import types
import pyowm

owm = pyowm.OWM('c8548689b28b1916f78403fb9c92e4f3', language='ru')

bot = telebot.TeleBot(config.TOKEN)

authenticator = IAMAuthenticator('9n-ZTrznhrAKV0YAJIWIM-fwico0pbNeHp9Wek67nt6V')
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticator
)
language_translator.set_service_url('https://api.eu-gb.language-translator.watson.cloud.ibm.com/instances'
                                    '/1bec2e12-6251-4b94-8d80-fcead8ec6d68')
languages = language_translator.list_languages().get_result()

user_dict = {}


# Формируем класс, для сохранения в него переменных (то что вводит кандидат)!
class User:
    def __init__(self, name):
        self.name = name
        self.application = None
        self.writer_lang = None
        self.phrases = None
        self.place = None


# Обработать / start и / help
@bot.message_handler(commands=['start', 'help'])
def command_start(message):
    chat_id = message.chat.id
    text = message.text
    msg = bot.send_message(chat_id,
                           "Здравствуйте, я полезный бот! Мое предназначение помогать в тех функциях которые в меня "
                           "встроенные! "
                           "В них входит перевод текста на необходимый Вам язык! Подскажите как я могу к Вам обращатся?")
    bot.register_next_step_handler(msg, process_name_step)


# Бот предлагает свои услуги\возможности!
@bot.message_handler(content_types=['text'])
def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    user = User(name)
    user_dict[chat_id] = user
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Переводчик', 'Погода', 'Список покупок')
    msg = bot.send_message(chat_id, 'Приятно познакомится ' + user.name + '! Выберите приложение, которым хотите '
                                                                          'воспользоваться!', reply_markup=markup)
    bot.register_next_step_handler(msg, how_can_i_help)


# Действие выполняется при выборе приложения!
@bot.message_handler(content_types=['text'])
def how_can_i_help(message):
    chat_id = message.chat.id
    application = message.text
    if application == '/start' or application == '/help':
        return command_start
    if application == u'Переводчик':
        user = user_dict[chat_id]
        user.application = application
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('английский', 'русский', 'испанский', 'немецкий', 'итальянский', 'французский', 'китайский',
                   'Погода')
        msg = bot.send_message(chat_id, "Укажите на каком языке будете писать (если такого языка нет в выпадающем "
                                        "списке, напишите этот язык в сообщении!): ", reply_markup=markup)
        bot.register_next_step_handler(msg, translater_func1)
    elif application == u'Погода':
        user = user_dict[chat_id]
        user.application = application
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Переводчик', 'Погода')
        msg = bot.send_message(chat_id, "Введите в каком городе/стране?: ", reply_markup=markup)
        bot.register_next_step_handler(msg, weather_bot)
    elif application == u'Список покупок':
        pass


# Тут запускается приложение для перевода текста!
@bot.message_handler(content_types=['text'])
def translater_func1(message):
    global lang1  # Создаем переменную lang1 (язык ввода текста)
    try:  # Создаем исключение для того чтобы различать кнопки и команду /start
        chat_id = message.chat.id
        writer_lang = message.text
        if writer_lang == u'Погода':  # Создаем условие нажатия на кнопку: если это погода выполняем код - ниже!
            user = user_dict[chat_id]
            user.writer_lang = writer_lang
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Переводчик')
            msg = bot.send_message(chat_id, "Введите в каком городе/стране?: ", reply_markup=markup)  # Спрашиваем в
            # каком городе проверить и при этом крепим кнопку переводчика!
            bot.register_next_step_handler(msg, weather_bot)
        # Дальше условия касаются выбора языка с помощью кнопок! Если выбрали одну из кнопок ниже :
        if writer_lang == u'английский':
            lang1 = 'en'
        elif writer_lang == u'русский':
            lang1 = 'ru'
        elif writer_lang == u'украинский':
            lang1 = 'uk'
        elif writer_lang == u'испанский':
            lang1 = 'es'
        elif writer_lang == u'немецкий':
            lang1 = 'de'
        elif writer_lang == u'итальянский':
            lang1 = 'it'
        elif writer_lang == u'французский':
            lang1 = 'fr'
        elif writer_lang == u'китайский':
            lang1 = 'zh'
        user = user_dict[chat_id]
        user.writer_lang = writer_lang
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('английский', 'русский', 'испанский', 'немецкий', 'итальянский', 'французский', 'китайский')
        # При этом спрашиваем на какой язык переводить и крепим кнопки с соответствующими языками
        msg = bot.send_message(chat_id, "На какой язык переводить (если такого языка нет в выпадающем "
                                        "списке, напишите этот язык в сообщении!): ", reply_markup=markup)
        bot.register_next_step_handler(msg, translater_func2)
    except:
        if writer_lang == '/start' or writer_lang == '/help': # Если написали команду старт, то возвращаемся в начало кода!
            msg = bot.send_message(chat_id,
                                   "Здравствуйте, я полезный бот! Мое предназначение помогать в тех функциях которые "
                                   "в меня "
                                   "встроенные! "
                                   "В них входит перевод текста на необходимый Вам язык! Подскажите как я могу к Вам "
                                   "обращатся?")
            bot.register_next_step_handler(msg, command_start)
        else:
            msg = bot.send_message(chat_id, "Oooops!")
            bot.register_next_step_handler(msg, translater_func1)


def translater_func2(message):
    global lang # Создаем глобальную переменную для языка на который будет осуществлятся перевод!
    try:
        chat_id = message.chat.id
        translation_lang = message.text
        if translation_lang == u'Погода': # Создаем условие нажатия на кнопку: если это погода выполняем код - ниже!
            user = user_dict[chat_id]
            user.translation_lang = translation_lang
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Переводчик')
            msg = bot.send_message(chat_id, "Введите в каком городе/стране?: ", reply_markup=markup)  # Спрашиваем в
            # каком городе проверить и при этом крепим кнопку переводчика!
            bot.register_next_step_handler(msg, weather_bot)
        # Условия для выбора языка на который будет перевод!
        if translation_lang == u'английский':
            lang = 'en'
        elif translation_lang == u'русский':
            lang = 'ru'
        elif translation_lang == u'украинский':
            lang = 'uk'
        elif translation_lang == u'испанский':
            lang = 'es'
        elif translation_lang == u'немецкий':
            lang = 'de'
        elif translation_lang == u'итальянский':
            lang = 'it'
        elif translation_lang == u'французский':
            lang = 'fr'
        elif translation_lang == u'китайский':
            lang = 'zh'
        user = user_dict[chat_id]
        user.translation_lang = translation_lang
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Смена языков для перевода', 'Смена языка для перевода', 'Погода')
        msg = bot.send_message(chat_id, "Введите фразу для перевода : ", reply_markup=markup) # После определения
        # языков просим ввести текст для перевода. А так же крепим кнопки!
        bot.register_next_step_handler(msg, translate_phrases)
    except:
        if translation_lang == '/start' or translation_lang == '/help':  # Если написали команду старт, то возвращаемся в начало кода!
            msg = bot.send_message(chat_id,
                                   "Здравствуйте, я полезный бот! Мое предназначение помогать в тех функциях которые "
                                   "в меня "
                                   "встроенные! "
                                   "В них входит перевод текста на необходимый Вам язык! Подскажите как я могу к Вам "
                                   "обращатся?")
            bot.register_next_step_handler(msg, command_start)
        else:
            msg = bot.send_message(chat_id, 'Oooops')
            bot.register_next_step_handler(msg, translater_func2)


def translate_phrases(message):
    #global translation

    chat_id = message.chat.id
    phrases = message.text
    # Устанавливаем цикл: если нажаты кнопки текст не переводится, а выполняется переход по приложениям или смена языков!
    while phrases == u'Погода' or phrases == u'Смена языков для перевода' or phrases == u'Смена языка для перевода':
        # Тут как раз условия которые работают если нажали на одну из кнопок!
        if phrases == u'Погода':
            user = user_dict[chat_id]
            user.phrases = phrases
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Переводчик')
            msg = bot.send_message(chat_id, "Введите в каком городе/стране?: ", reply_markup=markup)
            bot.register_next_step_handler(msg, weather_bot)
        elif phrases == u'Смена языков для перевода':
            user = user_dict[chat_id]
            user.phrases = phrases
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('английский', 'русский', 'испанский', 'немецкий', 'итальянский', 'французский', 'китайский',
                       'Погода')
            msg = bot.send_message(chat_id, "Укажите на каком языке будете писать (если такого языка нет в выпадающем "
                                            "списке, напишите этот язык в сообщении!): ", reply_markup=markup)
            bot.register_next_step_handler(msg, translater_func1)
        elif phrases == u'Смена языка для перевода':
            user = user_dict[chat_id]
            user.phrases = phrases
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('английский', 'русский', 'испанский', 'немецкий', 'итальянский', 'французский', 'китайский',
                       'Погода')
            msg = bot.send_message(chat_id, "На какой язык переводить (если такого языка нет в выпадающем "
                                            "списке, напишите этот язык в сообщении!): ", reply_markup=markup)
            bot.register_next_step_handler(msg, translater_func2)
        break
    else:
        translation = language_translator.translate(
            phrases,
            source=lang1, target=lang).get_result()
        msg = bot.send_message(chat_id, json.dumps(translation, indent=2, ensure_ascii=False))
        bot.register_next_step_handler(msg, translate_phrases)


# Здесь запускается приложение погода!
@bot.message_handler(content_types=['text'])
def weather_bot(message):
    global place
    try:
        chat_id = message.chat.id
        place = message.text
        user = user_dict[chat_id]
        user.place = place
        observation = owm.weather_at_place(place)
        w = observation.get_weather()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Переводчик')
        temp = w.get_temperature('celsius')["temp"]
        temp = round(temp)
        msg = bot.send_message(chat_id,
                               'В городе ' + place + ' сейчас ' + w.get_detailed_status() + ' Температура в этом '
                                                                                            'городе: ' + str(
                                   temp), reply_markup=markup)

        if temp < 10 and temp >= 0:
            msg = bot.send_message(chat_id, 'Сейчас пипец как холодно, одевайся как танк!')
        elif temp >= 10 and temp < 20:
            msg = bot.send_message(chat_id, 'Тепло конечно, но загорать еще рано!')
        elif temp >= 20 and temp < 25:
            msg = bot.send_message(chat_id, 'Ну еще чуть чуть и загорать можно идти!')
        elif temp > 25:
            msg = bot.send_message(chat_id, 'Можно смело загорать!')
        else:
            msg = bot.send_message(chat_id, 'Снеговики наступааааают!!!')

        bot.register_next_step_handler(msg, weather_bot)


    except:
        if place == u'Переводчик':
            user = user_dict[chat_id]
            user.place = place
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('английский', 'русский', 'испанский', 'немецкий', 'итальянский', 'французский', 'китайский',
                       'Погода')
            msg = bot.send_message(chat_id, 'Да, давайте переводить. Укажите на каком языке будете писать!', reply_markup=markup)
            bot.register_next_step_handler(msg, translater_func1)
        elif place == '/start' or place == '/help':
            msg = bot.send_message(chat_id,
                                   "Здравствуйте, я полезный бот! Мое предназначение помогать в тех функциях которые в меня "
                                   "встроенные! "
                                   "В них входит перевод текста на необходимый Вам язык! Подскажите как я могу к Вам обращатся?")
            bot.register_next_step_handler(msg, command_start)
        else:
            msg = bot.send_message(chat_id, 'Такого города нет... Уточните пожалуйста название!')
            bot.register_next_step_handler(msg, weather_bot)

            
bot.polling()
while True:
    pass

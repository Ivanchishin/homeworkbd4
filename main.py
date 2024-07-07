import random
import teletest
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = 'ВСТАВЬ ТОКЕН ОТ БОТА СЮДА'
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []

teletest.add_common_data()


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = str(message.chat.id)
    if cid not in known_users:
        teletest.add_user(cid)
        teletest.insert_common_data(cid)
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, """Привет 👋 Давай попрактикуемся в английском языке. 
Тренировки можешь проходить в удобном для себя темпе.
У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения. 
Для этого воспрользуйся инструментами:
добавить слово ➕,
удалить слово 🔙.
Ну что, начнём ⬇️""")

    markup = types.ReplyKeyboardMarkup(row_width=2)
    global buttons
    buttons = []
    other = []
    # Получаем доступный список слов
    telekeys = list(teletest.get_data().keys())
    # Выбираем из БД наугад слово для перевода
    target_word, translate = random.choice(list(teletest.get_data().items()))
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    # Выбриаем из БД наугад варианты ответа.
    telekeys.remove(target_word)
    for utr in range(3):
        word = random.choice(telekeys)
        other.append(word)
        telekeys.remove(word)
    others = other
    # Добавляем слова на панель
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


# Обработчик удаления слов
@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    ruswordtext = 'Введите русское слово, которое хотите удалить'
    bot.send_message(cid, ruswordtext)
    bot.register_next_step_handler(message, process_word_delete)


def process_word_delete(message):
    cid = str(message.chat.id)
    # Сохраняем русское слово
    rusname = message.text
    # Отправляем пользователю сообщение об успешном удалении
    if rusname is not None:
        teletest.delete_word(cid, rusname)
        bot.send_message(message.chat.id,
                         f"Слово '{rusname}' успешно удалено!")


# Обработчик добавления слов
@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    ruswordtext = 'Введите русское слово, которое хотите добавить'

    bot.send_message(cid, ruswordtext)
    bot.register_next_step_handler(message, process_russian_word_step)


def process_russian_word_step(message):
    # Сохраняем русское слово
    rusname = message.text
    # Отправляем запрос на английское слово
    bot.send_message(message.chat.id, "Введите английское слово, которое хотите добавить")
    bot.register_next_step_handler(message, process_english_word_step, rusname)


def process_english_word_step(message, rusname):
    # Сохраняем английское слово
    engname = message.text
    cid = str(message.chat.id)
    # Отправляем пользователю сообщение об успешном сохранении
    if rusname is not None and engname is not None and rusname != engname:
        teletest.add_word(cid, engname, rusname)
        bot.send_message(message.chat.id,
                         f"Слово '{rusname}' с переводом '{engname}' успешно добавлено в базу данных!")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)

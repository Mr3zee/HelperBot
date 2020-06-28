from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import FilmsBot.data as data
import FilmsBot.message as message

# todo fix it
keys_users = {}


def clear_keys_users():
    keys_users.clear()


def usernames_keyboard():
    keyboard = []
    row = []
    user_num = 0
    users = data.get_users()
    for user in users:
        if len(row) == 3:
            keyboard.append(row)
            row = []
        user_id = 'USER{}'.format(user_num)
        keys_users[user_id] = user
        row.append(InlineKeyboardButton(user, callback_data=user_id))
        user_num += 1
    if len(row) > 0:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


COMPLETE_BUTTON = 'complete_button'

keyboard_buttons = {
    COMPLETE_BUTTON: message.completed_text,
}

marked_buttons = set()

list_of_films = set()


def done_marked_buttons():
    marked_buttons.clear()


def tick_keyboard(user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[4:])
    for lnum in range(10):
        callback_data = 'tick' + str(lnum)
        button_text = (str(lnum) + (message.ticked_text if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(keyboard_buttons[COMPLETE_BUTTON], callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def untick_keyboard(user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[6:])
    for lnum in range(10):
        callback_data = 'untick' + str(lnum)
        button_text = (str(lnum) + (message.unticked_text if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(keyboard_buttons[COMPLETE_BUTTON], callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def remove_keyboard(user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[6:])
    for lnum in range(10):
        callback_data = 'remove' + str(lnum)
        button_text = (str(lnum) + (message.removed_text if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(keyboard_buttons[COMPLETE_BUTTON], callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)

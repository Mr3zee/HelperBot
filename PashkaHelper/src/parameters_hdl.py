from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, Filters, CommandHandler

from src.log import log_handler
from src.message import get_text
from src.buttons import *

from src import keyboard, database, common_functions as cf

# ConversationHandler's states:
MAIN_LVL, NAME_LVL, TIME_LVL, TZINFO_LVL = range(4)


@log_handler
def parameters(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    user_id = update.effective_user.id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('parameters_text', language_code) % database.get_user(user_id, language_code),
        reply_markup=keyboard.parameters_keyboard(language_code),
    )
    return MAIN_LVL


@log_handler
def __chg_parameters_page(update: Update, page_name, language_code, parameters_keyboard=None, ret_lvl=MAIN_LVL):
    user_id = update.effective_user.id
    try:
        update.callback_query.edit_message_text(
            text=get_text(f'{page_name}_parameters_text', language_code) % database.get_user(user_id,
                                                                                             language_code),
            reply_markup=(parameters_keyboard(language_code) if parameters_keyboard else None),
        )
    finally:
        return ret_lvl


def parameters_callback(update: Update, context: CallbackContext):
    data, language_code = cf.manage_callback_query(update)
    if data == EXIT_PARAMETERS:
        update.callback_query.edit_message_text(
            text=get_text('exit_parameters_text', language_code),
        )
        return ConversationHandler.END
    elif data in MAIN_SET:
        return __main_callback(update, context, data, language_code)
    elif data in COURSES_SET:
        return __chg_course(update, context, data, language_code)
    elif is_course_update(data):
        return __update_course(update, context, data, language_code)
    elif data in ATTENDANCE_SET:
        return __update_attendance(update, context, data, language_code)
    elif data in EVERYDAY_MESSAGE_SET:
        return __update_everyday_msg(update, context, data, language_code)


def __main_callback(update: Update, context: CallbackContext, data, language_code):
    if data == PARAMETERS_RETURN:
        return __return_callback(update, context, language_code)
    elif data == EVERYDAY_MESSAGE:
        return __mailing_callback(update, context, language_code)
    elif data == COURSES:
        return __chg_parameters_page(update, 'courses', language_code, keyboard.courses_keyboard)
    elif data == NAME:
        return __chg_parameters_page(update, 'name', language_code=language_code, ret_lvl=NAME_LVL)
    elif data == ATTENDANCE:
        return __chg_parameters_page(update, 'attendance', language_code, keyboard.attendance_keyboard)


@log_handler
def __return_callback(update: Update, context: CallbackContext, language_code):
    user_id = update.effective_user.id
    try:
        update.callback_query.edit_message_text(
            text=get_text('parameters_text', language_code) % database.get_user(user_id, language_code),
            reply_markup=keyboard.parameters_keyboard(language_code),
        )
    finally:
        return MAIN_LVL


@log_handler
def __mailing_callback(update: Update, context: CallbackContext, language_code):
    user_id = update.effective_user.id
    current_status = database.get_user_attr(user_id, 'mailing_status')
    update.callback_query.edit_message_text(
        text=get_text('mailing_parameters_text', language_code) % database.get_user(user_id, language_code),
        reply_markup=keyboard.mailing_keyboard(current_status, language_code),
    )
    return MAIN_LVL


def __get_button_vars(data):
    data = data[:-7]
    for a in range(len(data)):
        if data[a] == '_':
            return data[:a], data[a + 1:]


def __update_course(update: Update, context: CallbackContext, data, language_code):
    if data == ENG_NEXT:
        return __chg_parameters_page(update, 'eng', language_code, keyboard.eng2_keyboard)
    elif data == ENG_PREV:
        return __chg_parameters_page(update, 'eng', language_code, keyboard.eng1_keyboard)

    user_id = update.effective_user.id
    sub_name, subtype = __get_button_vars(data)
    database.set_user_attr(user_id, sub_name, subtype)
    return __chg_parameters_page(update, 'courses', language_code, keyboard.courses_keyboard)


def __chg_course(update: Update, context: CallbackContext, data, language_code):
    if data == OS_TYPE:
        return __chg_parameters_page(update, 'os', language_code, keyboard.os_keyboard)
    elif data == SP_TYPE:
        return __chg_parameters_page(update, 'sp', language_code, keyboard.sp_keyboard)
    elif data == HISTORY_GROUP:
        return __chg_parameters_page(update, 'history', language_code, keyboard.history_keyboard)
    elif data == ENG_GROUP:
        return __chg_parameters_page(update, 'eng', language_code, keyboard.eng1_keyboard)
    elif data == COURSES_RETURN:
        return __chg_parameters_page(update, 'courses', language_code, keyboard.courses_keyboard)


def __update_attendance(update: Update, context: CallbackContext, data, language_code):
    user_id = update.effective_user.id
    new_attendance, _blank = __get_button_vars(data)
    database.set_user_attr(user_id, 'attendance', new_attendance)
    return __return_callback(update, context, language_code)


@log_handler
def name_parameters(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    new_name = update.message.text
    database.set_user_attr(user_id, 'username', new_name)
    return parameters(update, context)


def __update_everyday_msg(update: Update, context: CallbackContext, data, language_code):
    user_id = update.effective_user.id
    if data == ALLOW_MESSAGE or data == FORBID_MESSAGE:
        if data == ALLOW_MESSAGE:
            cf.set_morning_message(context, update.effective_chat.id, user_id, language_code)
            new_status = 'allowed'
        else:
            cf.rm_morning_message(context)
            new_status = 'forbidden'
        database.set_user_attr(user_id, 'mailing_status', new_status)
        return __mailing_callback(update, context, language_code)
    elif data == TZINFO:
        return __chg_parameters_page(update, 'tzinfo', language_code=language_code, ret_lvl=TZINFO_LVL)
    elif data == MESSAGE_TIME:
        return __chg_parameters_page(update, 'time', language_code=language_code, ret_lvl=TIME_LVL)


# todo optimize
def __user_time_input_chg(update: Update, context: CallbackContext, validation, attr_name, error_lvl):
    language_code = update.effective_user.language_code
    new_info = update.message.text
    if validation(new_info):
        user_id = update.effective_user.id
        database.set_user_attr(user_id, attr_name, new_info)
        cf.rm_morning_message(context)
        cf.set_morning_message(context, update.effective_chat.id, user_id, language_code)
        current_status = database.get_user_attr(user_id, 'mailing_status')
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text('mailing_parameters_text', language_code) % database.get_user(user_id, language_code),
            reply_markup=keyboard.mailing_keyboard(current_status, language_code),
        )
        return MAIN_LVL
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('error_parameters_text', language_code),
    )
    return error_lvl


@log_handler
def tzinfo_parameters(update: Update, context: CallbackContext):
    return __user_time_input_chg(
        update=update,
        context=context,
        validation=database.valid_utcoffset,
        attr_name='utcoffset',
        error_lvl=TZINFO_LVL,
    )


@log_handler
def time_message_parameters(update: Update, context: CallbackContext):
    return __user_time_input_chg(
        update=update,
        context=context,
        validation=database.valid_time,
        attr_name='mailing_time',
        error_lvl=TIME_LVL,
    )


def parameters_error(name):
    @log_handler
    def error(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text(f'{name}_parameters_error_text', language_code),
        )
        return

    return MessageHandler(callback=error, filters=Filters.all)


@log_handler
def exit_parameters(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('exit_parameters_text', language_code),
    )
    return ConversationHandler.END


exit_parameters_hdl = CommandHandler(command='exit', callback=exit_parameters)

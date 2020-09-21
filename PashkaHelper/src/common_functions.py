from telegram.ext import CallbackContext, MessageHandler, CommandHandler
from telegram import Update

from src import keyboard, database
from src.timetable import get_timetable_by_index, get_subject_timetable
from src.time_management import get_weekday
from src.log import log_function
from src.message import get_text
from src.subject import subjects

from datetime import timedelta
import logging

MESSAGE, COMMAND = range(2)

logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)


def send_today_timetable(context: CallbackContext, user_id, chat_id, language_code,
                         disable_notification=False):
    attendance, utcoffset = database.get_user_attrs(user_id, ['attendance', 'utcoffset']).values()
    context.bot.send_message(
        chat_id=chat_id,
        text=get_timetable_by_index(
            day=get_weekday(timedelta(hours=utcoffset)),
            subject_names=database.get_user_subject_names(user_id),
            attendance=attendance,
            language_code=language_code,
        ),
        reply_markup=keyboard.timetable_keyboard(language_code=language_code),
        disable_notification=disable_notification,
    )


def send_morning_message(context: CallbackContext):
    job = context.job
    chat_id = job.context[0]
    user_id = job.context[1]
    language_code = job.context[2]
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('everyday_greeting_text', language_code),
        disable_notification=True,
    )
    send_today_timetable(
        context=context,
        chat_id=chat_id,
        user_id=user_id,
        language_code=language_code,
        disable_notification=True,
    )


def set_morning_message(context: CallbackContext, chat_id, user_id, language_code):
    job_name = 'job'
    if job_name not in context.chat_data:
        new_job = context.job_queue.run_daily(
            callback=send_morning_message,
            time=database.get_user_mailing_time_with_offset(user_id),
            days=(0, 1, 2, 3, 4, 5),
            context=[chat_id, user_id, language_code],
            name=job_name,
        )
        context.chat_data[job_name] = new_job
        return new_job


def rm_morning_message(context: CallbackContext):
    if 'job' in context.chat_data:
        old_job = context.chat_data['job']
        old_job.schedule_removal()
        del context.chat_data['job']


def simple_handler(hdl_name, hdl_type, filters=None, get_reply_markup=None, ret_lvl=None):
    @log_function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id

        context.bot.send_message(
            chat_id=chat_id,
            text=get_text(f'{hdl_name}_text', language_code),
            reply_markup=(get_reply_markup(language_code) if get_reply_markup else None),
        )
        return ret_lvl

    if hdl_type == COMMAND:
        ret_handler = CommandHandler(command=hdl_name, callback=inner)
    elif hdl_type == MESSAGE:
        ret_handler = MessageHandler(filters=filters, callback=inner)
    else:
        raise ValueError('Unsupported hdl type')
    return ret_handler


def get_subject_main_info(sub_name, user_id, language_code):
    header = get_text(f'{sub_name}_text', language_code)
    subtype = subjects[sub_name].get_subtype_full_name(database.get_user_attr(user_id, sub_name))
    main_info = '\n\n'.join([
        get_text(f'{name}_text', language_code)
        for name in (
            subjects[sub_name].get_subtypes_full_names() if not subtype else [subtype]
        )
    ])
    return header.format(main_info)


def subject_handler(sub_name):
    @log_function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        main_info = get_subject_main_info(sub_name, user_id, language_code)

        subtype, attendance = database.get_user_attrs(user_id, [sub_name, 'attendance']).values()

        additional_info = get_subject_timetable(sub_name, subtype, attendance, language_code)
        main_info = main_info % additional_info

        context.bot.send_message(
            chat_id=chat_id,
            text=main_info,
        )

    return CommandHandler(command=sub_name, callback=inner)


def manage_callback_query(update: Update):
    language_code = update.effective_user.language_code
    query = update.callback_query
    data = query.data
    query.answer()
    return data, language_code

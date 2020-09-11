from flask import Flask, request
from flask_sslify import SSLify

from telegram import ParseMode, Bot, Update
from telegram.ext import Dispatcher, Defaults

import config
import handler as hdl

import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
sslify = SSLify(app)


def connect_bot():
    logger.info('Connecting bot...')
    new_bot = Bot(
        token=config.BOT_TOKEN,
        defaults=Defaults(
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    )
    logger.info('Bot connected successfully')
    dp = Dispatcher(bot=new_bot, update_queue=None, workers=0, use_context=True)
    return dp, new_bot


def add_handlers(dispatcher: Dispatcher):
    for name, handler in hdl.handlers.items():
        logger.info('Adding ' + name + ' handler')
        dispatcher.add_handler(handler)
        logger.info('Handler added successfully')


def webhook(dispatcher: Dispatcher, update: Update):
    dispatcher.process_update(update)


def setup():
    logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

    dispatcher, bot = connect_bot()

    add_handlers(dispatcher)

    @app.route(f'/{config.BOT_TOKEN}', methods=['GET', 'POST'])
    def get_updates():
        if request.method == 'POST':
            update = Update.de_json(request.json, bot)
            webhook(dispatcher, update)
        return {'ok': True}

    logger.info('Staring bot...')

    app.run()


if __name__ == '__main__':
    setup()

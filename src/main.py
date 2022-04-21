import argparse
import logging
import os
from functools import partial
from typing import Any, Dict
from sys import stdout

import yaml
from telegram import Update
from telegram.ext import Updater, CommandHandler, ChatMemberHandler

from handlers.about import entrypoint as about_ep
from handlers.help import entrypoint as help_ep
from handlers.start import entrypoint as start_ep
from handlers.interview.new_members import entrypoint as new_members_ep


VERSION = (0, 1, 0)
VERSION_STR = '.'.join(str(_) for _ in VERSION)
DEFAULT_CFG = {
    'VERSION': VERSION,
    'VERSION_STR': VERSION_STR
}
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config.yml')
LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR
}


class ColorfulLevelFilter(logging.Filter):
    COLORED = {
        'DEBUG': '\033[1;34mDEBUG\033[0m',      # blue
        'INFO': '\033[1;32mINFO\033[0m',        # green
        'WARNING': '\033[1;33mWARNING\033[0m',  # yellow
        'ERROR': '\033[1;31mERROR\033[0m'       # red
    }

    def filter(self, record):
        record.coloredlevelname = ColorfulLevelFilter.COLORED[record.levelname]
        return True


def create_bot_updater(cfg: Dict[str, Any]) -> Updater:
    opts_wrapper = lambda f: partial(f, _cfg=cfg)

    updater = Updater(token=cfg['bot_token'], use_context=True)
    dispatcher = updater.dispatcher

    list(map(dispatcher.add_handler, [
        CommandHandler('about', opts_wrapper(about_ep)),
        CommandHandler('help', opts_wrapper(help_ep)),
        CommandHandler('start', opts_wrapper(start_ep)),
        ChatMemberHandler(new_members_ep, ChatMemberHandler.CHAT_MEMBER)
    ]))

    return updater


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', default=DEFAULT_CONFIG_PATH,
        help='the configuration file path (default: %s)' % DEFAULT_CONFIG_PATH
    )
    parser.add_argument(
        '-o', '--log-path', help='the log file path'
    )
    parser.add_argument(
        '-l', '--log-level', default='info',
        help=(
            'the logging level, which can be one of "debug", "info", '
            '"warning" and "error" (default: "info")'
        )
    )
    parser.add_argument(
        '-v', '--version', action='version',
        version=VERSION_STR
    )
    args = parser.parse_args()

    ft = ColorfulLevelFilter()
    console_fmt = logging.Formatter(
        '[%(asctime)s] %(coloredlevelname)-18s (%(name)s) %(message)s'
    )
    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(console_fmt)
    console_handler.addFilter(ft)
    logging_handlers = [console_handler]
    if args.log_path is not None:
        file_fmt = logging.Formatter(
            '[%(asctime)s] %(levelname)-7s (%(name)s) %(message)s'
        )
        file_handler = logging.FileHandler(args.log_path)
        file_handler.setFormatter(file_fmt)
        file_handler.addFilter(ft)
        logging_handlers.append(file_handler)
    logging.basicConfig(
        level=LEVELS[str.lower(args.log_level)],
        handlers=logging_handlers
    )

    with open(args.config, 'r', encoding='utf-8') as f:
        cfg: Dict | None = yaml.safe_load(f)
    if cfg is None:
        cfg = DEFAULT_CFG
    else:
        cfg.update(DEFAULT_CFG)
    logging.debug('Env: config: ' + args.config)
    logging.debug('Parsed configurations: ' + repr(cfg))

    updater = create_bot_updater(cfg)
    updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # execute after Ctrl+C / receiving signals
    updater.idle()


if __name__ == '__main__':
    main()
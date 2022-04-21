import argparse
import logging
import os
from functools import partial
from typing import Any, Dict

import yaml
from telegram.ext import Updater, CommandHandler

from handlers.about import entrypoint as about_ep
from handlers.help import entrypoint as help_ep
from handlers.start import entrypoint as start_ep


VERSION = (0, 1, 0)
VERSION_STR = '.'.join(str(_) for _ in VERSION)
DEFAULT_CFG = {
    'VERSION': VERSION,
    'VERSION_STR': VERSION_STR
}
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config.yml')


def create_bot_updater(cfg: Dict[str, Any]) -> Updater:
    opts_wrapper = lambda f: partial(f, _cfg=cfg)

    updater = Updater(token=cfg['bot_token'], use_context=True)
    dispatcher = updater.dispatcher

    list(map(dispatcher.add_handler, [
        CommandHandler('about', opts_wrapper(about_ep)),
        CommandHandler('help', opts_wrapper(help_ep)),
        CommandHandler('start', opts_wrapper(start_ep))
    ]))

    return updater


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', default=DEFAULT_CONFIG_PATH,
        help='specify a configuration file path'
    )
    parser.add_argument(
        '-v', '--version', action='version',
        version=VERSION_STR
    )
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        cfg: Dict | None = yaml.safe_load(f)
    if cfg is None:
        cfg = DEFAULT_CFG
    else:
        cfg.update(DEFAULT_CFG)
    logging.info('Env: config: ' + args.config)
    logging.info('Parsed configurations: ' + repr(cfg))

    updater = create_bot_updater(cfg)
    updater.start_polling()


if __name__ == '__main__':
    main()
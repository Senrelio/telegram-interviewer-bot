from functools import partial
from typing import Any, Dict

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler


TEXT = '''Telegram Interviewer Bot - v{ver}

Welcome!

Use <a href="/about">/about</a> command to show brief information of this bot.
Use <a href="/help">/help</a> command to list available commands.
Use <a href="/start">/start</a> command to show this message.'''


def entrypoint(
    update: Update, context: CallbackContext, _cfg: Dict[str, Any] = None
):
    _cfg = {} if _cfg is None else _cfg

    context.bot.send_message(
        # NOTE: MarkdownV2 has many shortcomings.
        chat_id=update.effective_chat.id, parse_mode='HTML',
        text=TEXT.format(ver=_cfg['VERSION_STR'])
    )


start_handler = lambda cfg: CommandHandler(
    'start',
    partial(entrypoint, _cfg=cfg)
)

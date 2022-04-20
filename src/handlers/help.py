from typing import Any, Dict
from telegram import Update
from telegram.ext import CallbackContext


TEXT = (
    'Telegram Interviewer Bot - Command List\n'
    '\n'
    '<a href="/about">/about</a>: show brief information of this bot\n'
    '<a href="/help">/help</a>: list available commands\n'
    '<a href="/start">/start</a>: show the starting message'
)


def entrypoint(
    update: Update, context: CallbackContext, _cfg: Dict[str, Any] = None
):
    _cfg = {} if _cfg is None else _cfg

    context.bot.send_message(
        chat_id=update.effective_chat.id, parse_mode='HTML',
        disable_web_page_preview=True,
        text=TEXT.format(ver=_cfg['VERSION_STR'])
    )

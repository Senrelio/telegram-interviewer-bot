from functools import partial
from typing import Any, Dict

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler


TEXT = (
    'Telegram Interviewer Bot\n'
    '\n'
    'Current Version: v{ver}\n'
    '\n'
    'This bot - just like its name "Interviewer" - is for group administrators '
    'to validate new people wanting to join a group by a virtual "interview". '
    'You can invite the bot to your managed groups and grant it administrative '
    'privileges. Then the bot will restrict new users unless they pass the '
    'interview.\n'
    'Of course, you can control how the interview like when configuring or '
    'even it\'s ongoing.\n'
    '\n'
    'See the project on <a href='
    '"https://github.com/nggiveyouup/telegram-interviewer-bot">GitHub</a> for '
    'further information.'
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

about_handler = lambda cfg: CommandHandler(
    'about',
    partial(entrypoint, _cfg=cfg)
)

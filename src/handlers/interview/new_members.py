from functools import partial
from typing import Any, Dict, Optional, Tuple

from telegram import (Chat, ChatMember, ChatMemberUpdated, ChatPermissions,
                      InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          ChatMemberHandler, CommandHandler,
                          ConversationHandler, Updater)


# callback queries
## answers
WRONG, CORRECT = range(2)
# states
ONGOING, END = range(2)


def extract_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:
    '''
    Takes a ChatMemberUpdated instance and extracts whether the
    'old_chat_member' was a member of the chat and whether the
    'new_chat_member' is a member of the chat. Returns None, if the status
    didn't change.
    '''

    # NOTE: If a user has been restricted, he/she will be ignored. So we must
    # use `is_member` field instead of `status`.
    old_status = chat_member_update.old_chat_member.status
    new_status = chat_member_update.new_chat_member.status
    old_is_member, new_is_member = chat_member_update.difference().get(
        'is_member', (None, None)
    )
    if old_status == new_status and old_status != ChatMember.RESTRICTED:
        return None
    
    was_member = (
        old_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR
        ]
        or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    )
    is_member = (
        new_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR
        ]
        or (new_status == ChatMember.RESTRICTED and new_is_member is True)
    )

    return was_member, is_member


def entrypoint(
    update: Update,
    context: CallbackContext,
    _cfg: Dict[str, Any] = None
) -> int:
    '''Restrict new members automatically.'''

    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    member_name = update.chat_member.new_chat_member.user.mention_html()
    user_id = update.chat_member.new_chat_member.user.id

    if not was_member and is_member:
        update.effective_chat.restrict_member(user_id, ChatPermissions())
        keyboard = [[InlineKeyboardButton(
            # enter the first question (starting with "0")
            'Start Interview', callback_data='0'
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.effective_chat.send_message(
            f'To {member_name}: please take part in an interview to remove '
            'restrictions on you.',
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        # specify a "state"
        return ONGOING


def first(
    update: Update,
    context: CallbackContext,
    _cfg: Dict[str, Any] = None
) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        query.message.text_html_urled + '\n\n<b>INTERVIEW STARTED</b>',
        parse_mode=ParseMode.HTML
    )
    user_id = update.effective_user.id
    # NOTE: You MUST set all fields True, or the user will still be restricted
    update.effective_chat.restrict_member(
        user_id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_send_polls=True
        )
    )
    return END


new_members_handler = lambda cfg: ConversationHandler(
    [ChatMemberHandler(
        partial(entrypoint, _cfg=cfg),
        ChatMemberHandler.CHAT_MEMBER
    )],
    {
        ONGOING: [
            CallbackQueryHandler(partial(first, _cfg=cfg), pattern='^0$')
        ],
        END: []
    },
    []
)

# PTB v22 Buttons, Copy Buttons, Effects & Single-Menu UX

Learned building a temp-mail bot with `python-telegram-bot==22.7` (Windows host,
Python 3.14). Complements the aiogram-centric main skill.

## Colored inline buttons (Bot API 9.4+)

`InlineKeyboardButton` accepts plain strings — do NOT import a style enum
(`telegram.constants.InlineKeyboardButtonStyle` does not exist in PTB 22.7):

```python
from telegram import InlineKeyboardButton as Btn
Btn("📥 صندوق", callback_data="m:inbox", style="primary")   # dark blue
Btn("✅ تایید", callback_data="ok", style="success")        # green
Btn("🗑 حذف", callback_data="del", style="danger")          # red
```

Old clients silently ignore `style` — safe to ship unconditionally.

## Copy-text buttons (no typing for the user)

```python
from telegram import CopyTextButton, InlineKeyboardButton as Btn
Btn("📋 کپی کد: 48210", copy_text=CopyTextButton(text="48210"))
```

Use for emails, OTP codes, card numbers, whole fake identities. One tap copies.

## Message effects (`message_effect_id`)

`Bot.send_message(..., message_effect_id="...")` plays a full-screen animation.
Free effects that work without Premium (verified IDs):

- 🔥 fire `5104841245755180586` — main menu / welcome
- 🎉 party `5046509860389126442` — success (email created, new mail arrived)
- ❤️ heart `5159385139981059251`
- 👍 like `5107584321108051014` — gate passed

Telegram can reject an effect (removed ID, client quirk) with BadRequest, so
always wrap sends:

```python
async def _send(bot, chat_id, text, markup=None, effect=None):
    kwargs = dict(parse_mode="HTML")
    if markup is not None:
        kwargs["reply_markup"] = markup
    if effect:
        try:
            return await bot.send_message(chat_id, text,
                                          message_effect_id=effect, **kwargs)
        except BadRequest:
            pass
    return await bot.send_message(chat_id, text, **kwargs)
```

## Single living menu (edit, don't spam)

- Keep one menu message per user: `menu_msg(user_id, message_id)` table.
- `render()` tries `edit_message_text` on the stored ID; on BadRequest
  (deleted / text identical) falls back to `send_message` + store new ID.
- Never pass `kb([])` as reply_markup to clear buttons — PTB sends an empty
  keyboard which Telegram rejects. Use `reply_markup=None` instead.
- `/start` handler deletes the user's command message; any junk plain text is
  deleted quietly (`on_text` → `message.delete()`), no scolding replies.
- Slash-command-free UX: `set_my_commands([])` in `post_init`, everything is
  inline buttons. Plain-text input is only honored when admin state
  (`ctx.user_data["awaiting"]`) expects it.

## Force-join gate (up to 30 channels)

- `channels(chat_id, title, link)` table; admin adds by `@username`/link.
- Verify each with `get_chat` + `get_chat_member`; require the bot to be
  **admin** in the channel or the check raises.
- `missing_channels()` returns channels where status is `left`/`kicked` or
  check raises Forbidden. Fail-open with a logged warning on other
  BadRequests (chat gone, bot removed) so one dead channel can't lock all users.
- Blocked users see `show_join()` (URL buttons + "✅ عضو شدم" re-check)
  instead of the menu, on EVERY callback — not just /start.
- Invite link: prefer `https://t.me/{username}`; fall back to
  `export_chat_invite_link`, then to the raw text the admin sent.

## Error handler must be async

`app.add_error_handler` AWAITS the callback. A sync `lambda` returns None →
`TypeError: 'NoneType' object can't be awaited`, masking the real exception.
Always use a coroutine:

```python
async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.warning("update error: %s", context.error)
```

Real incident: this exact TypeError hid an `OperationalError` for minutes
because the error-handler crash replaced the original traceback.

## Identical edits raise 400

`edit_message_text` with unchanged text/markup raises
`BadRequest: Message is not modified`. In `render()`/`_edit` wrappers, catch
it and return silently — users re-tapping the same button must be a no-op,
not an error.

## Premium animated emojis (`<tg-emoji>`)

Numeric custom-emoji IDs in HTML parse mode, plain-text fallback inside the
tag for clients that can't render them (all verified live against Bot API):

```python
EMOJI = {
    "spark": "5222108309795908493",   # ✨
    "lock": "4927431131898315396",    # 🔒
    "mask": "5359441070201513074",    # 🎭
    "key": "5372878055775683161",     # 🔑
    "mail": "5368324170671202286",    # ✉️
}
def E(name, fallback):
    return f'<tg-emoji emoji-id="{EMOJI[name]}">{fallback}</tg-emoji>'
```

If Telegram rejects an ID, the send raises BadRequest containing
"emoji"/"entity"/"can't parse" — retry with tags stripped
(`re.sub(r"</?tg-emoji[^>]*>", "", text)`), keeping fallback text, so the
message never fails to deliver. Harvest more IDs: owner sends any premium
emoji to the bot, read `message.entities[].custom_emoji_id`, append.
Verify a candidate by sending it to the owner and deleting immediately.

## Chat-folder UX deep link

`Btn("📁 پوشه‌ها", url="tg://settings/folders")` opens the client's folder
settings in one tap — users park the bot in a dedicated folder with no
instructions. In topic-enabled supergroups, thread replies through
`message_thread_id` so answers land in the right topic.

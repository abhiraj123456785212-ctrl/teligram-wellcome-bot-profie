import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
START_IMAGE = os.getenv("START_IMAGE")


def register_start(app: Client):

    @app.on_message(filters.command("start"))
    async def start_command(client: Client, message: Message):

        user = message.from_user
        name = user.first_name if user else "User"

        caption = f"""
Hey {name},

This is Aera music !

A music player bot with some awesome and useful features.

Click on the help button for more info.
"""

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Add me to your group",
                        url=f"https://t.me/{client.me.username}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Help",
                        callback_data="help_menu"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Support",
                        url=f"https://t.me/{SUPPORT_USERNAME}"
                    ),
                    InlineKeyboardButton(
                        "Channel",
                        url=CHANNEL_LINK
                    )
                ]
            ]
        )

        # 🔥 SEND WITHOUT REPLY
        if START_IMAGE:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=START_IMAGE,
                caption=caption,
                reply_markup=buttons
            )
        else:
            await client.send_message(
                chat_id=message.chat.id,
                text=caption,
                reply_markup=buttons
            )

    # Help button callback
    @app.on_callback_query(filters.regex("help_menu"))
    async def help_callback(client, callback_query):

        await callback_query.message.edit_caption(
            caption="""
Here is help section.

More features coming soon.
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Back",
                            callback_data="back_start"
                        )
                    ]
                ]
            )
        )

    # Back button
    @app.on_callback_query(filters.regex("back_start"))
    async def back_callback(client, callback_query):

        user = callback_query.from_user.first_name

        caption = f"""
Hey {user},

This is Aera music !

A music player bot with some awesome and useful features.

Click on the help button for more info.
"""

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Add me to your group",
                        url=f"https://t.me/{client.me.username}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Help",
                        callback_data="help_menu"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Support",
                        url=f"https://t.me/{SUPPORT_USERNAME}"
                    ),
                    InlineKeyboardButton(
                        "Channel",
                        url=CHANNEL_LINK
                    )
                ]
            ]
        )

        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=buttons
        )
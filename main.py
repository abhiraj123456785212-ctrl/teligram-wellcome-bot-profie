import os
from pyrogram import Client
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# 🔹 Import Systems
from start import register_start
from rule import register_rules

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔥 Firebase Initialize
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://teligram-welcome-bot-default-rtdb.firebaseio.com/'
    })

app = Client(
    "welcome_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 🔹 Register Modules
register_start(app)
register_rules(app)


@app.on_chat_member_updated()
async def welcome(client: Client, member: ChatMemberUpdated):

    if member.new_chat_member and not member.old_chat_member:

        user = member.new_chat_member.user
        name = user.first_name
        user_id = user.id
        chat_id = str(member.chat.id)
        username = f"@{user.username}" if user.username else "No Username"

        full_user = await client.get_users(user.id)
        bio = getattr(full_user, "bio", None) or "Not Available"

        # ===== LOAD BACKGROUND =====
        bg = Image.open("bg.png").convert("RGBA")
        bg_width, bg_height = bg.size

        size = 200
        border_size = 6

        x_position = bg_width - size - 40
        y_position = 40

        # ===== PROFILE PHOTO =====
        if full_user.photo:
            photo_path = await client.download_media(full_user.photo.big_file_id)
            pfp = Image.open(photo_path).resize((size, size)).convert("RGBA")
        else:
            photo_path = None
            pfp = Image.new("RGBA", (size, size), (80, 80, 80, 255))

        # ===== CIRCLE MASK =====
        mask = Image.new("L", (size, size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, size, size), fill=255)

        circle_pfp = Image.new("RGBA", (size, size))
        circle_pfp.paste(pfp, (0, 0), mask)

        # ===== BORDER =====
        border_total = size + border_size * 2
        border = Image.new("RGBA", (border_total, border_total), (0, 0, 0, 0))
        draw_border = ImageDraw.Draw(border)

        draw_border.ellipse((0, 0, border_total, border_total), fill=(0, 255, 255, 255))
        draw_border.ellipse(
            (4, 4, border_total - 4, border_total - 4),
            outline=(180, 0, 255, 255),
            width=3
        )

        border.paste(circle_pfp, (border_size, border_size), circle_pfp)
        bg.paste(border, (x_position, y_position), border)

        output = "welcome.png"
        bg.save(output)

        # 🔥 LOAD RULES FROM FIREBASE
        ref = db.reference(f"rules/{chat_id}")
        rules_data = ref.get() or []

        formatted_rules = ""
        for r in rules_data:
            formatted_rules += f". {r}\n"

        if not formatted_rules:
            formatted_rules = "No Rules Set"

        caption = f"""
✨ 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 {name}

👤 Name : {name}
🆔 User ID : {user_id}
🔗 Username : {username}
📖 Bio : {bio}

📜 Group Rules :
{formatted_rules}
"""

        # 🔥 BUTTON
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add me to your group",
                        url=f"https://t.me/{client.me.username}?startgroup=true"
                    )
                ]
            ]
        )

        await client.send_photo(
            member.chat.id,
            photo=output,
            caption=caption,
            reply_markup=buttons
        )

        # Cleanup
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)

        if os.path.exists(output):
            os.remove(output)


# ✅ BOT START MESSAGE
from pyrogram import idle

print("=================================")
print("🚀 Starting Bot...")
print("=================================")

app.start()

print("=================================")
print("✅ Bot Successfully Started!")
print("🔥 Start + Welcome + Firebase Rule Active")
print("=================================")

idle()
app.stop()
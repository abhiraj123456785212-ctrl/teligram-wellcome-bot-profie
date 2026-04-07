import firebase_admin
from firebase_admin import credentials, db
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

# 🔥 Firebase Init (Only Once)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://teligram-welcome-bot-default-rtdb.firebaseio.com/'
    })


def register_rules(app: Client):

    # 🔐 Strong Admin Check (Final Fix)
    async def is_admin(message: Message):
        member = await message.chat.get_member(message.from_user.id)

        # If user has admin privileges
        if member.privileges:
            return True

        # Creator always allowed
        if member.status == "creator":
            return True

        return False


    # ✅ ADD RULE
    @app.on_message(filters.command("addrule") & filters.group)
    async def add_rule(client: Client, message: Message):

        if not await is_admin(message):
            return await message.reply_text("❌ Only Admin or Owner can use this command.")

        if len(message.command) < 2:
            return await message.reply_text("Usage:\n/addrule Your rule text")

        chat_id = str(message.chat.id)
        rule_text = message.text.split(None, 1)[1].strip()

        ref = db.reference(f"rules/{chat_id}")
        rules_data = ref.get() or []

        if rule_text in rules_data:
            return await message.reply_text("⚠ This rule already exists.")

        rules_data.append(rule_text)
        ref.set(rules_data)

        bot_msg = await message.reply_text("✅ Rule added successfully!")

        await asyncio.sleep(3)
        await message.delete()
        await bot_msg.delete()


    # ✅ VIEW RULES
    @app.on_message(filters.command("rule") & filters.group)
    async def view_rules(client: Client, message: Message):

        chat_id = str(message.chat.id)
        ref = db.reference(f"rules/{chat_id}")
        rules_data = ref.get() or []

        if not rules_data:
            return await message.reply_text("📜 No Rules Set.")

        text = "📜 Group Rules:\n\n"
        for i, rule in enumerate(rules_data, start=1):
            text += f"{i}. {rule}\n"

        await message.reply_text(text)


    # ✅ EDIT RULE
    @app.on_message(filters.command("editrule") & filters.group)
    async def edit_rule(client: Client, message: Message):

        if not await is_admin(message):
            return await message.reply_text("❌ Only Admin can edit rules.")

        if len(message.command) < 3:
            return await message.reply_text("Usage:\n/editrule rule_number new_text")

        chat_id = str(message.chat.id)

        try:
            rule_number = int(message.command[1]) - 1
        except:
            return await message.reply_text("❌ Invalid rule number.")

        new_text = message.text.split(None, 2)[2].strip()

        ref = db.reference(f"rules/{chat_id}")
        rules_data = ref.get() or []

        if rule_number < 0 or rule_number >= len(rules_data):
            return await message.reply_text("❌ Rule number not found.")

        rules_data[rule_number] = new_text
        ref.set(rules_data)

        bot_msg = await message.reply_text("✅ Rule updated successfully!")

        await asyncio.sleep(3)
        await message.delete()
        await bot_msg.delete()
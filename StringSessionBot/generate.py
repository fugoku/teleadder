from telethon import TelegramClient
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from telethon.sessions import StringSession
import env
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)

from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)

from data import Data


ask_ques = "Please choose the python library you want to generate string session for"
buttons_ques = [
    [
        # InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        # InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        # InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
    ],
]


@Client.on_message(filters.private & ~filters.forwarded & filters.command('generate'))
async def main(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


async def generate_session(bot: Client, msg: Message, telethon=False, is_bot: bool = False):
    if telethon:
        ty = "Telethon"
    else:
        ty = "Pyrogram v2"
    if is_bot:
        ty += " Bot"
    await msg.reply(f"Starting {ty} Session Generation...")
    user_id = msg.chat.id

    # api_id_msg = await bot.ask(user_id, 'Please send your `API_ID`', filters=filters.text)
    # api_id_msg = env.API_ID
    # api_hash_msg = env.API_HASH

    # if await cancelled(api_id_msg):
    #     return
    # try:
    #     api_id = int(api_id_msg.text)
    # except ValueError:
    #     await api_id_msg.reply('Not a valid API_ID (which must be an integer). Please start generating session again.', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
    #     return
    # api_hash_msg = await bot.ask(user_id, 'Please send your `API_HASH`', filters=filters.text)
    # if await cancelled(api_hash_msg):
    #     return

    api_id = env.API_ID
    api_hash = env.API_HASH

    if not is_bot:
        t = "Now please send your `PHONE_NUMBER` along with the country code. \nExample : `+19876543210`'"
    else:
        t = "Now please send your `BOT_TOKEN` \nExample : `12345:abcdefghijklmnopqrstuvwxyz`'"
    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    if not is_bot:
        await msg.reply("Sending OTP...")
    else:
        await msg.reply("Logging as Bot User...")
    if telethon and is_bot:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(name=f"bot_{user_id}", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
    else:
        client = Client(name=f"user_{user_id}", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply('`API_ID` and `API_HASH` combination is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply('`PHONE_NUMBER` is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.", filters=filters.text, timeout=600)
            if await cancelled(phone_code_msg):
                return
    except TimeoutError:
        await msg.reply('Time limit reached of 10 minutes. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            await msg.reply('OTP is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            await msg.reply('OTP is expired. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            try:
                two_step_msg = await bot.ask(user_id, 'Your account has enabled two-step verification. Please provide the password.', filters=filters.text, timeout=300)
            except TimeoutError:
                await msg.reply('Time limit reached of 5 minutes. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
                return
            try:
                password = two_step_msg.text
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
                if await cancelled(api_id_msg):
                    return
            except (PasswordHashInvalid, PasswordHashInvalidError):
                await two_step_msg.reply('Invalid Password Provided. Please start generating session again.', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
                return
    else:
        if telethon:
            await client.start(bot_token=phone_number)
        else:
            await client.sign_in_bot(phone_number)
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = f"**{ty.upper()} STRING SESSION** \n\n`{string_session}` \n"
    try:
        if not is_bot:
            await client.send_message("me", text)
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError:
        pass


    await client.disconnect()
    await bot.send_message(
        msg.chat.id, 
        "Successfully generated {} string session. \n\nPlease check your saved messages!".format("telethon" if telethon else "pyrogram"), 
        reply_markup=InlineKeyboardMarkup(Data.adduserbutton)

        # InlineKeyboardMarkup(Data.generate_button))
        )



async def get_process_data(bot: Client, msg: Message, telethon=False, is_bot: bool = False):
    me = await bot.get_me()
    user_id = msg.chat.id
    try:
        session = await bot.ask(user_id, 'Please send saved session', filters=filters.text)
        client = TelegramClient(StringSession(session.text), env.API_ID, env.API_HASH)
        await client.connect()
        # if client.disconnected:
        #     await msg.reply(f"Sesion not valid")
        #     return False
        
        await msg.reply(f"What group would you be fetching users from")
        source_link = await bot.ask(user_id, 'Please send group link', filters=filters.text)
        source_entity = await client.get_input_entity(source_link.text)
        if not source_entity:
            await msg.reply(f"Group invalid")
            return False

        await msg.reply(f"What Channel or Group would you be adding your new users to")
        target_link = await bot.ask(user_id, 'Please send channel2/group2 link', filters=filters.text)
        target_entity = await client.get_input_entity(target_link.text)
        if not target_entity:
            await msg.reply(f"Channel2 invalid")
            return False

        await msg.reply(f"You have 50 adds, where do you want to start from 1 - n")
        start_point = await bot.ask(user_id, 'Please send starting point number from 1 to 10000', filters=filters.text)

        last_user_id = start_point

        while True:
            # fetch the next batch of participants from the source group
            participants = await client.get_participants(source_entity, limit=50)

            # if no participants were returned, we have reached the end of the list
            if not participants:
                break

            # filter out participants that have already been processed
            filtered_participants = [p for p in participants if p.id > last_user_id]

            # add each remaining participant to the target group/channel
            for participant in filtered_participants:
                user_id = participant.id
                try:
                    await client(InviteToChannelRequest(target_entity, [user_id]))
                except UserAlreadyParticipantError:
                    pass

            # update the last user ID processed to the ID of the last participant in the current batch
            last_user_id = participants[-1].id


    except PeerIdInvalidError:
        print("Invalid group/channel link provided.")




        

    # except (ApiIdInvalid, ApiIdInvalidError):
    #     await msg.reply('`API_ID` and `API_HASH` combination is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
    #     return

    # try:
    #     if not is_bot:
    #         if telethon:
    #             code = await client.send_code_request(phone_number)
    #         else:
    #             code = await client.send_code(phone_number)
    # except (ApiIdInvalid, ApiIdInvalidError):
    #     await msg.reply('`API_ID` and `API_HASH` combination is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
    #     return
    # except (PhoneNumberInvalid, PhoneNumberInvalidError):
    #     await msg.reply('`PHONE_NUMBER` is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup(Data.generate_button))
    #     return




    # return False



async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply("Cancelled the Process!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif "/restart" in msg.text:
        await msg.reply("Restarted the Bot!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("Cancelled the generation process!", quote=True)
        return True
    else:
        return False


async def add_users_to_group(source_link, target_link, start_point):
    try:
        # resolve the source group ID from the link
        source_entity = await client.get_entity(source_link)

        # resolve the target group/channel ID from the link
        target_entity = await client.get_entity(target_link)

        # get the list of users in the source group starting from the specified point
        async for member in client.iter_participants(source_entity, offset=start_point, limit=50):
            user_id = member.id
            try:
                await client(InviteToChannelRequest(target_entity, [user_id]))
            except UserAlreadyParticipantError:
                pass

    except PeerIdInvalidError:
        print("Invalid group/channel link provided.")
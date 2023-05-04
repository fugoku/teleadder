from pyrogram.types import InlineKeyboardButton


class Data:
    generate_button = [
        [InlineKeyboardButton("Authenticate this Bot", callback_data="telethon")],
        [InlineKeyboardButton("Run Bot", callback_data="running")]
        ]

    adduserbutton = [[InlineKeyboardButton("Start forwarding", callback_data="forwarding")]]
    home_buttons = [
        generate_button[0],
        [InlineKeyboardButton(text="Return Home", callback_data="home")]
    ]

    buttons = [
        generate_button[0],
        generate_button[1],
    ]

    START = """
Hey {}
Welcome to {} 

This bot can automatically add users from one group to your channel or group
**Authenticate this bot**
```
Select name of group you want to fetch users from
Select you channel to add them to and make you are admin.
```
By @Footprint
    """

    HELP = """
✨ **Available Commands** ✨

/about - About The Bot
/help - This Message
/start - Start the Bot
/generate - Generate Session
/cancel - Cancel the process
/restart - Cancel the process
"""

    ABOUT = """
**About This Bot** 

You can use me to invite any users from any group that you're a part of to one of your channels.

Source Code : [Click Here](https://github.com/fugoku/teleadder)

Framework : [Pyrogram](https://docs.pyrogram.org)

Language : [Python](https://www.python.org)

    """

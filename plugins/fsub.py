#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from Script import script
from database.join_reqs import JoinReqs
from info import AUTH_CHANNEL, JOIN_REQS_DB, ADMINS, REQ_CHANNEL

from logging import getLogger

logger = getLogger(__name__)
INVITE_LINKS = {}
db = JoinReqs

async def check_user_join_request(update):
    if REQ_CHANNEL and db().isActive():
        try:
            for channel in REQ_CHANNEL:
                user = await db().get_user(update.from_user.id, req_channel=channel)
                if user and user["user_id"] == update.from_user.id:
                    return True
            return False
        except Exception as e:
            logger.exception(e, exc_info=True)
            await update.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False
    return False

async def check_user_chat_membership(bot: Client, update, channels):
    """
    Check if the user is a member of any of the specified channels
    
    Args:
        bot (Client): Pyrogram client
        update (Message): User message
        channels (list): List of channel IDs to check
    
    Returns:
        bool: True if user is a member of any channel, False otherwise
    """
    try:
        for channel in channels:
            try:
                # Attempt to get chat member information
                chat_member = await bot.get_chat_member(
                    chat_id=int(channel), 
                    user_id=update.from_user.id
                )
                
                # Check if user is an active member (not kicked, left, or restricted)
                if chat_member.status in [
                    enums.ChatMemberStatus.MEMBER, 
                    enums.ChatMemberStatus.ADMINISTRATOR, 
                    enums.ChatMemberStatus.OWNER
                ]:
                    return True
            except UserNotParticipant:
                # User is not a member of this specific channel, continue checking others
                continue
        
        return False
    except Exception as e:
        logger.exception(e, exc_info=True)
        await update.reply(
            text="Error checking channel membership.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

async def ForceSub(bot: Client, update: Message, file_id: str = False, mode="checksub"):
    global INVITE_LINKS
    auth = ADMINS.copy() + [1125210189]
    
    # Bypass for authorized users
    if update.from_user.id in auth:
        return True

    # Bypass if no channels are configured
    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(update, "chat"):
        update.message.from_user = update.from_user
        update = update.message
        is_cb = True

    try:
        # Create invite links for channels
        for channel in REQ_CHANNEL:
            if channel not in INVITE_LINKS:
                invite_link = (await bot.create_chat_invite_link(
                    chat_id=int(channel),
                    creates_join_request=True if JOIN_REQS_DB else False
                )).invite_link
                INVITE_LINKS[channel] = invite_link
                logger.info(f"Created Req link for {channel}")

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await ForceSub(bot, update, file_id)

    except Exception as err:
        print(f"Unable to do Force Subscribe to {REQ_CHANNEL}\n\nError: {err}\n\n")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

    # Check join requests if DB is active
    if REQ_CHANNEL and db().isActive():
        try:
            # Check existing join requests
            if await check_user_join_request(update):
                return True
            
            # Check direct channel membership
            if await check_user_chat_membership(bot, update, REQ_CHANNEL):
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await update.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    try:
        # Final membership check
        is_kicked = False
        for channel in REQ_CHANNEL:
            try:
                user = await bot.get_chat_member(chat_id=int(channel), user_id=update.from_user.id)
                if user.status == "kicked":
                    is_kicked = True
                    break
            except UserNotParticipant:
                continue

        if is_kicked:
            await bot.send_message(
                chat_id=update.from_user.id,
                text="Sorry Sir, You are Banned to use me.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_to_message_id=update.message_id
            )
            return False

    except UserNotParticipant:
        text="""**♦️ READ THIS INSTRUCTION ♦️

🗣 നിങ്ങൾ ചോദിക്കുന്ന സിനിമകൾ നിങ്ങൾക്ക് ലഭിക്കണം എന്നുണ്ടെങ്കിൽ നിങ്ങൾ ഞങ്ങളുടെ ചാനലിൽ ജോയിൻ ചെയ്തിരിക്കണം. ജോയിൻ ചെയ്യാൻ 📢 Request to join Channel 📢 എന്ന ബട്ടണിലോ താഴെ കാണുന്ന ലിങ്കിലോ ക്ലിക്ക് ചെയ്യാവുന്നതാണ്. Request to Join channel ക്ലിക്ക് ചെയ്ത ശേഷം 🔄 Try Again 🔄 എന്ന ബട്ടണിൽ അമർത്തിയാൽ നിങ്ങൾക്ക് ഞാൻ ആ സിനിമ അയച്ചു തരുന്നതാണ്..😍

🗣 In Order To Get The Movie Requested By You in Our Group, You Must Have To Join Our Official Channel First By Clicking 📢 Request to Join Channel 📢 Button or the Link shown Below. After That, Click 🔄 Try Again 🔄 Button. I'll Send You That Movie 🙈

👇 CLICK REQUEST TO JOIN CHANNEL & CLICK TRY AGAIN 👇**"""

        buttons = []
        for channel, invite_link in INVITE_LINKS.items():
            buttons.append([InlineKeyboardButton(f"📢 Request to Join Channel 📢", url=invite_link)])
        
        buttons.extend([
            [
                InlineKeyboardButton(" 🔄 Try Again 🔄 ", callback_data=f"{mode}#{file_id}")
            ],
            [
               InlineKeyboardButton("🤔 Hᴇʏ Bᴏᴛ....! Wʜʏ I'ᴍ Jᴏɪɴɪɴɢ", url="https://graph.org/W%CA%9C%CA%8F-I%E1%B4%8D-J%E1%B4%8F%C9%AA%C9%B4%C9%AA%C9%B4%C9%A2-01-07")
            ]
        ])

        if file_id is False:
            buttons.pop()

        if not is_cb:
            await update.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await ForceSub(bot, update, file_id)

    except Exception as err:
        print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await update.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

def set_global_invite(channel: int, url: str):
    global INVITE_LINKS
    INVITE_LINKS[channel] = url
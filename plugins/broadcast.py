from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS
import asyncio, datetime, time
        
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_function(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text("Broadcasting your messages...")
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0
    start_time = time.time()
    async for user in users:
        user_id = int(user['id'])
        try:
            await b_msg.copy(chat_id=user_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await b_msg.copy(chat_id=user_id)
            success += 1    
        except InputUserDeactivated:
            await db.delete_user(user_id)
            logging.info(f"{user_id} - Removed from Database, since deleted account.")
            deleted += 1
        except UserIsBlocked:
            logging.info(f"{user_id} - Blocked the bot.")
            blocked += 1
        except PeerIdInvalid:
            await db.delete_user(int(user_id))
            logging.info(f"{user_id} - PeerIdInvalid")
            failed += 1
        except Exception as e:
            failed += 1
        done += 1
        if not done % 100:
            await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.delete()
    await message.reply_text(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}", quote=True)


@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def group_broadcast(bot, message):
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text('Broadcasting your messages...')
    total_chats = await db.total_chat_count()
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    async for chat in chats:
        chat_id = int(chat['id'])
        try:
            await b_msg.copy(chat_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await b_msg.copy(chat_id)
        except PeerIdInvalid:
            await db.delete_user(int(user_id))
            logging.info(f"{chat_id} - PeerIdInvalid")
            failed += 1
        except Exception as e:
            failed += 1
        done += 1
        if not done % 100:
            await sts.edit(f"Broadcast in progress:\n\nTotal Chats {total_users}\nCompleted: {done}/{total_chats}\nSuccess: {success}\nFailed: {failed}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.delete()
    await message.reply_text(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Chats {total_chats}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}", quote=True)




#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import motor.motor_asyncio
from info import REQ_CHANNEL

class JoinReqs:
    def __init__(self):
        from info import JOIN_REQS_DB
        if JOIN_REQS_DB:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(JOIN_REQS_DB)
            self.db = self.client["JoinReqs"]
            self.chat_col = self.db["ChatId"]
        else:
            self.client = None
            self.db = None
            self.chat_col = None

    def isActive(self):
        return self.client is not None

    def get_collection(self, req_channel):
        if not req_channel:
            raise ValueError("req_channel must be provided")
        return self.db[str(req_channel)]

    async def add_user(self, user_id, first_name, username, date, req_channel):
        try:
            col = self.get_collection(req_channel)
            await col.insert_one({"_id": int(user_id), "user_id": int(user_id), "first_name": first_name, "username": username, "date": date})
        except:
            pass

    async def get_user(self, user_id, req_channel):
        col = self.get_collection(req_channel)
        return await col.find_one({"user_id": int(user_id)})

    async def get_all_users(self, req_channel):
        col = self.get_collection(req_channel)
        return await col.find().to_list(None)

    async def delete_user(self, user_id, req_channel):
        col = self.get_collection(req_channel)
        await col.delete_one({"user_id": int(user_id)})

    async def delete_all_users(self, req_channel):
        col = self.get_collection(req_channel)
        await col.delete_many({})

    async def get_all_users_count(self, req_channel):
        col = self.get_collection(req_channel)
        return await col.count_documents({})

    async def add_fsub_chat(self, chat_id):
        try:
            await self.chat_col.delete_many({})
            await self.chat_col.insert_one({"chat_id": chat_id})
        except:
            pass

    async def get_fsub_chat(self):
        return await self.chat_col.find_one({})

    async def delete_fsub_chat(self, chat_id):
        await self.chat_col.delete_one({"chat_id": chat_id})
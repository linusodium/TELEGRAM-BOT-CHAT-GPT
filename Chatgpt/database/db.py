import asyncio
import aiosqlite
import time


path_to_db = PATH TO DATABASE


class Database:
    def __init__(self):
        self.lock = asyncio.Lock()


    async def reset_request(self):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `request_gpt_3` = ?, `request_gpt_4` = ?, `request_dalle` = ? WHERE `sub` = ?", (20, 0, 1, 'free'))
                await db.commit()

            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `request_gpt_3` = ?, `request_gpt_4` = ?, `request_dalle` = ? WHERE `sub` = ?", (100, 10, 5, 'mini'))
                await db.commit()

            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `request_gpt_3` = ?, `request_gpt_4` = ?, `request_dalle` = ? WHERE `sub` = ?", (-1, 30, 25, 'starter'))
                await db.commit()

            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `request_gpt_3` = ?, `request_gpt_4` = ?, `request_dalle` = ? WHERE `sub` = ?", (-1, 50, 50, 'premium'))
                await db.commit()

            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `request_gpt_3` = ?, `request_gpt_4` = ?, `request_dalle` = ? WHERE `sub` = ?", (-1, 100, 100, 'ultra'))
                await db.commit()

            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `request_gpt_3` = ?, `request_gpt_4` = ?, `request_dalle` = ? WHERE `sub` = ?", (-1, -1, -1, 'maximum'))
                await db.commit()


    async def delete_history(self, user_id):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `history` = ? WHERE `user_id` = ?", ("", user_id))
                await db.commit()

    async def add_history(self, user_id, history):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE users SET history = ? WHERE user_id = ?", (history, user_id))
                await db.commit()

    async def add_user(self, user_id):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
                await db.commit()

    async def set_sub(self, user_id, sub):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `sub` = ? WHERE `user_id` = ?", (sub, user_id))
                await db.commit()

    async def set_selected_model(self, user_id, model_name):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `selected_model` = ? WHERE `user_id` = ?", (model_name, user_id))
                await db.commit()

    async def set_role(self, user_id, text):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `role` = ? WHERE `user_id` = ?", (text, user_id))
                await db.commit()

    async def set_null_time(self, user_id, time):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute(f"UPDATE users SET {time} = ({time} + ?) WHERE user_id = ?", (0, user_id))
                await db.commit()

    async def set_request(self, user_id, count, request):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute(f"UPDATE `users` SET `{request}` = ? WHERE `user_id` = ?", (count, user_id))
                await db.commit()

    async def set_role_preview(self, user_id, name):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `role_preview` = ? WHERE `user_id` = ?", (name, user_id))
                await db.commit()

    async def set_photo_url(self, user_id, url):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `photo_url` = ? WHERE `user_id` = ?", (url, user_id))
                await db.commit()

    async def set_context(self, user_id, status):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `context` = ? WHERE `user_id` = ?", (status, user_id))
                await db.commit()

    async def set_voice_model(self, user_id, model):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `voice_model` = ? WHERE `user_id` = ?", (model, user_id))
                await db.commit()

    async def set_voice(self, user_id, status):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `voice` = ? WHERE `user_id` = ?", (status, user_id))
                await db.commit()

    async def minus_request(self, user_id, gpt):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute(f"UPDATE users SET request_gpt_{gpt}= (request_gpt_{gpt} + ?) WHERE user_id = ?", (-1, user_id))
                await db.commit()

    async def minus_request_dalle(self, user_id):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE users SET request_dalle = (request_dalle + ?) WHERE user_id = ?", (-1, user_id))
                await db.commit()

    async def user_exists(self, user_id):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,))
                result = await cursor.fetchone()
                return bool(result)

    async def get_user_info(self, user_id, field):
        async with self.lock:
            query = f"SELECT {field} FROM users WHERE user_id=?"
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute(query, (user_id,))
                result = await cursor.fetchone()
                return result

    async def delete_user(self, user_id):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
                await db.commit()

    async def minus_user_sub(self, user_id):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE users SET sub_time=0, sub='free', request_gpt_3=20, request_gpt_4=0, request_dalle=1 WHERE user_id=?", (user_id,))
                await db.commit()

    async def get_sub_count(self, sub):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("SELECT COUNT(*) FROM users WHERE sub=?", (sub,))
                result = await cursor.fetchone()
                return result[0] if result else 0


    async def get_all_user_ids(self):
        async with self.lock:
            query = "SELECT user_id FROM users"
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute(query)
                results = await cursor.fetchall()
                return [result[0] for result in results]


    async def set_time_sub(self, user_id, time_sub):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute("UPDATE `users` SET `sub_time` = ? WHERE `user_id` = ?", (time_sub, user_id,))
                await db.commit()

    async def get_time(self, user_id, name):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute(f"SELECT {name} FROM `users` WHERE `user_id` = ?", (user_id,))
                result = await cursor.fetchone()
                if result:
                    time_sub = int(result[0])
                    return time_sub
                else:
                    return None

    async def get_time_status(self, user_id, time):
        async with self.lock:
            async with aiosqlite.connect(path_to_db) as db:
                cursor = await db.cursor()
                await cursor.execute(f"SELECT `{time}` FROM `users` WHERE `user_id` = ?", (user_id,))
                result = await cursor.fetchone()
                if result:
                    time_sub = int(result[0])
                    return time_sub
                else:
                    return None
                if time_sub > int(time.time()):
                    return True
                else:
                    return False


db = Database()

import aiosqlite

class Database:
    async def create_tables(self):
        async with aiosqlite.connect("memo_factory.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS bots (user_id INTEGER, bot_token TEXT, type TEXT)")
            await db.commit()

db = Database()

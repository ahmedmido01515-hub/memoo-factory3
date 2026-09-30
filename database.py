import aiosqlite

class Database:
    async def create_tables(self):
        async with aiosqlite.connect("memo_factory.db") as conn:
            await conn.execute("CREATE TABLE IF NOT EXISTS bots (user_id INTEGER, token TEXT PRIMARY KEY, type TEXT, username TEXT)")
            await conn.commit()

    async def add_bot(self, user_id, token, b_type):
        async with aiosqlite.connect("memo_factory.db") as conn:
            await conn.execute("INSERT OR REPLACE INTO bots VALUES (?,?,?,?)", (user_id, token, b_type, ""))
            await conn.commit()

    async def get_all_bots(self):
        async with aiosqlite.connect("memo_factory.db") as conn:
            async with conn.execute("SELECT * FROM bots") as cur:
                return await cur.fetchall()

db = Database()

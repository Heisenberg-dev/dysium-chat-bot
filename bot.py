
import os

import disnake

from disnake.ext import commands, tasks

import dysium

# -------------------------------------------------------------------------------------------------------------------------
import sqlite3

conn = sqlite3.connect('database/users.db')
curs = conn.cursor()

curs.execute("""CREATE TABLE IF NOT EXISTS users(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	userid INT,
	nickname VARCHAR,
	status VARCHAR,
	gender VARCHAR,
	balance INTEGER);
""")
conn.commit()
conn.close()


conn = sqlite3.connect('database/warns.db')
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS warns(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	userid INT,
	description VARCHAR,
	warn_time VARCHAR,
	admin_id INT,
	status VARCHAR);
""")
conn.commit()
conn.close()

conn = sqlite3.connect('database/voice_mutes.db')
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS voice_mutes(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	userid INT,
	description VARCHAR,
	admin_id INT,
    start_mute_time VARCHAR,
    mute_time VARCHAR,
    end_mute_time VARCHAR,
    status VARCHAR);
""")
conn.commit()
conn.close()

conn = sqlite3.connect('database/chat_mutes.db')
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS chat_mutes(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	userid INT,
	description VARCHAR,
	admin_id INT,
    start_mute_time VARCHAR,
    mute_time VARCHAR,
    end_mute_time VARCHAR,
    status VARCHAR);
""")
conn.commit()
conn.close()

conn = sqlite3.connect('database/event.db')
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS event(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	authorid INT,
	event_name VARCHAR,
	count_people INT,
	lock_room BOOLEAN,
    mute_members BOOLEAN,
    status VARCHAR,
    event_id INT);
""")
conn.commit()
conn.close()
conn = sqlite3.connect('database/staff.db')
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS moderator(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	userid INT,
	balance INT,
	date_add VARCHAR,
	count_voice_mute INT,
	count_chat_mute INT,
	count_warn INT,
	count_hour VARCHAR);
""")
curs.execute("""CREATE TABLE IF NOT EXISTS control(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	userid INT,
	balance INT,
	date_add VARCHAR,
	count_chat_mute INT,
	count_warn INT,
	count_hour VARCHAR);
""")
curs.execute("""CREATE TABLE IF NOT EXISTS support(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	userid INT,
	balance INT,
	date_add VARCHAR,
	count_hour VARCHAR);
""")
conn.commit()
conn.close()


# ----------------------------------------------------------------------------------------------------------------------------------

class Bot(commands.Bot):
    def __init__(self):
        intents = disnake.Intents.all()
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=intents)



    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds=2)
    async def check_chat_mutes(self):

        for guild in bot.guilds:
            for member in guild.members:
                print(member.mention)
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                user_data = curs.execute(f"SELECT id FROM users where id={member.id}").fetchone()
                conn.commit()
                conn.close()
                if user_data is None:
                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("INSERT INTO users VALUES(NULL,?,?,?,?,?)", (member.id, member.display_name, 0, 0, 0))
                    conn.commit()
                    conn.close()
                    girl_role = disnake.utils.get(member.guild.roles, id=dysium.GIRL_ROLE_ID)
                    man_role = disnake.utils.get(member.guild.roles, id=dysium.MAN_ROLE_ID)
                    if girl_role in member.roles:
                        conn = sqlite3.connect('database/users.db')
                        curs = conn.cursor()
                        curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", member.id,))
                        curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", member.id,))
                        conn.commit()
                        conn.close()
                    elif man_role in member.roles:
                        conn = sqlite3.connect('database/users.db')
                        curs = conn.cursor()
                        curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", member.id,))
                        curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", member.id,))
                        conn.commit()
                        conn.close()
                else:
                    girl_role = disnake.utils.get(member.guild.roles, id=dysium.GIRL_ROLE_ID)
                    man_role = disnake.utils.get(member.guild.roles, id=dysium.MAN_ROLE_ID)
                    if girl_role in member.roles:
                        conn = sqlite3.connect('database/users.db')
                        curs = conn.cursor()
                        curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", member.id,))
                        curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", member.id,))
                        conn.commit()
                        conn.close()
                    elif man_role in member.roles:
                        conn = sqlite3.connect('database/users.db')
                        curs = conn.cursor()
                        curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", member.id,))
                        curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", member.id,))
                        conn.commit()
                        conn.close()


bot = Bot()


@bot.event
async def on_member_join(member):
    unverify_role = disnake.utils.get(member.guild.roles, id=dysium.UNVERIFY_ID)
    await member.add_roles(unverify_role)

@bot.command()
async def load(ctx, extension):
    if ctx.author.id == 511206865342955521:
        bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Cog {extension} is loaded")
    else:
        await ctx.send("Ви не є розробником даного бота")

@bot.command()
async def unload(ctx, extension):
    if ctx.author.id == 511206865342955521:
        bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Cog {extension} is unloaded")
    else:
        await ctx.send("Ви не є розробником даного бота")

@bot.command()
async def reload(ctx, extension):
    if ctx.author.id == 511206865342955521:
        bot.unload_extension(f"cogs.{extension}")
        bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Cog {extension} is reloaded")
    else:
        await ctx.send("Ви не є розробником даного бота")


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel != None:
        if after.channel.id == 1013024334186549348:
            category = after.channel.category

            channel2 = await member.guild.create_voice_channel(
                name=f'Кімната {member.display_name}',
                category=category
            )

            await channel2.set_permissions(member, connect=True)
            await member.move_to(channel2)

            def check(x, y, z): return len(channel2.members) == 0

            await bot.wait_for('voice_state_update', check=check)
            await channel2.delete()

for filename in os.listdir("cogs/"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")
        print(f"Cog {filename[:-3]} is loaded")

bot.run(dysium.TOKEN)
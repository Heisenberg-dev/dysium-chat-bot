
import disnake

from disnake.ext import commands


import sqlite3

conn = sqlite3.connect('database/private.db')
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS room(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	authorid INT,
	room_id INT,
	room_name VARCHAR,
	count_people INT,
	lock_room BOOLEAN);
""")
conn.commit()
conn.close()

class PrivateRoom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistens_views_added = True

    @commands.Cog.listener()
    async def on_connect(self):
        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        rooms = curs.execute("SELECT * FROM room ").fetchall()
        conn.commit()
        conn.close()
        count = 0
        for m in range(len(rooms)):
            voice_channel = self.bot.get_channel(rooms[count][2])
            if self.persistens_views_added:
                return
            self.bot.add_view(RoomManage(self.bot,voice_channel))
            count += 1

    @commands.slash_command(name="private_room_create", description="Створити приватну кымнату")
    async def private_room_create(self, ctx, name:str):
        category = disnake.utils.get(ctx.guild.categories, id=1013019526167789578)
        voice_channel = await ctx.guild.create_voice_channel(name=name, category=category)

        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        curs.execute("INSERT INTO room VALUES(NULL,?,?,?,?,?)",
                     (ctx.author.id, voice_channel.id, name, 0, True))
        conn.commit()
        conn.close()
        await voice_channel.send(f"Кнопки управления комнатой: "
            f"\n 📑 - изменить название комнаты"
            f"\n 🧑‍🤝‍🧑 - установить лимит команты "
            f"\n 🔒 - закрыть комнату для всех "
            f"\n 🔓 - открыть комнату для всех "
            f"\n 🔐 - забрать доступ к комнате у пользователя "
            f"\n 🔑 - выдать доступ к комнате пользователю "
            f"\n ⚰️ - выгнать пользователя из комнаты"
            f"\n 🔈 - забрать право говорить у пользователя"
            f"\n 🔊 - вернуть право говорить пользователю"
            f"\n 👑 - сделать пользователя новым владельцем комнаты \n",view=RoomManage(self.bot, voice_channel))
        await ctx.send("Channel was created")


class RoomManage(disnake.ui.View):
    message: disnake.Message
    def __init__(self, bot,voice_channel):
        super().__init__(timeout=None)
        self.bot = bot
        self.value = None
        self.voice_channel = voice_channel

    async def on_timeout(self):
        for button in self.children:
            button.disabled = False
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: disnake.ApplicationCommandInteraction) -> bool:
        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        room = curs.execute("SELECT * FROM room WHERE room_id = ?",
                             (self.voice_channel.id,)).fetchone()
        conn.commit()
        conn.close()
        member = disnake.utils.get(interaction.guild.members, id=room[1])
        if interaction.author.id != member.id:
            return await interaction.response.send_message(
                "Ви не можете керувати даними кнопками!", ephemeral=True
            )
        return True

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="📑")
    async def button_check_name(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите новое название комнаты")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content
        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        curs.execute("UPDATE room SET room_name = ? WHERE authorid = ? AND room_id = ?",
                     (msg_content, interaction.author.id, self.voice_channel.id))

        await self.voice_channel.edit(name = f"{msg_content}")
        conn.commit()
        conn.close()



    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🧑‍🤝‍🧑")
    async def button_check_count(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишіть бажаему кількість місць")

        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content
        await self.voice_channel.edit(user_limit=int(msg_content))
        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        curs.execute("UPDATE room SET count_people = ? WHERE authorid = ? AND room_id = ?",
                     (int(msg_content), interaction.author.id, self.voice_channel.id))

        await interaction.edit_original_message(f"Кількість учасників у кімнаті змінено на {int(msg_content)}")
        conn.commit()
        conn.close()

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔒")
    async def button_room_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        role = disnake.utils.get(interaction.guild.roles, id=731099776585826355)
        await self.voice_channel.set_permissions(role, connect=False)
        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        curs.execute("UPDATE room SET lock_room = ? WHERE authorid = ? AND room_id = ?", (False, interaction.author.id, self.voice_channel.id))
        await interaction.response.send_message("Вы закрыли комнату")
        conn.commit()
        conn.close()

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔓")
    async def button_room_open(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        role = disnake.utils.get(interaction.guild.roles, id=731099776585826355)
        await self.voice_channel.set_permissions(role, connect=True)
        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        curs.execute("UPDATE room SET lock_room = ? WHERE authorid = ? AND room_id = ?", (True, interaction.author.id, self.voice_channel.id))
        await interaction.response.send_message("Вы открыли комнату")
        conn.commit()
        conn.close()

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔐")
    async def button_ban_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите пользователя которому хотите убрать доступ")

        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        member = disnake.utils.get(interaction.guild.members, id=member_id)
        print(member)
        overwrite = disnake.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.view_channel = True
        overwrite.connect = False
        await self.voice_channel.set_permissions(member, overwrite=overwrite)
        await member.move_to(None)

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔑")
    async def button_unban_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите пользователя которому хотите дать доступ")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        member = disnake.utils.get(interaction.guild.members, id=member_id)
        overwrite = disnake.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.view_channel = True
        overwrite.connect = True
        await self.voice_channel.set_permissions(member, overwrite=overwrite)


    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="⚰️")
    async def button_kick_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите пользователя которого хотите кикнуть")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        member = disnake.utils.get(interaction.guild.members, id=member_id)
        await member.move_to(None)

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔈")
    async def button_mute_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите кого хотите замутить")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content
        
        member_id = int(msg_content[2:-1])
        member = disnake.utils.get(interaction.guild.members, id=member_id)
        overwrite = disnake.PermissionOverwrite()
        overwrite.speak = False
        await self.voice_channel.set_permissions(member, overwrite=overwrite)
        await member.move_to(self.voice_channel)


    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔊")
    async def button_unmute_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите кого хотите размутить")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        member = disnake.utils.get(interaction.guild.members, id=member_id)
        overwrite = disnake.PermissionOverwrite()
        overwrite.speak = True
        await self.voice_channel.set_permissions(member, overwrite=overwrite)
        await member.move_to(self.voice_channel)


    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="👑")
    async def button_new_author(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите нового владельца комнаты")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author, timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content
        
        member_id = int(msg_content[2:-1])
        member = disnake.utils.get(interaction.guild.members, id=member_id)

        conn = sqlite3.connect('database/private.db')
        curs = conn.cursor()
        curs.execute("UPDATE room SET authorid = ? WHERE room_id = ?", (member.id, self.voice_channel.id))
        await self.voice_channel.send(f"Новый владелец комнаты {member.mention}")
        conn.commit()
        conn.close()
def setup(bot):
    bot.add_cog(PrivateRoom(bot))
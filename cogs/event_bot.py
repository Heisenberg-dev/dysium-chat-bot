import datetime
import os
from enum import Enum
import disnake

from disnake.ext import commands, tasks
from disnake import TextInputStyle

import dysium

import sqlite3

class Prize(str, Enum):
    Winner = "Переможець"
    Player = "Учасник"

class EventBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot




    @commands.slash_command(name="event_create", description="Створити новий івент")
    async def event_create(self, ctx):
        print(f"member:{ctx.author} func: /event_create")
        # Create the view containing our dropdown
        status = "Active"
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        event = curs.execute("SELECT * FROM event WHERE authorid = ? AND status = ?",
                                          (ctx.author.id, status)).fetchone()
        conn.commit()
        conn.close()
        if event == None or event[6] =="Deactive":
            view = EventsPanel(self.bot,ctx.author)
            message = await ctx.send("Оберіть потрібний івент:", view=view)
            view.message = message
        elif event[6] == "Active":
            await ctx.send("Завершіть старий івент, щоб почати новий")
        # Sending a message containing our view

    @commands.slash_command(name="all_event_close", description="Видалити не завершенний івент у ведучого")
    async def all_event_close(self, ctx, member: disnake.Member):
        print(f"member:{ctx.author} func: /all_event_close")
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        event = curs.execute("SELECT * FROM event WHERE authorid = ? AND status = ?",
                             (member.id, "Active")).fetchone()

        if event == None:
            await ctx.send(f"Нема активних івентів у ведущого {member}")

        else:
            category = disnake.utils.get(ctx.guild.categories, name=f"{event[2]}  ・  {ctx.author.display_name}")
            curs.execute("UPDATE event SET status = ? WHERE authorid = ?", ("Deactive", member.id,))
            await ctx.send(f"Івент {event[2]} ведущого {member.mention} був завершенний")

            for channel in category.voice_channels:
                await channel.delete()

            for channel in category.text_channels:
                await channel.delete()

            await category.delete()

        conn.commit()
        conn.close()

    @commands.slash_command(name="prize", description="Видати винагороду за івент")
    async def prize(self, ctx, target: Prize, member: disnake.Member):
        print(f"member:{ctx.author} func: /prize")
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        event = curs.execute("SELECT * FROM event WHERE authorid = ? AND status = ?",
                             (ctx.author.id, "Active")).fetchone()

        if event == None:
            await ctx.send("Неможливо видати винагороду за завершенний івент")
            conn.commit()
            conn.close()
        else:
            conn.commit()
            conn.close()
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            user_data = curs.execute("SELECT * FROM users WHERE userid = ?",
                                     (member.id,)).fetchone()

            if target == "Учасник":
                prize = 75
                new_balance = user_data[5] + prize

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (new_balance, member.id,))

                await ctx.send(f" Ведучий {ctx.author} нагородив {member} за участь в івенті {event[2]}")
                conn.commit()
                conn.close()
            elif target == "Переможець":
                prize = 125
                new_balance = user_data[5] + prize

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (new_balance, member.id,))

                await ctx.send(f" Ведучий {ctx.author.display_name} нагородив {member.display_name} за перемогу в івенті {event[2]}")
                conn.commit()
                conn.close()


class EventsSelect(disnake.ui.Select):
    def __init__(self, bot, author):
        self.bot = bot
        self.author = author

        options = [
            disnake.SelectOption(
                label="Мафія", description="Створити івент: Мафія",
            ),
            disnake.SelectOption(
                label="Крокодил", description="Створити івент: Крокодил",
            ),
            disnake.SelectOption(
                label="Бункер", description="Створити івент: Бункер",
            ),
            disnake.SelectOption(
                label="Монополія", description="Створити івент: Монополія",
            ),
            disnake.SelectOption(
                label="Цитадель", description="Створити івент: Цитадель",
            ),
            disnake.SelectOption(
                label="CodeNames", description="Створити івент: CodeNames",
            ),
            disnake.SelectOption(
                label="Хто я", description="Створити івент: Хто я",
            ),
            disnake.SelectOption(
                label="Казки на нічь", description="Створити івент: Казки на нічь",
            ),
            disnake.SelectOption(
                label="Література", description="Створити івент: Література",
            ),
            disnake.SelectOption(
                label="Караоке", description="Створити івент: Караоке",
            ),
            disnake.SelectOption(
                label="Нульовий івент", description="Створити нульовий івент",
            ),
        ]

        super().__init__(
            placeholder="Оберіть потрібний івент",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.message.delete()
        await inter.guild.create_category(f"{self.values[0]}  ・  {inter.author.display_name}", position= 8)

        category = disnake.utils.get(inter.guild.categories, name=f"{self.values[0]}  ・  {inter.author.display_name}")
        category_id = category.id
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        curs.execute("INSERT INTO event VALUES(NULL,?,?,?,?,?,?,?)",
                                           (inter.author.id, self.values[0], 8, True, True,"Active", category_id))
        conn.commit()
        conn.close()

        text_channel = await inter.guild.create_text_channel(f"📌・Керування", category=category, )
        chat_channel = await inter.guild.create_text_channel(f"💬・Чат", category=category)
        voice_channel = await inter.guild.create_voice_channel(f"🟢・Івент", category=category)
        await inter.send(
            f" {disnake.utils.get(inter.guild.roles, id=731099776585826355).mention} Почато новий івент {self.values[0]}")

        await text_channel.send(f">>> Керівник івенту: {inter.author.mention}\n"
                                f" Кнопки управления комнатой: "
                                 f"\n 🧑‍🤝‍🧑 - установить лимит команты "
                                 f"\n 🔒 - закрыть комнату для всех "
                                 f"\n 🔓 - открыть комнату для всех "
                                 f"\n 🔐 - забрать доступ к комнате у пользователя "
                                 f"\n 🔑 - выдать доступ к комнате пользователю "
                                 f"\n ⚰️ - выгнать пользователя из комнаты"
                                 f"\n 🔈 - забрать право говорить у пользователя"
                                 f"\n 🔊 - вернуть право говорить пользователю"
                                 f"\n 👑 - сделать пользователя новым владельцем комнаты "
                                 f"\n ❌ - закончить ивент",
                                 view = EventManage(self.bot, self.author,text_channel,chat_channel,voice_channel, category))
class EventsPanel(disnake.ui.View):
    message: disnake.Message

    def __init__(self,bot,author):
        super().__init__()

        # Add the dropdown to our view object.
        self.add_item(EventsSelect(bot,author))
        self.bot = bot
        self.author = author

    async def interaction_check(self, interaction: disnake.ApplicationCommandInteraction) -> bool:
        if interaction.author.id != self.author.id:
            return await interaction.response.send_message(
                "Ви не можете керувати даними кнопками!", ephemeral=True
            )
        return True
    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

class EventManage(disnake.ui.View):
    message: disnake.Message

    def __init__(self, bot, author,text_channel,chat_channel,voice_channel,category):
        super().__init__(timeout=999999)
        self.bot = bot
        self.value = None
        self.author = author
        self.text_channel = text_channel
        self.chat_channel = chat_channel
        self.voice_channel = voice_channel
        self.category = category

    async def on_timeout(self):
        for button in self.children:
            button.disabled = False
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: disnake.ApplicationCommandInteraction) -> bool:
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        event = curs.execute("SELECT * FROM event WHERE event_id = ?",
                            (self.category.id,)).fetchone()
        conn.commit()
        conn.close()
        member = disnake.utils.get(interaction.guild.members, id=event[1])
        if interaction.author.id != member.id:
            return await interaction.response.send_message(
                "Ви не можете керувати даними кнопками!", ephemeral=True
            )
        return True


    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🧑‍🤝‍🧑")
    async def button_check_count(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишіть бажаему кількість місць")

        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author,
                                      timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content
        await self.voice_channel.edit(user_limit=int(msg_content))
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        curs.execute("UPDATE event SET count_people = ? WHERE authorid = ? AND status = ?",
                     (int(msg_content), interaction.author.id, "Active"))

        await interaction.edit_original_message(f"Кількість учасників у кімнаті змінено на {int(msg_content)}")
        conn.commit()
        conn.close()

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔒")
    async def button_room_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        role = disnake.utils.get(interaction.guild.roles, id=731099776585826355)
        await self.voice_channel.set_permissions(role, connect=False)
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        curs.execute("UPDATE event SET lock_room = ? WHERE authorid = ? AND status = ?",
                     (False, interaction.author.id, self.voice_channel.id))
        await interaction.response.send_message("Вы закрыли комнату")
        conn.commit()
        conn.close()

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔓")
    async def button_room_open(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        role = disnake.utils.get(interaction.guild.roles, id=731099776585826355)
        await self.voice_channel.set_permissions(role, connect=True)
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        curs.execute("UPDATE event SET lock_room = ? WHERE authorid = ? AND status = ?",
                     (True, interaction.author.id,  "Active"))
        await interaction.response.send_message("Вы открыли комнату")
        conn.commit()
        conn.close()

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔐")
    async def button_ban_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите пользователя которому хотите убрать доступ")

        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author,
                                      timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        room_member = disnake.utils.get(interaction.guild.members, id=member_id)

        overwrite = disnake.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.view_channel = True
        overwrite.connect = False
        await self.voice_channel.set_permissions(room_member, overwrite=overwrite)

        members = self.voice_channel.members
        for member in members:
            if member.id == room_member.id:
                await room_member.move_to(None)

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔑")
    async def button_unban_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите пользователя которому хотите дать доступ")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author,
                                      timeout=60.0)
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
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author,
                                      timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        room_member = disnake.utils.get(interaction.guild.members, id=member_id)
        members = self.voice_channel.members
        for member in members:
            if member.id == room_member.id:
                await room_member.move_to(None)

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔈")
    async def button_mute_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите кого хотите замутить")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author,
                                      timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        room_member = disnake.utils.get(interaction.guild.members, id=member_id)
        overwrite = disnake.PermissionOverwrite()
        overwrite.speak = False
        await self.voice_channel.set_permissions(room_member, overwrite=overwrite)
        members = self.voice_channel.members
        for member in members:
            if member.id == room_member.id:
                await member.move_to(self.voice_channel)

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="🔊")
    async def button_unmute_member(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите кого хотите размутить")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author,
                                      timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        room_member = disnake.utils.get(interaction.guild.members, id=member_id)
        overwrite = disnake.PermissionOverwrite()
        overwrite.speak = True
        await self.voice_channel.set_permissions(room_member, overwrite=overwrite)
        members = self.voice_channel.members
        for member in members:
            if member.id == room_member.id:
                await member.move_to(self.voice_channel)

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="👑")
    async def button_new_author(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Напишите нового владельца комнаты")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == interaction.author,
                                      timeout=60.0)
        await self.bot.process_commands(msg)
        msg_content = msg.content

        member_id = int(msg_content[2:-1])
        member = disnake.utils.get(interaction.guild.members, id=member_id)

        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        curs.execute("UPDATE event SET authorid = ? WHERE status = ?", (member.id, "Active"))
        await self.text_channel.send(f"Новый владелец комнаты {member.mention}")
        conn.commit()
        conn.close()

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji="❌")
    async def button_delete_event(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/event.db')
        curs = conn.cursor()
        event = curs.execute("SELECT * FROM event WHERE authorid = ? AND status = ?",
                             (interaction.author.id, "Active")).fetchone()
        curs.execute("UPDATE event SET status = ? WHERE authorid = ?", ("Deactive", interaction.author.id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Івент {event[2]} було завершено")

        for channel in self.category.voice_channels:
            await channel.delete()

        for channel in self.category.text_channels:
            await channel.delete()

        await self.category.delete()

def setup(bot):
    bot.add_cog(EventBot(bot))
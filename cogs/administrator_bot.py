import datetime
import os
import asyncio
import disnake

from disnake.ext import commands, tasks
from disnake import TextInputStyle

import dysium

import sqlite3

class AdministatorBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="action", description="Список команд для Адміністрації")
    async def action(self, ctx, member: disnake.Member):
        print(f"member:{ctx.author} func: /action")
        if member and member.top_role.position > ctx.author.top_role.position:
            return await ctx.send(f"Ви не маєте достатньо прав для дій над користувачем {member}")
        support_role = disnake.utils.get(ctx.guild.roles, id=dysium.SUPPORT_ROLE_ID)
        control_role = disnake.utils.get(ctx.guild.roles, id=dysium.CONTROL_ROLE_ID)
        moderator_role = disnake.utils.get(ctx.guild.roles, id=dysium.MODERATOR_ROLE_ID)
        curator_role = disnake.utils.get(ctx.guild.roles, id=dysium.CURATOR_ROLE_ID)

        curator_moderator_role = disnake.utils.get(ctx.guild.roles, id=dysium.CURATOR_MODERATOR_ROLE_ID)
        curator_control_role = disnake.utils.get(ctx.guild.roles, id=dysium.CURATOR_CONTROL_ROLE_ID)
        curator_support_role = disnake.utils.get(ctx.guild.roles, id=dysium.CURATOR_SUPPORT_ROLE_ID)



        if support_role in ctx.author.roles:
            view = Support(self.bot, ctx.author, member)
            message = await ctx.send(f'Виберіть дію над користувачем {member.mention}', view=view)
            view.message = message

        elif control_role in ctx.author.roles:
            view = Control(self.bot, ctx.author, member)
            message = await ctx.send(f'Виберіть дію над користувачем {member.mention}', view=view)
            view.message = message

        elif moderator_role in ctx.author.roles:
            view = Moderator(self.bot, ctx.author, member)
            message = await ctx.send(f'Виберіть дію над користувачем {member.mention}', view=view)
            view.message = message
        elif curator_moderator_role in ctx.author.roles:
            view = CuratorModerator(self.bot, ctx.author, member)
            message = await ctx.send(f'Виберіть дію над користувачем {member.mention}', view=view)
            view.message = message
        elif curator_control_role in ctx.author.roles:
            view = CuratorControl(self.bot, ctx.author, member)
            message = await ctx.send(f'Виберіть дію над користувачем {member.mention}', view=view)
            view.message = message
        elif curator_support_role in ctx.author.roles:
            view = CuratorSupport(self.bot, ctx.author, member)
            message = await ctx.send(f'Виберіть дію над користувачем {member.mention}', view=view)
            view.message = message

class Support(disnake.ui.View):
    message: disnake.Message

    def __init__(self, bot, author, member):
        super().__init__(timeout=30.0)
        self.value = None
        self.bot = bot
        self.author = author
        self.member = member

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

    @disnake.ui.button(label='Верифікувати', style=disnake.ButtonStyle.blurple)
    async def button_verify(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.stop()
        await interaction.response.send_message(f"Верифікація {self.member.mention} успішна")
        unverify_role = interaction.guild.get_role(dysium.UNVERIFY_ID)
        girl_role = interaction.guild.get_role(dysium.GIRL_ROLE_ID)
        man_role = interaction.guild.get_role(dysium.MAN_ROLE_ID)
        await self.member.remove_roles(unverify_role)
        await self.member.add_roles(man_role)
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE userid = ?", self.member.id)
        data_s = curs.fetchone()
        conn.commit()
        conn.close()
        if data_s == None:
            if girl_role in self.member.roles:

                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)",
                             (self.member.id, self.member, "Вільна", "♀", 0))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:

                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)", (self.member.id, self.member.mention, "Вільний", "♂", 0,))
                conn.commit()
                conn.close()



    @disnake.ui.button(label='Змінити стать', style=disnake.ButtonStyle.blurple)
    async def button_change_gender(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):

        await interaction.response.send_message(f"Стать {self.member.mention} була змінена")
        girl_role = interaction.guild.get_role(dysium.GIRL_ROLE_ID)
        man_role = interaction.guild.get_role(dysium.MAN_ROLE_ID)
        if girl_role in self.member.roles:
            await self.member.add_roles(man_role)
            await self.member.remove_roles(girl_role)
        elif man_role in self.member.roles:
            await self.member.add_roles(girl_role)
            await self.member.remove_roles(man_role)
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE userid = ?", (self.member.id,))
        data_s = curs.fetchone()
        conn.commit()
        conn.close()
        if data_s == None:  # если чела нет в бд
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO users VALUES(?, ?, ?)", (self.member.id, 0, 0))
            conn.commit()
            conn.close()
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", self.member.id,))
                conn.commit()
                conn.close()

        else:
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", self.member.id,))
                conn.commit()
                conn.close()

    @disnake.ui.button(label="Заблокувати", style=disnake.ButtonStyle.grey)
    async def button_block(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        block_role = self.member.guild.get_role(dysium.BLOCK_ID)
        await self.member.add_roles(block_role)
        await interaction.response.send_message(f"Учасник {self.member.mention} був заблокований")

class Control(disnake.ui.View):
    message: disnake.Message

    def __init__(self, bot, author, member):
        super().__init__(timeout=30.0)
        self.bot = bot
        self.value = None
        self.author = author
        self.member = member

    async def interaction_check(self, interaction: disnake.ApplicationCommandInteraction) -> bool:
        if interaction.author.id != self.author.id:
            return await interaction.response.send_message(
                "Вы не можете управлять этими кнопками!", ephemeral=True
            )
        return True

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

    @disnake.ui.button(label='Застереження', style=disnake.ButtonStyle.blurple)
    async def button_warn(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalWarn(self.member, self.author))

    @disnake.ui.button(label="Зняти застереження", style=disnake.ButtonStyle.grey)
    async def button_unwarn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        warn_role = self.member.guild.get_role(dysium.WARN_ROLE_ID)
        await self.member.remove_roles(warn_role)
        await interaction.response.send_message(f"Користувач {self.member.mention} позбавлений застереження")

    @disnake.ui.button(label='Чат мут', style=disnake.ButtonStyle.blurple)
    async def button_chat_mute(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalChatMute(self.member, self.author))

    @disnake.ui.button(label="Зняти чат мут", style=disnake.ButtonStyle.grey)
    async def button_chat_unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        chat_mute_role = self.member.guild.get_role(dysium.MUTE_ROLE_ID)
        await self.member.remove_roles(chat_mute_role)
        status = "Active"
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        curs.execute("UPDATE chat_mutes SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Користувач {self.member.mention} позбавлений чат муту")

    @disnake.ui.button(label="Історія чат мутів", style=disnake.ButtonStyle.grey)
    async def button_mute_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        chat_mutes_mutes1 = curs.execute("SELECT * FROM chat_mutes WHERE userid = ?", (self.member.id,)).fetchall()
        conn.commit()
        conn.close()
        chat_mutes = ""
        count = 0
        for m in range(len(chat_mutes_mutes1)):
            admin = self.bot.get_user(chat_mutes_mutes1[count][3])
            chat_mutes += f" №{count + 1} \n \n**Адміністратор:** {admin}    \n**Час муту:** {chat_mutes_mutes1[count][5]}   \n**Статус:** {chat_mutes_mutes1[count][7]} \n**Опис:** {chat_mutes_mutes1[count][2]}   \n**Дата муту:** {chat_mutes_mutes1[count][4]}\n \n"
            count += 1
        chat_embed_mute = disnake.Embed(title=f"Історія чат мутів користувача: {self.member}:", description=chat_mutes,
                                        colour=disnake.Color.purple())
        await interaction.response.send_message(embed=chat_embed_mute)

class Moderator(disnake.ui.View):
    message: disnake.Message

    def __init__(self,bot, author, member):
        super().__init__(timeout=60.0)
        self.value = None
        self.bot = bot
        self.author = author
        self.member = member

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

    @disnake.ui.button(label='Змінити стать', style=disnake.ButtonStyle.blurple)
    async def button_change_gender(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):


        girl_role = interaction.guild.get_role(dysium.GIRL_ROLE_ID)
        man_role = interaction.guild.get_role(dysium.MAN_ROLE_ID)
        if girl_role in self.member.roles:
            await self.member.add_roles(man_role)
            await self.member.remove_roles(girl_role)
        elif man_role in self.member.roles:
            await self.member.add_roles(girl_role)
            await self.member.remove_roles(man_role)

        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE userid = ?", (self.member.id,))
        data_s = curs.fetchone()
        conn.commit()
        conn.close()
        if data_s == None:  # если чела нет в бд
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO users VALUES(?, ?, ?)", (self.member.id, 0, 0))
            conn.commit()
            conn.close()
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", self.member.id,))
                conn.commit()
                conn.close()

        else:
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
        await interaction.response.send_message(f"Стать {self.member.mention} було змінено")

    @disnake.ui.button(label="Заблокувати", style=disnake.ButtonStyle.blurple)
    async def button_ban(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        ban_role = self.member.guild.get_role(dysium.BAN_ROLE_ID)
        await self.member.add_roles(ban_role)
        await interaction.response.send_message(f"Користувача {self.member.mention} було заблоковано")

    @disnake.ui.button(label="Розблокувати", style=disnake.ButtonStyle.grey)
    async def button_unban(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        ban_role = self.member.guild.get_role(dysium.BAN_ROLE_ID)
        await self.member.remove_roles(ban_role)
        await interaction.response.send_message(f"Користувача {self.member.mention} було разбанено")

    @disnake.ui.button(label='Застереження', style=disnake.ButtonStyle.blurple)
    async def button_warn(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalWarn(self.member, self.author))

    @disnake.ui.button(label="Зняти застереження", style=disnake.ButtonStyle.grey)
    async def button_unwarn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        warn_role = self.member.guild.get_role(dysium.WARN_ROLE_ID)
        await self.member.remove_roles(warn_role)
        status = "Active"
        conn = sqlite3.connect('database/warns.db')
        curs = conn.cursor()
        curs.execute("UPDATE warns SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Користувач {self.member.mention} позбавлений застереження")

    @disnake.ui.button(label='Дати голосовий мут', style=disnake.ButtonStyle.blurple)
    async def button_voice_mute(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalVoiceMute(self.member, self.author))

    @disnake.ui.button(label="Зняти голосовий мут", style=disnake.ButtonStyle.grey)
    async def button_voice_unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        voice_mute_role = self.member.guild.get_role(dysium.VOICE_MUTE_ROLE_ID)
        await self.member.remove_roles(voice_mute_role)
        status = "Active"
        conn = sqlite3.connect('database/voice_mutes.db')
        curs = conn.cursor()
        curs.execute("UPDATE voice_mutes SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Користувач {self.member.mention} був розмучений у голосових каналах")

    @disnake.ui.button(label="Історія голосових мутів", style=disnake.ButtonStyle.grey)
    async def button_voice_mute_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/voice_mutes.db')
        curs = conn.cursor()
        voice_mutes1 = curs.execute("SELECT * FROM voice_mutes WHERE userid = ?", (self.member.id,)).fetchall()
        conn.commit()
        conn.close()
        voice_mutes = ""
        count = 0
        for m in range(len(voice_mutes1)):
            admin = self.bot.get_user(voice_mutes1[count][3])
            voice_mutes += f" №{count + 1} \n \n**Адміністратор:** {admin}    \n**Чат муту:** {voice_mutes1[count][5]}   \n**Статус:** {voice_mutes1[count][7]} \n**Опис:** {voice_mutes1[count][2]}   \n**Дата муту:** {voice_mutes1[count][4]}\n \n"
            count += 1
        emb = disnake.Embed(title=f"Історія голосових мутів користувача: {self.member}:", description=voice_mutes,
                            colour=disnake.Color.purple())
        await interaction.response.send_message(embed=emb)

    @disnake.ui.button(label='Дати чат мут', style=disnake.ButtonStyle.blurple)
    async def button_chat_mute(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalChatMute(self.member, self.author))

    @disnake.ui.button(label="Зняти мут у чаті", style=disnake.ButtonStyle.grey)
    async def button_chat_unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        chat_mute_role = self.member.guild.get_role(dysium.MUTE_ROLE_ID)
        await self.member.remove_roles(chat_mute_role)
        status = "Active"
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        curs.execute("UPDATE chat_mutes SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Користувач {self.member.mention} був размучений у чаті")

    @disnake.ui.button(label="Історія чат мутів", style=disnake.ButtonStyle.grey)
    async def button_chat_mute_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        chat_mutes_mutes1 = curs.execute("SELECT * FROM chat_mutes WHERE userid = ?", (self.member.id,)).fetchall()
        conn.commit()
        conn.close()
        chat_mutes = ""
        count = 0
        for m in range(len(chat_mutes_mutes1)):
            admin = self.bot.get_user(chat_mutes_mutes1[count][3])
            chat_mutes += f" №{count + 1} \n \n**Адміністратор:** {admin}    \n**Час муту:** {chat_mutes_mutes1[count][5]}   \n**Статус:** {chat_mutes_mutes1[count][7]} \n**Опис:** {chat_mutes_mutes1[count][2]}   \n**Дата муту:** {chat_mutes_mutes1[count][4]}\n \n"
            count += 1
        chat_embed_mute = disnake.Embed(title=f"Історія чат мутів користувача: {self.member}:", description=chat_mutes,
                                        colour=disnake.Color.purple())
        await interaction.response.send_message(embed=chat_embed_mute)

class CuratorModerator(disnake.ui.View):
    message: disnake.Message

    def __init__(self,bot, author, member):
        super().__init__(timeout=60.0)
        self.value = None
        self.bot = bot
        self.author = author
        self.member = member

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

    @disnake.ui.button(label='Змінити стать', style=disnake.ButtonStyle.blurple)
    async def button_change_gender(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):


        girl_role = interaction.guild.get_role(dysium.GIRL_ROLE_ID)
        man_role = interaction.guild.get_role(dysium.MAN_ROLE_ID)
        if girl_role in self.member.roles:
            await self.member.add_roles(man_role)
            await self.member.remove_roles(girl_role)
        elif man_role in self.member.roles:
            await self.member.add_roles(girl_role)
            await self.member.remove_roles(man_role)

        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE userid = ?", (self.member.id,))
        data_s = curs.fetchone()
        conn.commit()
        conn.close()
        if data_s == None:  # если чела нет в бд
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO users VALUES(?, ?, ?)", (self.member.id, 0, 0))
            conn.commit()
            conn.close()
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", self.member.id,))
                conn.commit()
                conn.close()

        else:
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", self.member.id,))
                conn.commit()
                conn.close()
        await interaction.response.send_message(f"Стать {self.member.mention} було змінено")

    @disnake.ui.button(label="Заблокувати", style=disnake.ButtonStyle.blurple)
    async def button_ban(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        ban_role = self.member.guild.get_role(dysium.BAN_ROLE_ID)
        await self.member.add_roles(ban_role)
        await interaction.response.send_message(f"Користувач {self.member.mention} був заблокований")

    @disnake.ui.button(label="Розблокувати", style=disnake.ButtonStyle.grey)
    async def button_unban(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        ban_role = self.member.guild.get_role(dysium.BAN_ROLE_ID)
        await self.member.remove_roles(ban_role)
        await interaction.response.send_message(f"Користувач {self.member.mention} був розблокований ")

    @disnake.ui.button(label='Застереження', style=disnake.ButtonStyle.blurple)
    async def button_warn(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalWarn(self.member, self.author))

    @disnake.ui.button(label="Зняти застереження", style=disnake.ButtonStyle.grey)
    async def button_unwarn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        warn_role = self.member.guild.get_role(dysium.WARN_ROLE_ID)
        await self.member.remove_roles(warn_role)
        status = "Active"
        conn = sqlite3.connect('database/warns.db')
        curs = conn.cursor()
        curs.execute("UPDATE warns SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Користувач {self.member.mention} був позбавлений застереження")

    @disnake.ui.button(label='Дати голосовий мут', style=disnake.ButtonStyle.blurple)
    async def button_voice_mute(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalVoiceMute(self.member, self.author))

    @disnake.ui.button(label="Зняти голосовий мут", style=disnake.ButtonStyle.grey)
    async def button_voice_unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        voice_mute_role = self.member.guild.get_role(dysium.VOICE_MUTE_ROLE_ID)
        await self.member.remove_roles(voice_mute_role)
        status = "Active"
        conn = sqlite3.connect('database/voice_mutes.db')
        curs = conn.cursor()
        curs.execute("UPDATE voice_mutes SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Користувача {self.member.mention} було розмучено")

    @disnake.ui.button(label="Історія голосових мутів", style=disnake.ButtonStyle.grey)
    async def button_voice_mute_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/voice_mutes.db')
        curs = conn.cursor()
        voice_mutes1 = curs.execute("SELECT * FROM voice_mutes WHERE userid = ?", (self.member.id,)).fetchall()
        conn.commit()
        conn.close()
        voice_mutes = ""
        count = 0
        for m in range(len(voice_mutes1)):
            admin = self.bot.get_user(voice_mutes1[count][3])
            voice_mutes += f" №{count + 1} \n \n**Адміністратор:** {admin}    \n**Час муту:** {voice_mutes1[count][5]}   \n**Статус:** {voice_mutes1[count][7]} \n**Опис:** {voice_mutes1[count][2]}   \n**Дата муту:** {voice_mutes1[count][4]}\n \n"
            count += 1
        emb = disnake.Embed(title=f"Історія голосових мутів користувача: {self.member}:", description=voice_mutes,
                            colour=disnake.Color.purple())
        await interaction.response.send_message(embed=emb)

    @disnake.ui.button(label='Дати чат мут', style=disnake.ButtonStyle.blurple)
    async def button_chat_mute(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalChatMute(self.member, self.author))

    @disnake.ui.button(label="Зняти чат мут", style=disnake.ButtonStyle.grey)
    async def button_chat_unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        chat_mute_role = self.member.guild.get_role(dysium.MUTE_ROLE_ID)
        await self.member.remove_roles(chat_mute_role)
        status = "Active"
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        curs.execute("UPDATE chat_mutes SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"Користувач {self.member.mention} позбавлений муту у чаті")

    @disnake.ui.button(label="Історія чат мутів", style=disnake.ButtonStyle.grey)
    async def button_chat_mute_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        chat_mutes_mutes1 = curs.execute("SELECT * FROM chat_mutes WHERE userid = ?", (self.member.id,)).fetchall()
        conn.commit()
        conn.close()
        chat_mutes = ""
        count = 0
        for m in range(len(chat_mutes_mutes1)):
            admin = self.bot.get_user(chat_mutes_mutes1[count][3])
            chat_mutes += f" №{count + 1} \n \n**Адміністратор:** {admin}    \n**Час муту:** {chat_mutes_mutes1[count][5]}   \n**Статус:** {chat_mutes_mutes1[count][7]} \n**Опис:** {chat_mutes_mutes1[count][2]}   \n**Дата муту:** {chat_mutes_mutes1[count][4]}\n \n"
            count += 1
        chat_embed_mute = disnake.Embed(title=f"Історія чат мутів користувача: {self.member}:", description=chat_mutes,
                                        colour=disnake.Color.purple())
        await interaction.response.send_message(embed=chat_embed_mute)

    @disnake.ui.button(label="Список модераторів", style=disnake.ButtonStyle.grey)
    async def button_moderator_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        moderator_list = curs.execute("SELECT * FROM moderator").fetchall()
        conn.commit()
        conn.close()
        moderators = ""
        count = 0

        for m in range(len(moderator_list)):
            admin = self.bot.get_user(moderator_list[count][1])
            moderators += f" №{count + 1} \n " \
                          f"\n**Користувач:** ```{admin}```    " \
                          f"\n**Стаф баланс:** ```{moderator_list[count][2]}```   " \
                          f"\n**Дата становлення:** {moderator_list[count][3]}\n \n"
            count += 1
        embed_mod_list = disnake.Embed(title=f"Список модераторів:", description=moderators,
                                        colour=disnake.Color.purple())
        await interaction.response.send_message(embed=embed_mod_list)

    @disnake.ui.button(label="Додати модератора", style=disnake.ButtonStyle.grey)
    async def button_add_modrator(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        current = datetime.datetime.now()
        add_time = f"{current.year}-{current.month}-{current.day} {current.hour}:{current.minute}"
        moderator_role = disnake.utils.get(interaction.guild.roles, id=dysium.MODERATOR_ROLE_ID)
        staff_role = disnake.utils.get(interaction.guild.roles, id=dysium.STAFF_ROLE_ID)
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        curs.execute("INSERT INTO moderator VALUES(NULL,?,?,?,?,?,?,?)", (self.member.id, 100, add_time, 0, 0, 0, 0,))
        conn.commit()
        conn.close()
        await self.member.add_roles(staff_role)
        await self.member.add_roles(moderator_role)
        await interaction.send(f"Новий модератор {self.member.mention} починає роботу")

    @disnake.ui.button(label="Звільнити модератора", style=disnake.ButtonStyle.grey)
    async def button_remove_moderator(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        moderator_role = disnake.utils.get(interaction.guild.roles, id=dysium.MODERATOR_ROLE_ID)
        staff_role = disnake.utils.get(interaction.guild.roles, id=dysium.STAFF_ROLE_ID)
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        curs.execute("DELETE FROM moderator WHERE userid=?", (self.member.id,))
        conn.commit()
        conn.close()
        await self.member.remove_roles(moderator_role)
        await self.member.remove_roles(staff_role)
        await interaction.send(f"Модератора {self.member.mention} було звільнено")

class CuratorControl(disnake.ui.View):
    message: disnake.Message

    def __init__(self, bot, author, member):
        super().__init__(timeout=30.0)
        self.bot = bot
        self.value = None
        self.author = author
        self.member = member

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

    @disnake.ui.button(label='Застереження', style=disnake.ButtonStyle.blurple)
    async def button_warn(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalWarn(self.member, self.author))

    @disnake.ui.button(label="Зняти застереження", style=disnake.ButtonStyle.grey)
    async def button_unwarn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        warn_role = self.member.guild.get_role(dysium.WARN_ROLE_ID)
        await self.member.remove_roles(warn_role)
        await interaction.response.send_message(f"Користувач {self.member.mention} був позбавлений застереження")

    @disnake.ui.button(label='Дати чат мут', style=disnake.ButtonStyle.blurple)
    async def button_chat_mute(self, button: disnake.ui.Button, inter: disnake.AppCmdInter):

        await inter.response.send_modal(modal=ModalChatMute(self.member, self.author))

    @disnake.ui.button(label="Зняти чат мут", style=disnake.ButtonStyle.grey)
    async def button_chat_unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        chat_mute_role = self.member.guild.get_role(dysium.MUTE_ROLE_ID)
        await self.member.remove_roles(chat_mute_role)
        status = "Active"
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        curs.execute("UPDATE chat_mutes SET status = ? WHERE userid = ? AND status = ?",
                     ("Deactive", self.member.id, status))
        conn.commit()
        conn.close()

    @disnake.ui.button(label="Історія чат мутів", style=disnake.ButtonStyle.grey)
    async def button_mute_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/chat_mutes.db')
        curs = conn.cursor()
        chat_mutes_mutes1 = curs.execute("SELECT * FROM chat_mutes WHERE userid = ?", (self.member.id,)).fetchall()
        conn.commit()
        conn.close()
        chat_mutes = ""
        count = 0
        for m in range(len(chat_mutes_mutes1)):
            admin = self.bot.get_user(chat_mutes_mutes1[count][3])
            chat_mutes += f" №{count + 1} \n \n**Адміністратор:** {admin}    \n**Час муту:** {chat_mutes_mutes1[count][5]}   \n**Статус:** {chat_mutes_mutes1[count][7]} \n**Опис:** {chat_mutes_mutes1[count][2]}   \n**Дата муту:** {chat_mutes_mutes1[count][4]}\n \n"
            count += 1
        chat_embed_mute = disnake.Embed(title=f"Історія чат мутів користувача: {self.member}:", description=chat_mutes,
                                        colour=disnake.Color.purple())
        await interaction.response.send_message(embed=chat_embed_mute)

    @disnake.ui.button(label="Список редакторів", style=disnake.ButtonStyle.grey)
    async def button_control_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        control_list = curs.execute("SELECT * FROM control").fetchall()
        conn.commit()
        conn.close()
        controls = ""
        count = 0

        for m in range(len(control_list)):
            admin = self.bot.get_user(control_list[count][1])
            controls += f" №{count + 1} \n " \
                          f"\n**Користувач:** ```{admin}```    " \
                          f"\n**Стаф баланс:** ```{control_list[count][2]}```   " \
                          f"\n**Дата становлення:** {control_list[count][3]}\n \n"
            count += 1
        embed_mod_list = disnake.Embed(title=f"Список редакторів:", description=controls,
                                       colour=disnake.Color.purple())
        await interaction.response.send_message(embed=embed_mod_list)

    @disnake.ui.button(label="Додати редактора", style=disnake.ButtonStyle.grey)
    async def button_add_control(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        current = datetime.datetime.now()
        add_time = f"{current.year}-{current.month}-{current.day} {current.hour}:{current.minute}"
        control_role = disnake.utils.get(interaction.guild.roles, id=dysium.CONTROL_ROLE_ID)
        staff_role = disnake.utils.get(interaction.guild.roles, id=dysium.STAFF_ROLE_ID)
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        curs.execute("INSERT INTO control VALUES(NULL,?,?,?,?,?,?)", (self.member.id, 100, add_time, 0, 0, 0,))
        conn.commit()
        conn.close()
        await self.member.add_roles(staff_role)
        await self.member.add_roles(control_role)
        await interaction.send(f"Новий редактор {self.member.mention} почав роботу")

    @disnake.ui.button(label="Звільнити редактора", style=disnake.ButtonStyle.grey)
    async def button_remove_control(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        control_role = disnake.utils.get(interaction.guild.roles, id=dysium.CONTROL_ROLE_ID)
        staff_role = disnake.utils.get(interaction.guild.roles, id=dysium.STAFF_ROLE_ID)
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        curs.execute("DELETE FROM control WHERE userid=?", (self.member.id,))
        conn.commit()
        conn.close()
        await self.member.remove_roles(control_role)
        await self.member.remove_roles(staff_role)
        await interaction.send(f"Редактора {self.member.mention} було звільнено")

class CuratorSupport(disnake.ui.View):
    message: disnake.Message

    def __init__(self, bot, author, member):
        super().__init__(timeout=30.0)
        self.value = None
        self.bot = bot
        self.author = author
        self.member = member

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

    @disnake.ui.button(label='Верифікувати', style=disnake.ButtonStyle.blurple)
    async def button_verify(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.stop()
        await interaction.response.send_message(f"Верифікація {self.member.mention} успішна")
        unverify_role = interaction.guild.get_role(dysium.UNVERIFY_ID)
        girl_role = interaction.guild.get_role(dysium.GIRL_ROLE_ID)
        man_role = interaction.guild.get_role(dysium.MAN_ROLE_ID)
        await self.member.remove_roles(unverify_role)
        await self.member.add_roles(man_role)
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE userid = ?", self.member.id)
        data_s = curs.fetchone()
        conn.commit()
        conn.close()
        if data_s == None:
            if girl_role in self.member.roles:

                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)",
                             (self.member.id, self.member, "Вільна", "♀", 0))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:

                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)", (self.member.id, self.member.mention, "Вільний", "♂", 0,))
                conn.commit()
                conn.close()



    @disnake.ui.button(label='Змінити стать', style=disnake.ButtonStyle.blurple)
    async def button_change_gender(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):

        await interaction.response.send_message(f"Стать {self.member.mention} змінено")
        girl_role = interaction.guild.get_role(dysium.GIRL_ROLE_ID)
        man_role = interaction.guild.get_role(dysium.MAN_ROLE_ID)
        if girl_role in self.member.roles:
            await self.member.add_roles(man_role)
            await self.member.remove_roles(girl_role)
        elif man_role in self.member.roles:
            await self.member.add_roles(girl_role)
            await self.member.remove_roles(man_role)
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE userid = ?", (self.member.id,))
        data_s = curs.fetchone()
        conn.commit()
        conn.close()
        if data_s == None:  # если чела нет в бд
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO users VALUES(?, ?, ?)", (self.member.id, 0, 0))
            conn.commit()
            conn.close()
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", self.member.id,))
                conn.commit()
                conn.close()

        else:
            if girl_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", self.member.id,))
                conn.commit()
                conn.close()
            elif man_role in self.member.roles:
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", self.member.id,))
                curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", self.member.id,))
                conn.commit()
                conn.close()

    @disnake.ui.button(label="Заблокувати", style=disnake.ButtonStyle.grey)
    async def button_block(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        block_role = self.member.guild.get_role(dysium.BLOCK_ID)
        await self.member.add_roles(block_role)
        await interaction.response.send_message(f"Користувача {self.member.mention} заблоковано")

    @disnake.ui.button(label="Список охоронців", style=disnake.ButtonStyle.grey)
    async def button_support_list(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        support_list = curs.execute("SELECT * FROM support").fetchall()
        conn.commit()
        conn.close()
        supports = ""
        count = 0

        for m in range(len(support_list)):
            admin = self.bot.get_user(support_list[count][1])
            supports += f" №{count + 1} \n " \
                          f"\n**Користувач:** ```{admin}```    " \
                          f"\n**Стаф баланс:** ```{support_list[count][2]}```   " \
                          f"\n**Дата становлення:** {support_list[count][3]}\n \n"
            count += 1
        embed_mod_list = disnake.Embed(title=f"Список охоронців:", description=supports,
                                       colour=disnake.Color.purple())
        await interaction.response.send_message(embed=embed_mod_list)

    @disnake.ui.button(label="Додати охоронця", style=disnake.ButtonStyle.grey)
    async def button_add_support(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        current = datetime.datetime.now()
        add_time = f"{current.year}-{current.month}-{current.day} {current.hour}:{current.minute}"
        support_role = disnake.utils.get(interaction.guild.roles, id=dysium.SUPPORT_ROLE_ID)
        staff_role = disnake.utils.get(interaction.guild.roles, id=dysium.STAFF_ROLE_ID)
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        curs.execute("INSERT INTO support VALUES(NULL,?,?,?,?)", (self.member.id, 100, add_time, 0,))
        conn.commit()
        conn.close()
        await self.member.add_roles(staff_role)
        await self.member.add_roles(support_role)
        await interaction.send(f"Новий охоронець {self.member.mention} почав роботу")

    @disnake.ui.button(label="Звільнити охоронця", style=disnake.ButtonStyle.grey)
    async def button_remove_support(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        support_role = disnake.utils.get(interaction.guild.roles, id=dysium.SUPPORT_ROLE_ID)
        staff_role = disnake.utils.get(interaction.guild.roles, id=dysium.STAFF_ROLE_ID)
        conn = sqlite3.connect('database/staff.db')
        curs = conn.cursor()
        curs.execute("DELETE FROM support WHERE userid=?", (self.member.id,))
        conn.commit()
        conn.close()
        await self.member.remove_roles(support_role)
        await self.member.remove_roles(staff_role)
        await interaction.send(f"Охоронець {self.member.mention} був звільнений")

class ModalWarn(disnake.ui.Modal):
    def __init__(self, member, author):
        # The details of the modal, and its components
        self.member = member
        self.author = author
        components = [
            disnake.ui.TextInput(
                label="Опис порушення",
                placeholder="Опис порушення",
                custom_id="description",
                style=TextInputStyle.paragraph,
                max_length=70,
            ),
        ]
        super().__init__(
            title="Видати застереження",
            custom_id="create_warn",
            timeout=300.0,
            components=components,
        )

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):

        embed = disnake.Embed(title="Видано застереження")
        for key, value in inter.text_values.items():
            embed.add_field(
                name="Користувач:",
                value=f"```{self.member}```",
                inline=True,
            )
            embed.add_field(
                name="Адміністратор:",
                value=f"```{self.author}```",
                inline=True,
            )
            embed.add_field(
                name=key.capitalize(),
                value=f"```{value}```",
                inline=False,
            )
            embed.set_thumbnail(url=self.member.avatar.url)

            warn_time = datetime.datetime.now()
            end_warn_time = warn_time + datetime.timedelta(weeks=1)
            conn = sqlite3.connect('database/warns.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO warns VALUES(NULL,?,?,?,?,?)",
                         (self.member.id, value[:1024], end_warn_time, self.author.id, "Active",))
            conn.commit()
            conn.close()
        warn_role = self.member.guild.get_role(dysium.WARN_ROLE_ID)
        await self.member.add_roles(warn_role)
        await inter.response.send_message(embed=embed)

class ModalChatMute(disnake.ui.Modal):
    def __init__(self, member, author):
        # The details of the modal, and its components
        self.member = member
        self.author = author

        components = [
            disnake.ui.TextInput(
                label="Правило",
                placeholder="Номер правила",
                custom_id="Правило",
                style=TextInputStyle.short,
                max_length=10,
            ),
            disnake.ui.TextInput(
                label="Час покарання",
                placeholder="час<m/h/d/w>",
                custom_id="Час покарання",
                style=TextInputStyle.short,
                max_length=10,
            ),
            disnake.ui.TextInput(
                label="Опис порушення",
                placeholder="Опис порушення",
                custom_id="Опис",
                style=TextInputStyle.paragraph,
                max_length=70,
            ),
        ]
        super().__init__(
            title="Видати чат мут",
            custom_id="create_chat_mute",
            timeout=300.0,
            components=components,
        )

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):

        embed_chat_mute = disnake.Embed(title="Видано чат мут")
        value_from_modal = []
        for key, value in inter.text_values.items():
            value_from_modal.append(value)

        embed_chat_mute.add_field(
            name="Користувач:",
            value=f"```{self.member}```",
            inline=True,
        )
        embed_chat_mute.add_field(
            name="Адміністратор:",
            value=f"```{self.author}```",
            inline=True,
        )
        embed_chat_mute.add_field(
            name="Правило",
            value=f"```{value_from_modal[0]}```",
            inline=False,
        )
        embed_chat_mute.add_field(
            name="Час покарання",
            value=f"```{value_from_modal[1]}```",
            inline=True,
        )
        embed_chat_mute.add_field(
            name="Опис",
            value=f"```{value_from_modal[2]}```",
            inline=False,
        )
        mute_time = value_from_modal[1]
        how_time = mute_time[-1]
        count_time = mute_time[:-1]

        if how_time == "s":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(seconds=int(count_time))
            conn = sqlite3.connect('database/chat_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO chat_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "m":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(minutes=int(count_time))
            conn = sqlite3.connect('database/chat_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO chat_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "h":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(hours=int(count_time))
            conn = sqlite3.connect('database/chat_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO chat_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "d":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(days=int(count_time))
            conn = sqlite3.connect('database/chat_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO chat_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "w":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(weeks=int(count_time))
            conn = sqlite3.connect('database/chat_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO chat_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()

        embed_chat_mute.set_thumbnail(url=self.member.avatar.url)
        chat_mute_role = self.member.guild.get_role(dysium.MUTE_ROLE_ID)
        await self.member.add_roles(chat_mute_role)
        await inter.response.send_message(embed=embed_chat_mute)

class ModalVoiceMute(disnake.ui.Modal):
    def __init__(self, member, author):
        # The details of the modal, and its components
        self.member = member
        self.author = author

        components = [
            disnake.ui.TextInput(
                label="Правило",
                placeholder="Номер правила",
                custom_id="Правило",
                style=TextInputStyle.short,
                max_length=10,
            ),
            disnake.ui.TextInput(
                label="Час покарання",
                placeholder="час<m/h/d/w>",
                custom_id="Час покарання",
                style=TextInputStyle.short,
                max_length=10,
            ),
            disnake.ui.TextInput(
                label="Опис порушення",
                placeholder="Опис порушення",
                custom_id="Описание",
                style=TextInputStyle.paragraph,
                max_length=70,
            ),
        ]
        super().__init__(
            title="Видати голосовий мут",
            custom_id="create_voice_mute",
            timeout=300.0,
            components=components,
        )

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):

        embed_voice_mute = disnake.Embed(title="Видано голосовий мут")
        value_from_modal = []
        for key, value in inter.text_values.items():
            value_from_modal.append(value)

        embed_voice_mute.add_field(
            name="Користувач:",
            value=f"```{self.member}```",
            inline=True,
        )
        embed_voice_mute.add_field(
            name="Адміністратор:",
            value=f"```{self.author}```",
            inline=True,
        )
        embed_voice_mute.add_field(
            name="Правило",
            value=f"```{value_from_modal[0]}```",
            inline=False,
        )
        embed_voice_mute.add_field(
            name="Час покарання",
            value=f"```{value_from_modal[1]}```",
            inline=True,
        )
        embed_voice_mute.add_field(
            name="Опис",
            value=f"```{value_from_modal[2]}```",
            inline=False,
        )
        mute_time = value_from_modal[1]
        how_time = mute_time[-1]
        count_time = mute_time[:-1]

        if how_time == "s":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(seconds=int(count_time))
            conn = sqlite3.connect('database/voice_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO voice_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "m":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(minutes=int(count_time))
            conn = sqlite3.connect('database/voice_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO voice_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "h":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(hours=int(count_time))
            conn = sqlite3.connect('database/voice_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO voice_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "d":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(days=int(count_time))
            conn = sqlite3.connect('database/voice_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO voice_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()
        if how_time == "w":
            start_mute_time = datetime.datetime.now()
            end_mute_time = start_mute_time + datetime.timedelta(weeks=int(count_time))
            conn = sqlite3.connect('database/voice_mutes.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO voice_mutes VALUES(NULL,?,?,?,?,?,?,?)",
                         (self.member.id, value_from_modal[2], self.author.id, start_mute_time, value_from_modal[1],
                          end_mute_time, "Active",))
            conn.commit()
            conn.close()

        embed_voice_mute.set_thumbnail(url=self.member.avatar.url)
        voice_mute_role = self.member.guild.get_role(dysium.VOICE_MUTE_ROLE_ID)
        await self.member.add_roles(voice_mute_role)
        await inter.response.send_message(embed=embed_voice_mute)



def setup(bot):
    bot.add_cog(AdministatorBot(bot))
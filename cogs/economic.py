import datetime
import os
from random import randint

import disnake

from disnake.ext import commands, tasks
from disnake import TextInputStyle

import dysium

import sqlite3



class Economic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="give", description="Видати валюту учаснику")
    async def give(self, ctx, user: disnake.User = commands.Param(description="учасник кому переказ коштів"), amount: int = commands.Param(description="Кількість монет")):
        print(f"member:{ctx.author} func: /give")
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE userid = ?", (ctx.author.id,))
        data_author = curs.fetchone()
        curs.execute("SELECT * FROM users WHERE userid = ?", (user.id,))
        data_member = curs.fetchone()

        member_balance = data_member[5]
        author_balance = data_author[5]
        conn.commit()

        if amount > author_balance:
            await ctx.send(f"У вас недостатньо монет")
        elif amount < 0:
            return
        elif data_author == data_member:
            await ctx.send(f"Ви не можете видати собі монети")
        else:
            member_balance += amount
            author_balance -= amount

            curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (author_balance, ctx.author.id,))
            curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (member_balance, user.id,))

            conn.commit()
            conn.close()

            await ctx.send(f"Учасник {ctx.author.mention} перевів {user.mention} {amount} монет")

    @commands.slash_command(name="clear_balance", description="Очистити баланс учасника")
    @commands.has_permissions(administrator=True)
    async def clear_balance(self, ctx, user: disnake.User):
        print(f"member:{ctx.author} func: /clear_balance")
        member_balance = 0

        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (member_balance, user.id,))
        conn.commit()
        conn.close()
        await ctx.send(f"Користувач {ctx.author.mention} позбавив {user.mention} усіх  монет")

    @commands.slash_command(name="dupe", description="Видати користувачу монети(тільки для адміністрації)")
    @commands.has_permissions(administrator=True)
    async def dupe(self, ctx, user: disnake.User, amount: int):
        print(f"member:{ctx.author} func: /dupe")
        if user == None:
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("SELECT * FROM users WHERE userid = ?", (ctx.author.id,))
            data_member = curs.fetchone()
            conn.commit()

            if amount > 0 and amount <= 15000:
                member_balance = data_member[5] + amount
                curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (member_balance, user.id,))
                conn.commit()
                conn.close()
                await ctx.send(f"Адміністратор {ctx.author.mention} перевів {ctx.author.mention} {amount}  монет")
            else:
                await ctx.send(f"Ви не можете видати {amount} монет")
        else:
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("SELECT * FROM users WHERE userid = ?", (user.id,))
            conn.commit()

            data_member = curs.fetchone()
            if amount > 0 and amount <= 15000:
                member_balance = data_member[5] + amount

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?", (member_balance, user.id,))
                conn.commit()
                conn.close()
                await ctx.send(f"Адміністратор {ctx.author.mention} перевів {user.mention} {amount}  монет")
            else:
                await ctx.send(f"Ви не можете видати {amount} монет")


    @commands.slash_command(name="balance", description="Подивитись баланс учасника")
    async def balance(self,ctx, user: disnake.User = None):
        print(f"member:{ctx.author} func: /balance")
        if user == None:
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("SELECT * FROM users WHERE userid = ?", (ctx.author.id,))
            data_s = curs.fetchone()
            conn.commit()
            conn.close()
            now_balance = data_s[5]
            emb_author_balance = disnake.Embed()
            emb_author_balance.add_field(name='**Ім\'я:**', value=data_s[2], inline=False)
            emb_author_balance.add_field(name='**Баланс:**', value=now_balance, inline=False)
            await ctx.send(embed=emb_author_balance)
        else:
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("SELECT * FROM users WHERE userid = ?", (user.id,))
            data_user = curs.fetchone()
            conn.commit()
            conn.close()
            now_balance = data_user[5]
            emb_user_balance = disnake.Embed()
            emb_user_balance.add_field(name='**Ім\'я:**', value=data_user[2], inline=False)
            emb_user_balance.add_field(name='**Баланс:**', value=now_balance, inline=False)
            await ctx.send(embed=emb_user_balance)

    @commands.slash_command(name="coin", description="Орел/решка - попитати свою вдачу та виграти серверні монети")
    async def coin(self, ctx):
        print(f"member:{ctx.author} func: /coin")
        random = randint(1, 10)

        view = Coin(ctx.author, random)
        message = await ctx.send(f'Виберіть сторону монети', view=view)
        view.message = message



class Coin(disnake.ui.View):
    message: disnake.Message

    def __init__(self, author, random):
        super().__init__(timeout=60.0)
        self.value = None
        self.author = author
        self.random = random


    async def interaction_check(self, interaction: disnake.ApplicationCommandInteraction) -> bool:
        if interaction.author.id != self.author.id:
            return await interaction.response.send_message(
                "Ви не можете керувати даними кнопками", ephemeral=True
            )
        return True

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

    @disnake.ui.button(label='Орел', style=disnake.ButtonStyle.blurple)
    async def button_eagle(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.button_eagle.disabled = True
        self.button_tail.disabled = True
        await inter.response.defer(ephemeral=True)
        tail = [1, 3, 5, 7, 9]
        eagle = [2, 4, 6, 8, 10]
        print(self.random)
        if self.random in eagle:
            embed_eagle = disnake.Embed(
                color=disnake.Colour.purple()
            )
            embed_eagle.set_image(url="https://media.discordapp.net/attachments/1012342781949259806/1078297023633178634/38858777b9965fac.gif")
            await inter.edit_original_message("Ви перемогли", embed = embed_eagle,view=None)
        elif self.random in tail:
            embed_tail = disnake.Embed(
                color=disnake.Colour.purple()
            )
            embed_tail.set_image(url="https://media.discordapp.net/attachments/1012342781949259806/1078297325916663858/c2eef9829663baed.gif")
            await inter.edit_original_message("Ви програли", embed=embed_tail, view=None)


    @disnake.ui.button(label='Решка', style=disnake.ButtonStyle.blurple)
    async def button_tail(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.button_eagle.disabled = True
        self.button_tail.disabled = True
        await inter.response.defer()
        tail = [1, 3, 5, 7, 9]
        eagle = [2, 4, 6, 8, 10]
        print(self.random)
        if self.random in eagle:
            embed_eagle = disnake.Embed(
                color=disnake.Colour.purple()
            )
            embed_eagle.set_image(url="https://media.discordapp.net/attachments/1012342781949259806/1078297023633178634/38858777b9965fac.gif")
            await inter.edit_original_message("Ви програли", embed = embed_eagle,view=None)
        elif self.random in tail:
            embed_tail = disnake.Embed(
                color=disnake.Colour.purple()
            )
            embed_tail.set_image(url="https://media.discordapp.net/attachments/1012342781949259806/1078297325916663858/c2eef9829663baed.gif")
            await inter.edit_original_message("Ви перемогли", embed=embed_tail, view=None)


def setup(bot):
    bot.add_cog(Economic(bot))
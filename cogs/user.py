import datetime
import os

import disnake

from disnake.ext import commands, tasks
from disnake import TextInputStyle

import config

import sqlite3




class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="profile", description="Подивитись профіль учасника")
    async def profile(self, ctx, member: disnake.Member = None):
        print(f"member:{ctx.author} func: /profile")
        if member == None:

            girl_role = ctx.guild.get_role(config.GIRL_ROLE_ID)
            man_role = ctx.guild.get_role(config.MAN_ROLE_ID)
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("SELECT * FROM users WHERE userid = ?", (ctx.author.id,))
            data_s = curs.fetchone()

            if data_s == None:
                if girl_role in ctx.author.roles:

                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)",
                                 (ctx.author.id, ctx.author.mention, "Вільна", "♀", 0))
                    conn.commit()

                elif man_role in ctx.author.roles:

                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)",
                                 (ctx.author.id, ctx.author.mention, "Вільний", "♂", 0,))
                    conn.commit()
                conn.close()
            else:

                if girl_role in ctx.author.roles:

                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", ctx.author.id,))
                    curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", ctx.author.id,))
                    conn.commit()
                elif man_role in ctx.author.roles:
                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", ctx.author.id,))
                    curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", ctx.author.id,))
                    conn.commit()
                conn.close()
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("SELECT * FROM users WHERE userid = ?", (ctx.author.id,))
                data_s = curs.fetchone()
                times_start = datetime.datetime.today()
                emb_profile = disnake.Embed(title=f'**Профіль учасника**')
                emb_profile.add_field(name='**Ім\'я:**', value= data_s[2], inline=False)
                emb_profile.add_field(name="Код користувача:", value=f"```{ctx.author.id}```", inline=False)
                emb_profile.add_field(name='**Статус:**', value=f"```{data_s[3]}```", inline=True)
                emb_profile.add_field(name='**Стать:**', value=f"```  {data_s[4]}```", inline=True)
                emb_profile.add_field(name='**Баланс:**', value=f"```{data_s[5]}```", inline=False)
                emb_profile.add_field(name='**Сервер:**', value=ctx.guild.name, inline=False)
                emb_profile.set_footer(text=f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
                emb_profile.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(embed=emb_profile)
                conn.close()
        else:
            girl_role = ctx.guild.get_role(config.GIRL_ROLE_ID)
            man_role = ctx.guild.get_role(config.MAN_ROLE_ID)
            conn = sqlite3.connect('database/users.db')
            curs = conn.cursor()
            curs.execute("SELECT * FROM users WHERE userid = ?", (member.id,))
            data_s = curs.fetchone()
            conn.commit()
            if data_s == None:
                if girl_role in member.roles:

                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)",
                                 (member.id, member.mention, "Вільна", "♀", 0))
                    conn.commit()

                elif man_role in member.roles:

                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("INSERT INTO users VALUES(NULL,?,?, ?, ?, ?)",
                                 (member.id, member.mention, "Вільний", "♂", 0,))
                    conn.commit()
                conn.close()
            else:
                if girl_role in member.roles:

                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♀", member.id,))
                    curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільна", member.id,))
                    conn.commit()

                elif man_role in member.roles:
                    conn = sqlite3.connect('database/users.db')
                    curs = conn.cursor()
                    curs.execute("UPDATE users SET status = ? WHERE userid = ?", ("Вільний", member.id,))
                    curs.execute("UPDATE users SET gender = ? WHERE userid = ?", ("♂", member.id,))
                    conn.commit()
                conn.close()
                conn = sqlite3.connect('database/users.db')
                curs = conn.cursor()
                curs.execute("SELECT * FROM users WHERE userid = ?", (member.id,))
                data_s = curs.fetchone()
                times_start = datetime.datetime.today()
                emb_user_profile = disnake.Embed(title=f'**Профіль учасника**')
                emb_user_profile.add_field(name='**Ім\'я:**', value=f"```{member}```", inline=False)
                emb_user_profile.add_field(name="Код користувача:", value=f"```{member.id}```", inline=False)
                emb_user_profile.add_field(name='**Статус:**', value=f"```{data_s[3]}```", inline=True)
                emb_user_profile.add_field(name='**Стать:**', value=f"```{data_s[4]}```", inline=True)
                emb_user_profile.add_field(name='**Баланс:**', value=f"```{data_s[5]}```", inline=False)
                emb_user_profile.add_field(name='**Сервер:**', value=ctx.guild.name, inline=False)
                emb_user_profile.set_thumbnail(url=member.avatar.url)
                emb_user_profile.set_footer(text=f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
                await ctx.send(embed=emb_user_profile)
                conn.close()


def setup(bot):
    bot.add_cog(User(bot))
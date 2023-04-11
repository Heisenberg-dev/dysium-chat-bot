from typing import List
import disnake
import datetime

from disnake.ext import commands
import sqlite3

conn = sqlite3.connect('database/roles.db')
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS roles(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	authorid INT,
	role_id INT,
	role_title VARCHAR,
    role_price INT,
    number INT);
""")
conn.commit()
conn.close()


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="create_role", description="Створити нову роль")
    async def create_role(self, ctx, title: str, price: int, color):
        role = disnake.utils.get(ctx.guild.roles, name=title)
        if role in ctx.guild.roles:
            await ctx.send(f"Роль {role.mention} вже існує")
        else:
            colour = disnake.Colour(int(f"0x{color[1:]}", 16))
            await ctx.guild.create_role(name=title, color=colour)
            new_role = disnake.utils.get(ctx.guild.roles, name=title)

            await ctx.author.add_roles(new_role)
            conn = sqlite3.connect('database/roles.db')
            curs = conn.cursor()
            curs.execute("INSERT INTO roles VALUES(NULL,?,?,?,?,?)",
                         [ctx.author.id, new_role.id, title, price, 0])
            conn.commit()
            conn.close()
            await ctx.send(f"Роль {new_role} була створена користувачем {ctx.author.display_name}")

    @commands.slash_command(name="shop", description="Купити нову роль")
    async def shop(self, ctx):
        # Creates the embeds as a list.
        conn = sqlite3.connect('database/roles.db')
        curs = conn.cursor()
        all_roles = curs.execute("SELECT * FROM roles").fetchall()

        conn.commit()
        shop_item = ''
        count = 0

        embeds = []
        for m in range(len(all_roles)):

            role_id = all_roles[count][2]
            role = disnake.utils.get(ctx.guild.roles, id=role_id)
            creator = self.bot.get_user(all_roles[count][1])
            conn = sqlite3.connect('database/roles.db')
            curs = conn.cursor()
            curs.execute("UPDATE roles SET number = ? WHERE role_id = ?",
                         (count + 1, role_id))
            conn.commit()
            conn.close()
            shop_item += f" №{count + 1} \n " \
                         f"\n**Роль:** {role.mention}   " \
                         f"\n**Ціна:** {all_roles[count][4]}   " \
                         f"\n**Ким створена:** {creator.mention}\n \n"
            count += 1

            if count % 5 == 0:
                embeds.append(disnake.Embed(
                    title="Магазин ролей",
                    description=shop_item,
                ))
                shop_item = ""

        if len(shop_item) != 0:
            embeds.append(disnake.Embed(
                title="Магазин ролей",
                description=shop_item,
            ))

        return await ctx.send(embed=embeds[0], view=Menu(embeds, count, ctx.author))

        # Sends first embed with the buttons, it also passes the embeds list into the View class.


class Menu(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed], count, author):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.index = 0
        self.count = count
        self.author = author


        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Сторінка {i + 1} of {len(self.embeds)}")


        self._update_state()

    async def interaction_check(self, interaction: disnake.ApplicationCommandInteraction) -> bool:
        if interaction.author.id != self.author.id:
            return await interaction.response.send_message(
                "Ви не можете керувати даними кнопками", ephemeral=True
            )
        return True

    def _update_state(self) -> None:

        self.first_item.disabled = False

        self.second_item.disabled = False

        self.third_item.disabled = False

        self.fourth_item.disabled = False

        self.fifth_item.disabled = False

        self.first_page.disabled = True
        self.prev_page.disabled = self.index == 0
        self.last_page.disabled = True
        self.next_page.disabled = self.index == len(self.embeds) - 1

        conn = sqlite3.connect('database/roles.db')
        curs = conn.cursor()
        all_roles = curs.execute("SELECT * FROM roles").fetchall()
        conn.commit()
        conn.close()
        _roles = []
        for role in self.author.roles:
            _roles.append(role.id)

        for m in range(len(all_roles)):
            count = m + 1
            conn = sqlite3.connect('database/roles.db')
            curs = conn.cursor()
            role_counter = curs.execute("SELECT * FROM roles WHERE number = ?", (count,)).fetchone()
            conn.commit()
            conn.close()
            roles_number = []
            if role_counter[2] in _roles:
                roles_number.append(role_counter[5])
                for added_role_number in roles_number:

                    if int(self.first_item.label) == added_role_number:
                        self.first_item.disabled = True
                        print(self.first_item.label)
                    if int(self.second_item.label) == added_role_number:
                        self.second_item.disabled = True
                        print(self.second_item.label)
                    if int(self.third_item.label) == added_role_number:
                        self.third_item.disabled = True
                        print(self.third_item.label)
                    if int(self.fourth_item.label) == added_role_number:
                        self.fourth_item.disabled = True
                        print(self.fourth_item.label)
                    if int(self.fifth_item.label) == added_role_number:
                        self.fifth_item.disabled = True
                        print(self.fifth_item.label)


    @disnake.ui.button(label="1", style=disnake.ButtonStyle.green)
    async def first_item(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        conn = sqlite3.connect('database/roles.db')
        curs = conn.cursor()
        role_counter = curs.execute("SELECT * FROM roles WHERE number = ?", (int(button.label),)).fetchone()
        conn.commit()
        conn.close()
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        author_info = curs.execute("SELECT * FROM users WHERE userid = ?", (inter.author.id,)).fetchone()
        conn.commit()

        role_id = role_counter[2]
        role = disnake.utils.get(inter.guild.roles, id=role_id)
        if role in self.author.roles:
            button.disabled = True
            await inter.response.edit_message("Ви вже маєте цю роль",
                                              view=Menu(self.embeds, self.count, self.author),
                                              embed=self.embeds[0])
        else:
            if role_counter[4] > author_info[5]:
                await inter.response.edit_message("Недостатньо коштів на рахунку",
                                                  view=Menu(self.embeds, self.count, self.author),
                                                  embed=self.embeds[0])
            if role_counter[4] < author_info[5]:
                new_balance = author_info[5] - role_counter[4]

                new_role = inter.author.guild.get_role(role_counter[2])

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?",
                             (new_balance, self.author.id,))
                conn.commit()
                conn.close()
                await inter.author.add_roles(new_role)

                await inter.response.edit_message(f"Ви купили роль {role.mention} за {role_counter[4]} монет",
                                                  view=None,
                                                  embed=None)

    @disnake.ui.button(label="2", style=disnake.ButtonStyle.green)
    async def second_item(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        conn = sqlite3.connect('database/roles.db')
        curs = conn.cursor()
        role_counter = curs.execute("SELECT * FROM roles WHERE number = ?", (int(button.label),)).fetchone()
        conn.commit()
        conn.close()
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        author_info = curs.execute("SELECT * FROM users WHERE userid = ?", (inter.author.id,)).fetchone()
        conn.commit()

        role_id = role_counter[2]
        role = disnake.utils.get(inter.guild.roles, id=role_id)
        if role in self.author.roles:
            await inter.response.edit_message("Ви вже маєте цю роль",
                                              view=Menu(self.embeds, self.count, self.author),
                                              embed=self.embeds[0])
        else:
            if role_counter[4] > author_info[5]:
                await inter.response.edit_message("Недостатньо коштів на рахунку",
                                                  view=Menu(self.embeds, self.count, self.author),
                                                  embed=self.embeds[0])
            if role_counter[4] < author_info[5]:
                new_balance = author_info[5] - role_counter[4]

                new_role = inter.author.guild.get_role(role_counter[2])

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?",
                             (new_balance, self.author.id,))
                conn.commit()
                conn.close()
                await inter.author.add_roles(new_role)

                await inter.response.edit_message(f"Ви купили роль {role.mention} за {role_counter[4]} монет",
                                                  view=None,
                                                  embed=None)

    @disnake.ui.button(label="3", style=disnake.ButtonStyle.green)
    async def third_item(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):

        conn = sqlite3.connect('database/roles.db')
        curs = conn.cursor()
        role_counter = curs.execute("SELECT * FROM roles WHERE number = ?", (int(button.label),)).fetchone()
        conn.commit()
        conn.close()
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        author_info = curs.execute("SELECT * FROM users WHERE userid = ?", (inter.author.id,)).fetchone()
        conn.commit()

        role_id = role_counter[2]
        role = disnake.utils.get(inter.guild.roles, id=role_id)
        if role in self.author.roles:
            await inter.response.edit_message("Ви вже маєте цю роль",
                                              view=Menu(self.embeds, self.count, self.author),
                                              embed=self.embeds[0])
        else:
            if role_counter[4] > author_info[5]:
                await inter.response.edit_message("Недостатньо коштів на рахунку",
                                                  view=Menu(self.embeds, self.count, self.author),
                                                  embed=self.embeds[0])
            if role_counter[4] < author_info[5]:
                new_balance = author_info[5] - role_counter[4]

                new_role = inter.author.guild.get_role(role_counter[2])

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?",
                             (new_balance, self.author.id,))
                conn.commit()
                conn.close()
                await inter.author.add_roles(new_role)

                await inter.response.edit_message(f"Ви купили роль {role.mention} за {role_counter[4]} монет",
                                                  view=None,
                                                  embed=None)

    @disnake.ui.button(label="4", style=disnake.ButtonStyle.green)
    async def fourth_item(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):

        conn = sqlite3.connect('database/roles.db')
        curs = conn.cursor()
        role_counter = curs.execute("SELECT * FROM roles WHERE number = ?", (int(button.label),)).fetchone()
        conn.commit()
        conn.close()
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        author_info = curs.execute("SELECT * FROM users WHERE userid = ?", (inter.author.id,)).fetchone()
        conn.commit()

        role_id = role_counter[2]
        role = disnake.utils.get(inter.guild.roles, id=role_id)
        if role in self.author.roles:
            await inter.response.edit_message("Ви вже маєте цю роль",
                                              view=Menu(self.embeds, self.count, self.author),
                                              embed=self.embeds[0])
        else:
            if role_counter[4] > author_info[5]:
                await inter.response.edit_message("Недостатньо коштів на рахунку",
                                                  view=Menu(self.embeds, self.count, self.author),
                                                  embed=self.embeds[0])
            if role_counter[4] < author_info[5]:
                new_balance = author_info[5] - role_counter[4]

                new_role = inter.author.guild.get_role(role_counter[2])

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?",
                             (new_balance, self.author.id,))
                conn.commit()
                conn.close()
                await inter.author.add_roles(new_role)

                await inter.response.edit_message(f"Ви купили роль {role.mention} за {role_counter[4]} монет",
                                                  view=None,
                                                  embed=None)

    @disnake.ui.button(label="5", style=disnake.ButtonStyle.green)
    async def fifth_item(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):

        conn = sqlite3.connect('database/roles.db')
        curs = conn.cursor()
        role_counter = curs.execute("SELECT * FROM roles WHERE number = ?", (int(button.label),)).fetchone()
        conn.commit()
        conn.close()
        conn = sqlite3.connect('database/users.db')
        curs = conn.cursor()
        author_info = curs.execute("SELECT * FROM users WHERE userid = ?", (inter.author.id,)).fetchone()
        conn.commit()

        role_id = role_counter[2]
        role = disnake.utils.get(inter.guild.roles, id=role_id)
        if role in self.author.roles:
            await inter.response.edit_message("Ви вже маєте цю роль",
                                              view=Menu(self.embeds, self.count, self.author),
                                              embed=self.embeds[0])
        else:
            if role_counter[4] > author_info[5]:
                await inter.response.edit_message("Недостатньо коштів на рахунку",
                                                  view=Menu(self.embeds, self.count,self.author),
                                                  embed=self.embeds[0])
            if role_counter[4] < author_info[5]:
                new_balance = author_info[5] - role_counter[4]

                new_role = inter.author.guild.get_role(role_counter[2])

                curs.execute("UPDATE users SET balance = ? WHERE userid = ?",
                             (new_balance, self.author.id,))
                conn.commit()
                conn.close()
                await inter.author.add_roles(new_role)

                await inter.response.edit_message(f"Ви купили роль {role.mention} за {role_counter[4]} монет", view=None,
                                                  embed=None)

    @disnake.ui.button(label="<--", style=disnake.ButtonStyle.blurple)
    async def first_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index = 0
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index -= 1

        self.first_item.label = str(int(self.first_item.label) - 5)
        self.second_item.label = str(int(self.second_item.label) - 5)
        self.third_item.label = str(int(self.third_item.label) - 5)
        self.fourth_item.label = str(int(self.fourth_item.label) - 5)
        self.fifth_item.label = str(int(self.fifth_item.label) - 5)

        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(view=None)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index += 1

        self.first_item.label = str(int(self.first_item.label) + 5)
        self.second_item.label = str(int(self.second_item.label) + 5)
        self.third_item.label = str(int(self.third_item.label) + 5)
        self.fourth_item.label = str(int(self.fourth_item.label) + 5)
        self.fifth_item.label = str(int(self.fifth_item.label) + 5)

        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="-->", style=disnake.ButtonStyle.blurple)
    async def last_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.index = len(self.embeds) - 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)





def setup(bot):
    bot.add_cog(Shop(bot))

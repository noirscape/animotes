import discord
from discord.ext import commands
import re
import sqlite3

#    Cog to reformat messages to allow for animated emotes, regardless of nitro status.
#    Copyright (C) 2017 Valentijn <ev1l0rd>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


class Animotes:
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('animotes.sqlite3')
        create_database(self.conn)
        self.conn.commit()

    async def on_message(self, message):
        if not message.author.bot and self.conn.cursor().execute('SELECT * FROM animotes WHERE user_id=?', (message.author.id,)).fetchone():
            channel = message.channel
            content = emote_corrector(self, message)
            if content:
                await message.delete()
                await channel.send(content=content)

    @commands.command(aliases=['unregister'])
    async def register(self, ctx):
        if self.conn.cursor().execute('SELECT * FROM animotes WHERE user_id=?', (ctx.author.id,)).fetchone():
            self.conn.cursor().execute('DELETE FROM animotes WHERE user_id=?', (ctx.author.id,))
            message = 'You sucessfully have been opted out of using animated emotes.'
        else:
            self.conn.cursor().execute('INSERT INTO animotes VALUES (?)', (ctx.author.id,))
            message = 'You sucessfully have been opted into using using animated emotes.'

        self.conn.commit()
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        await ctx.message.author.send(content=message)


def emote_corrector(self, message):
    '''Locate and change any emotes to emote objects'''
    r = re.compile(r':\w+:')
    _r = re.compile(r'<a:\w+:\w+>')
    if _r.search(message.content):
        return None
    found = r.findall(message.content)
    emotes = []
    for em in found:
        temp = discord.utils.get(self.bot.emojis, name=em[1:-1])
        try:
            if temp.animated:
                emotes.append((em, str(temp)))
        except AttributeError:
            pass  # We only care about catching this, not doing anything with it

    if emotes:
        temp = message.content
        for em in set(emotes):
            temp = temp.replace(*em)
    else:
        return None

    escape = re.compile(r':*<\w?:\w+:\w+>')
    # This escapes all colons that come before an emoji;
    # thanks to Discord shenanigans, this is needed.
    for esc in set(escape.findall(temp)):
        temp_esc = esc.split('<')
        esc_s = '{}<{}'.format(temp_esc[0].replace(':', '\:'), temp_esc[1])
        temp = temp.replace(esc, esc_s)

    temp = '**<{}>** '.format(message.author.name) + temp

    return temp


def setup(bot):
    bot.add_cog(Animotes(bot))


def create_database(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS animotes (
            user_id integer PRIMARY KEY
        );''')

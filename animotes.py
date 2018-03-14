import discord
from discord.ext import commands
import re
import sqlite3
import os
import mimetypes
import magic
import shutil
import tempfile

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
        self.conn = sqlite3.connect('databases/animotes.sqlite3')
        create_database(self.conn)
        self.conn.commit()
        try:
            self.bot.heroku_git_fs.update()
        except AttributeError as e:
            pass

    async def remove_original_message(self, message):
        try:
            await message.delete()
        except Exception:
            pass

    async def parse_attachments(self, message, temporary_dir):
        for i, attachment in enumerate(message.attachments):
            await attachment.save('{0}/{1}'.format(temporary_dir, i))

        for filename in os.listdir(temporary_dir):
            try:
                mimetype = magic.from_file('{0}/{1}'.format(temporary_dir, filename), mime=True)
                mimetype = mimetypes.guess_extension(mimetype)
                if mimetype:
                    os.rename(src='{0}/{1}'.format(temporary_dir, filename), dst='{0}/{1}{2}'.format(temporary_dir, filename, mimetype))
            except Exception as e:
                pass

        files = []
        for filename in os.listdir(temporary_dir):
            files.append(discord.File(os.path.abspath('{0}/{1}'.format(temporary_dir, filename))))
        return files

    async def on_message(self, message):
        if not message.author.bot and self.conn.cursor().execute('SELECT * FROM animotes WHERE user_id=?', (message.author.id,)).fetchone():
            channel = message.channel
            content = emote_corrector(self, message)
            if content:
                if message.attachments:
                    with tempfile.TemporaryDirectory() as temporary_dir:
                        files = await self.parse_attachments(message, temporary_dir)
                        await self.remove_original_message(message)
                        await channel.send(content=content, files=files)
                else:
                    await self.remove_original_message(message)
                    await channel.send(content=content)

    @commands.command(aliases=['unregister'])
    async def register(self, ctx):
        '''Register/Unregister from animated emotes.'''
        if self.conn.cursor().execute('SELECT * FROM animotes WHERE user_id=?', (ctx.author.id,)).fetchone():
            self.conn.cursor().execute('DELETE FROM animotes WHERE user_id=?', (ctx.author.id,))
            message = 'You sucessfully have been opted out of using animated emotes.'
        else:
            self.conn.cursor().execute('INSERT INTO animotes VALUES (?)', (ctx.author.id,))
            message = 'You sucessfully have been opted into using using animated emotes.'
        self.conn.commit()

        try:
            self.bot.heroku_git_fs.update()
        except AttributeError as e:
            pass

        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        await ctx.message.author.send(content=message)

    @commands.command()
    async def list_emotes(self, ctx):
        '''Lists all animated emotes the bot 'knows'.'''
        message = commands.Paginator(prefix='', suffix='')
        for guild in self.bot.guilds:
            emoji = guild.emojis
            if emoji:
                message.add_line(f'Emotes in guild __{guild.name}__:')
                for emoji in guild.emojis:
                    if emoji.animated:
                        message.add_line(f'**{emoji.name}**: {emoji}')
                message.add_line('')
        if not message:
            message.add_line('I\'m not in any guilds with emotes.')
            message.add_line('Try adding me to a guild with emotes.')

        for page in message.pages:
            await ctx.author.send(content=page)

    @commands.command()
    async def toggle_emoji(self, ctx):
        '''Block a specific emoji'''
        pass


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

    temp = '**<{}#{}>** '.format(message.author.name, message.author.discriminator) + temp

    return temp


def setup(bot):
    bot.add_cog(Animotes(bot))


def create_database(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS animotes (
            user_id integer PRIMARY KEY
        );''')

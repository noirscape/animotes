import discord

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

    async def on_message(self, message):
        if not message.author.bot:
            channel = message.channel
            content = emote_corrector(self, message)
            if content is not False:
                await message.delete()
                await channel.send(content=content)


def emote_corrector(self, message):
    '''Locate and change any emotes to emote objects'''
    content_list = message.content.split(":")
    new_content_list = []
    for potential_emote in range(0, len(content_list)):
        temp = discord.utils.get(self.bot.emojis, name=content_list[potential_emote])
        if type(temp) is discord.Emoji:
            if not temp.animated:
                return False
            else:
                new_content_list.append(temp)
        else:
            new_content_list.append(content_list[potential_emote])

    if all(type(contentpart) is not discord.Emoji for contentpart in new_content_list):
        return False

    new_content_list = [str(contentpart) for contentpart in new_content_list if contentpart is not None]

    new_content_list.insert(0, "**<{}>** ".format(message.author.display_name))

    return "".join(new_content_list)


def setup(bot):
    bot.add_cog(Animotes(bot))

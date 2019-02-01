import traceback

import discord
from discord.ext import commands

import Token
import bd_verification
import messages

bot = commands.Bot(command_prefix='f.',
                   description='The official bot of the Furry Hideout!',
                   pm_help=True,
                   command_not_found="Command not found")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("f.help"))
    print('Logged in as: {}'.format(bot.user.name))
    print('-----------------')


@bot.event
async def on_member_join(member):
    await member.send(messages.WELCOME_MESSAGE)


@bot.event
async def on_message(message):
    try:
        if not message.author.bot:
            if message.channel.name == "verification":
                log_channel = discord.utils.get(discord.utils.get(bot.guilds, name="bot fuck").channels, name='botlog')
                try:
                    bd_verification.verify_birthday(message.content)
                    await message.author.add_roles(discord.utils.get(message.guild.roles, name="verified"))
                    await message.delete()
                    await message.author.send(messages.USER_IS_VERIFIED)
                    await log_channel.send(messages.GIVEN_VERIFIED_TO_USER.format(message.author))
                except ValueError:
                    await message.channel.send(messages.INPUT_NOT_VALID.format("date"))
                except bd_verification.Underaged as e:
                    await message.author.send(e)
                    await log_channel.send(messages.USER_IS_UNDERAGED.format(
                        message))
                    await message.author.ban(reason=messages.USER_IS_UNDERAGED.format(
                        message.content))
    except AttributeError as e:
        e_mess = """```An error has occured:\n{}\n""".format(e.args)
        await message.channel.send(e_mess + traceback.format_tb(e.__traceback__)[0] + "```")


def main():
    try:
        token = Token.get_token()
        bot.run(token)
    except FileNotFoundError:
        print("Token not found")


if __name__ == '__main__':
    main()

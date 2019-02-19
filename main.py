import datetime
import os
import traceback

import discord
from discord.ext import commands

import Token
import bd_verification
import messages
import roles

bot = commands.Bot(command_prefix='!.',
                   description='The official bot of the Furry Hideout!',
                   command_not_found="Command not found",
                   max_message=100000)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!.help"))
    print('Logged in as: {}'.format(bot.user.name))
    print('-----------------')


@bot.event
async def on_member_join(member):
    await member.send(messages.WELCOME_MESSAGE)


async def create_invite_with_exc_msg(e, channel):
    il = await channel.create_invite(max_uses=1, max_age=86400, unique=True, reason="Needed to reinvite user")
    embed = discord.Embed(color=0xff0000)
    embed.add_field(name=e, value=il)
    return embed


@bot.event
async def on_message(message):
    if not message.author.bot:
        if message.attachments:
            await messages.save_attachments(message)
            message.content = "[Has attachment]" + message.content + "\n\tAttachments:\n\t\t"
            for a in message.attachments:
                message.content += str(a.url.split("/")[-1]) + " [ID: {}]\n\t\t".format(a.id)
        with open(Token.get_log_path(message), 'a+', encoding="utf-8") as file:
            file.seek(0, os.SEEK_END)
            if not file.tell():
                file.write(messages.USER_FILE_INFO.format(message.author))
            file.seek(0)
            file.write(messages.USER_NEW_MESSAGE_TO_LOG.format(message))

    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        log_channel = discord.utils.get(message.guild.text_channels, name="bot-log")
        file_channel = discord.utils.get(bot.guilds, name="zamirynth").text_channels[0]
        if log_channel:
            await messages.member_deleted_message(message, log_channel, file_channel)
        with open(Token.get_log_path(message), 'a+', encoding="utf-8") as file:
            file.seek(0, os.SEEK_END)
            if not file.tell():
                file.write(messages.USER_FILE_INFO.format(message.author))
            file.seek(0)
            file.write(messages.USER_MESSAGE_DELETED_TO_LOG.format(datetime.datetime.utcnow(), message))


@bot.event
async def on_message_edit(b, a):
    if not a.author.bot and b.content != a.content:
        log_channel = discord.utils.get(a.guild.text_channels, name="bot-log")
        if log_channel:
            await log_channel.send(embed=messages.member_edited_message(b, a))
        with open(Token.get_log_path(a), 'a+', encoding="utf-8") as file:
            file.seek(0, os.SEEK_END)
            if not file.tell():
                file.write(messages.USER_FILE_INFO.format(a.author))
            file.seek(0)
            file.write(messages.USER_MESSAGE_EDITED_TO_LOG.format(b, a))


@bot.command(pass_context=True)
@commands.has_role("Admin")
async def ban(ctx, user_id, reason):
    """
    Ban a user across all the guilds the bot is in
    :param user_id: the ID of the user to ban
    :param reason: the reason of the ban, must be between ""
    """
    int_user_id = int(user_id)
    user = bot.get_user(int_user_id)
    for guild in bot.guilds:
        log_channel = discord.utils.get(guild.text_channels, name="bot-log")
        if not log_channel:
            await guild.owner.send("I need a text channel called 'bot-log' in order to log my activities")
        else:
            await log_channel.send("Banning user '{0}' with reason '{1}'. The ban was put in place by {"
                                   "2.message.author.name} in the guild '{2.guild.name}'".format(user, reason, ctx))
        try:
            await guild.ban(user, reason=reason, delete_message_days=7)
        except Exception as e:
            print(e)


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have the permissions to use this command")
    else:
        await ctx.send(error.args)


@bot.command(pass_context=True)
async def verify(ctx, keyword, date_of_birth):
    """
    To verify yourself in the server
    :param keyword: The keyword found in the rules
    :param date_of_birth: pretty self explanatory ;3
    """
    try:
        if not ctx.message.author.bot:
            await ctx.message.delete()
            if keyword != "kitten":
                return await ctx.message.channel.send("That's the wrong key word, please go read the rules carefully")
            role = discord.utils.get(ctx.message.guild.roles, name="Verified")
            if not role:
                role = await create_role(ctx.message.guild, "Verified", discord.colour.Color.blue())
            if role not in ctx.message.author.roles:
                if ctx.message.channel.name == "verification":
                    log_channel = discord.utils.get(ctx.guild.channels,
                                                    name='bot-log')
                    if not log_channel:
                        await ctx.message.delete()
                        return await ctx.send("There is no channel called 'bot-log' in this server, please create one "
                                              "to use this functionality")
                    try:
                        bd_verification.verify_birthday(date_of_birth)
                        async with log_channel.typing():
                            await ctx.message.author.add_roles(role)
                            await ctx.message.author.send(messages.USER_IS_VERIFIED)
                            await log_channel.send(embed=messages.member_is_verified(ctx.message, date_of_birth))
                    except ValueError:
                        await ctx.message.channel.send(messages.INPUT_NOT_VALID.format("date"))
                    except bd_verification.Underaged as e:
                        await ctx.message.author.send(e)
                        await log_channel.send(embed=messages.member_is_underaged(ctx.message, date_of_birth))
                        await ctx.message.author.kick(reason=messages.USER_IS_UNDERAGED.format(
                            ctx.message))

    except AttributeError as e:
        e_mess = "```If you get this message, please send it to Raldryniorth the ferg#3621:\n{}\n".format(e.args)
        await ctx.message.channel.send(e_mess + traceback.format_tb(e.__traceback__)[0] + "```")
    except discord.errors.Forbidden:
        await ctx.message.channel.send("I cannot send you a DM {}, please ask a staff member to assist you with the "
                                       "verification process".format(ctx.message.author.mention))


@verify.error
async def verify_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments, please make sure you include all arguments in the command")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have the permissions required to do this. (missing: {})".format(error.missing_perms))


async def create_role(guild, name, color):
    return await guild.create_role(name=name,
                                   color=color,
                                   permissions=discord.Permissions(104188992),
                                   hoist=True,
                                   mentionable=True,
                                   reason="Role did not exist and was needed")


async def get_role_from_reaction(message, emoji):
    guild = message.channel.guild
    if message.content == """```md
Gender
------

1. Male
2. Female
3. Gender Fluid
4. Transgender

< To give yourself your desired role, select the corresponding emoji bellow > 
/* To remove a role you have, remove the corresponding reaction *```""":
        if emoji == '1⃣':
            r = discord.utils.get(guild.roles, name='Male')
            if not r:
                r = await create_role(guild, "Male", discord.Color.teal())
            return r
        elif emoji == '2⃣':
            r = discord.utils.get(guild.roles, name='Female')
            if not r:
                r = await create_role(guild, "Female", discord.Color(16727295))
            return r
        elif emoji == '3⃣':
            r = discord.utils.get(guild.roles, name='Gender Fluid')
            if not r:
                r = await create_role(guild, "Gender Fluid", discord.Color(13057084))
            return r
        elif emoji == '4⃣':
            r = discord.utils.get(guild.roles, name='Transgender')
            if not r:
                r = await create_role(guild, "Transgender", discord.Color(8978687))
            return r
        else:
            raise ValueError("Invalid reaction ID")

    elif message.content == """```md
Orientation
-----------

1.  Heterosexual
2.  Homosexual
3.  Bisexual
4.  Pansexual
5.  Demisexual

< To give yourself your desired role, select the corresponding emoji bellow >
/* To remove a role you have, remove the corresponding reaction *```""":
        if emoji == '1⃣':
            r = discord.utils.get(guild.roles, name='Heterosexual')
            if not r:
                r = await create_role(guild, "Heterosexual", discord.Color.blurple())
            return r
        elif emoji == '2⃣':
            r = discord.utils.get(guild.roles, name='Homosexual')
            if not r:
                r = await create_role(guild, "Homosexual", discord.Color.blurple())
            return r
        elif emoji == '3⃣':
            r = discord.utils.get(guild.roles, name='Bisexual')
            if not r:
                r = await create_role(guild, "Bisexual", discord.Color.blurple())
            return r
        elif emoji == '4⃣':
            r = discord.utils.get(guild.roles, name='Pansexual')
            if not r:
                r = await create_role(guild, "Pansexual", discord.Color.blurple())
            return r
        elif emoji == '5⃣':
            r = discord.utils.get(guild.roles, name='Demisexual')
            if not r:
                r = await create_role(guild, "Demisexual", discord.Color.blurple())
            return r
        else:
            raise ValueError("Invalid reaction ID")
    elif message.content == """```md
Preference
----------

1.  Dominant
2.  Submissive
3.  Switch

< To give yourself your desired role, select the corresponding emoji bellow > 
/* To remove a role you have, remove the corresponding reaction *```""":
        if emoji == '1⃣':
            r = discord.utils.get(guild.roles, name='Dominant')
            if not r:
                r = await create_role(guild, "Dominant", discord.Color.dark_red())
            return r
        elif emoji == '2⃣':
            r = discord.utils.get(guild.roles, name='Submissive')
            if not r:
                r = await create_role(guild, "Submissive", discord.Color.magenta())
            return r
        elif emoji == '3⃣':
            r = discord.utils.get(guild.roles, name='Switch')
            if not r:
                r = await create_role(guild, "Switch", discord.Color.purple())
            return r
        else:
            raise ValueError("Invalid reaction ID")
    else:
        raise ValueError("Invalid message ID")


@bot.event
async def on_raw_reaction_add(payload):
    if bot.get_channel(payload.channel_id).name == "get-roles":
        message = await bot.get_channel(payload.channel_id).get_message(payload.message_id)
        user = discord.utils.get(bot.get_all_members(), id=payload.user_id)
        if not user.bot:
            try:
                role = await get_role_from_reaction(message,
                                                    payload.emoji.name)
                if not role:
                    return await bot.get_channel(payload.channel_id).send(
                        "There was an error, please contact an admin")
                elif role in user.roles:
                    return await user.send("You already have that role, this should not be happening")
                elif roles.user_has_role_in_same_category(user, role):
                    await message.remove_reaction(payload.emoji, user)
                    return await user.send("You already have a role in that category, please remove it before assigning"
                                           " yourself a new one")
                else:
                    await user.add_roles(role)
            except Exception as e:
                e_mess = "```If you get this message, please send it to Raldryniorth the ferg#3621:\n{}\n".format(
                    e.args)
                return await message.channel.send(e_mess + traceback.format_tb(e.__traceback__) + "```")


@bot.event
async def on_raw_reaction_remove(payload):
    if bot.get_channel(payload.channel_id).name == "get-roles":
        message = await bot.get_channel(payload.channel_id).get_message(payload.message_id)
        user = discord.utils.get(bot.get_all_members(), id=payload.user_id)
        if not user.bot:
            try:
                role = await get_role_from_reaction(message,
                                                    payload.emoji.name)
                if not role:
                    return await bot.get_channel(payload.channel_id).send(
                        "There was an error (cant_get_role_from_react)")
                elif role not in user.roles:
                    return None
                else:
                    return await user.remove_roles(role)
            except Exception as e:
                e_mess = "```If you get this message, please send it to Raldryniorth the ferg#3621:\n{}\n".format(
                    e.args)
                return await message.channel.send(e_mess + traceback.format_tb(e.__traceback__) + "```")


def main():
    try:
        token = Token.get_token()
        bot.run(token)
    except FileNotFoundError:
        print("Token not found")


if __name__ == '__main__':
    main()

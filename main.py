import traceback

import discord
from discord.ext import commands

import Token
import bd_verification
import messages
import roles

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


async def create_invite_with_exc_msg(e, channel):
    il = await channel.create_invite(max_uses=1, max_age=86400, unique=True, reason="Needed to reinvite user")
    embed = discord.Embed(color=0xff0000)
    embed.add_field(name=e, value=il)
    return embed


@bot.event
async def on_message(message):
    try:
        if not message.author.bot:
            role = discord.utils.get(message.guild.roles, name="Verified")
            if message.channel.name == "verification":
                await message.delete()
                if role not in message.author.roles:
                    log_channel = discord.utils.get(
                        discord.utils.get(bot.guilds, name="Furry HideOut").channels,
                        name='bot-log')
                    try:
                        bd_verification.verify_birthday(message.content)
                        await message.author.add_roles(role)
                        await message.author.send(messages.USER_IS_VERIFIED)
                        await log_channel.send(messages.GIVEN_VERIFIED_TO_USER.format(message))
                    except ValueError:
                        await message.channel.send(messages.INPUT_NOT_VALID.format("date"))
                    except bd_verification.Underaged as e:
                        await message.author.send(embed=await create_invite_with_exc_msg(e, message.channel))
                        await message.channel.guild.kick(message.author,
                                                         reason=messages.USER_IS_UNDERAGED.format(message))
                        await log_channel.send(messages.USER_IS_UNDERAGED.format(
                            message))

    except Exception as e:
        e_mess = "```If you get this message, please send it to Raldryniorth the ferg#3621:\n{}\n".format(e.args)
        await message.channel.send(e_mess + traceback.format_tb(e.__traceback__) + "```")


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

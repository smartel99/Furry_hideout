from datetime import datetime

import discord
from discord.ext import commands

import Token
from services import data_service as svc

USER_IS_UNDERAGED = "User {0.author.name} entered a date less than 18 years ago ({0.content})"
USER_IS_VERIFIED = "You are now verified."
INPUT_NOT_VALID = "Input is not valid, please enter a '{}'"

WELCOME_MESSAGE = """Welcome to Furry HideOut!

Please check the rule channels (#rules), then follow the steps hidden somewhere in that channel.
If you get kicked after entering your date and think it is by mistake, just rejoin the server!
https://discord.gg/5xqjzdQ
Once you are verified, please use the #get-roles channel to set your basic roles.

Enjoy your stay in the Furry Hideout!"""

GIVEN_VERIFIED_TO_USER = "Given the verified role to user {0.name}. (birthday entered: {1})\n" \
                         "{0.name} joined discord on {0.created_at}"

USER_FILE_INFO = "Username: {0.name}, ID: {0.id}, joined the server: {0.joined_at}, created account: {0.created_at}\n"

USER_NEW_MESSAGE_TO_LOG = "[Created: {0.created_at}][Channel: {0.channel.name}][ID: {0.id}] {0.content}\n"

USER_MESSAGE_DELETED_TO_LOG = "[Deleted: {0}][Channel: {1.channel.name}][ID: {1.id}] {1.content}\n"

USER_MESSAGE_EDITED_TO_LOG = "[Edited: {1.edited_at}][Channel: {1.channel.name}][ID: {1.id}]\n" \
                             "  From: {0.content}\n" \
                             "  To:   {1.content}\n"

DEFAULT_WELCOME_MESSAGE = "Welcome to {}!"
ON_GUILD_JOIN_MESSAGE = """Hello there!
I'm Zamyrinth, your friendly helping dragon bot!
To view what I can do, use the command `!.help`!"""


def member_is_underaged(message, date_of_birth):
    em = discord.Embed(title="User is underaged",
                       description=message.author.name,
                       timestamp=datetime.now(),
                       colour=discord.Color.red())
    em.add_field(name="Birthday", value=date_of_birth)
    em.add_field(name="Joined Discord", value=message.author.created_at)
    em.set_thumbnail(url=message.author.avatar_url)
    return em


def member_is_verified(message: discord.Message, date_of_birth: str) -> discord.Embed:
    em = discord.Embed(title="Verified user",
                       description=message.author.name,
                       timestamp=datetime.now(),
                       colour=discord.Color.red())
    em.add_field(name="Birthday", value=date_of_birth)
    em.add_field(name="Joined Discord", value=message.author.created_at)
    em.set_thumbnail(url=message.author.avatar_url)
    return em


def member_edited_message(b, a):
    em = discord.Embed(title="Edited Message",
                       description="In channel {}".format(a.channel.name),
                       color=discord.Color.green())
    em.set_author(name=b.author.name, icon_url=b.author.avatar_url)
    em.add_field(name="From:", value=b.content, inline=False)
    em.add_field(name="To:", value=a.content, inline=False)
    em.timestamp = a.edited_at
    return em


async def send_files_to_file_channel(message, file_channel):
    al = []
    try:
        for a in message.attachments:
            al.append(discord.File(Token.get_attachment_file_path(message, a)))
        m = await file_channel.send(files=al)
        al = []
        for a in m.attachments:
            al.append(a.url)
    except Exception as e:
        print(e)
    return al


async def member_deleted_message(message: discord.Message,
                                 log_channel: discord.TextChannel,
                                 file_channel: discord.TextChannel):
    em = discord.Embed(title="Deleted Message",
                       description="In channel {}".format(message.channel.name),
                       color=discord.Color.blue())
    em.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    em.add_field(name="Message:", value=message.content, inline=False)
    em.timestamp = datetime.utcnow()
    if message.attachments:
        fl = await send_files_to_file_channel(message, file_channel)
        for m in fl:
            em.add_field(name=m.split("/")[-1], value=m)
    await log_channel.send(embed=em)


async def save_attachments(message):
    for a in message.attachments:
        await a.save(Token.get_attachment_file_path(message, a))


def format_updated_message(message):
    m = "Here is the new welcoming message for this guild!:\n```{}```".format(message)
    return m


def create_new_role(category, roles, guild: discord.Guild) -> str:
    message = f"```md\n{category}\n"
    for l in category:
        message += "-"
    message += "\n\n"

    for idx, role in enumerate(roles):
        r = discord.utils.get(guild.roles, name=role)
        if not r:
            return ""
        message += f"{idx + 1}.  {role}\n"
    # message += "\n< To give yourself your desired role, select the corresponding emoji bellow >"
    # message += "\n/* To remove a role you have, remove the corresponding reaction *```"
    return message


def create_settings_embed(ctx: discord.ext.commands.Context) -> discord.Embed:
    bot: commands.Bot = ctx.bot
    guild: discord.Guild = ctx.guild
    settings = svc.get_settings_for_guild(guild.id)
    user: discord.User = ctx.author
    try:
        log_channel = guild.get_channel(settings["log_channel"]).name if settings[
                                                                             "log_channel"] is not None else "No channel set "
    except KeyError:
        log_channel = "No channel set"
    try:
        verification_channel = guild.get_channel(settings["verification_channel"]).name if settings[
                                                                                               "verification_channel"] is not None else "No channel set "
    except KeyError:
        verification_channel = "No channel set"
    try:
        update_channel = guild.get_channel(settings["update_channel"]).name if settings[
                                                                                   "update_channel"] is not None else "No channel set"
    except KeyError:
        update_channel = "No channel set"
    try:
        verified_role = svc.get_verified_role_in_guild(guild).mention
    except AttributeError:
        verified_role = "No role set"

    welcome_message = settings["welcome_message"] if len(settings["welcome_message"]) <= 50 else settings[
                                                                                                     "welcome_message"][
                                                                                                 :49] + "..."

    em = discord.Embed(title=f"Settings in {ctx.guild.name}",
                       description=f"For {bot.user.name}",
                       colour=discord.Color.gold(),
                       url="https://github.com/smartel99/Furry_hideout")
    em.set_thumbnail(url=guild.icon_url)
    em.set_author(name=user.name, icon_url=user.avatar_url)
    em.set_footer(text=bot.user.name, icon_url=bot.user.avatar_url)

    em.add_field(name="Name of the server", value=settings["name"], inline=False)
    em.add_field(name="Welcome message", value=welcome_message, inline=False)
    em.add_field(name="Should welcome new members", value=settings["should_welcome_members"], inline=False)
    em.add_field(name="Log Channel", value=log_channel, inline=False)
    em.add_field(name="Should Log Deleted Messages", value=settings["should_show_deleted"], inline=False)
    em.add_field(name="Should Log Edited Messages", value=settings["should_show_edited"], inline=False)
    em.add_field(name="Should Log Joining Members", value=settings["should_show_joining"], inline=False)
    em.add_field(name="Should Log Leaving Members", value=settings["should_show_leaving"], inline=False)
    em.add_field(name="Verification Channel", value=verification_channel, inline=False)
    em.add_field(name="Verified Role", value=verified_role, inline=False)
    em.add_field(name="Should Verify Members", value=settings["should_verify"], inline=False)
    em.add_field(name="Requires Password", value=settings["password"] is None, inline=False)
    em.add_field(name="Should Save messages and files", value=settings["should_save_messages"], inline=False)
    em.add_field(name="Update Channel", value=update_channel, inline=False)

    return em


def create_member_joined_embed(member: discord.Member) -> discord.Embed:
    # """This creates an embed when a member joins"""
    em = discord.Embed(title="Someone joined the server!",
                       description=member.display_name,
                       color=discord.Color.purple(),
                       timestamp=datetime.now())
    em.set_thumbnail(url=member.avatar_url)
    return em


def create_member_left_embed(member: discord.Member) -> discord.Embed:
    em = discord.Embed(title="Someone left the server!",
                       description=member.display_name,
                       color=discord.Color.dark_purple(),
                       timestamp=datetime.now())
    em.set_thumbnail(url=member.avatar_url)
    return em

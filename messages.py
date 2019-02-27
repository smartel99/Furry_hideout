from datetime import datetime

import discord

import Token

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
            return None
        message += f"{idx + 1}.  {role}\n"
    message += "\n< To give yourself your desired role, select the corresponding emoji bellow >"
    message += "\n/* To remove a role you have, remove the corresponding reaction *```"
    return message

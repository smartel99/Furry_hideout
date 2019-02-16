from datetime import datetime

import discord

USER_IS_UNDERAGED = "User {0.author.name} entered a date less than 18 years ago ({0.content})"
USER_IS_VERIFIED = "You are now verified, please setup your roles in the #get_roles channel."
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


def member_is_underaged(message, date_of_birth):
    em = discord.Embed(title="User is underaged",
                       description=message.author.name,
                       timestamp=datetime.now(),
                       colour=discord.Color.red())
    em.add_field(name="Birthday", value=date_of_birth)
    em.add_field(name="Joined Discord", value=message.author.created_at)
    em.set_thumbnail(url=message.author.avatar_url)
    return em


def member_is_verified(message, date_of_birth):
    em = discord.Embed(title="Verified user",
                       description=message.author.name,
                       timestamp=datetime.now(),
                       colour=discord.Color.red())
    em.add_field(name="Birthday", value=date_of_birth)
    em.add_field(name="Joined Discord", value=message.author.created_at)
    em.set_thumbnail(url=message.author.avatar_url)
    return em

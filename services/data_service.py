import json

import discord
from discord.ext import commands

import messages
import reactions
from data.guilds import Guild
from data.roles import Role
from services import exceptions


def create_default_guild(guild: discord.Guild):
    g = get_guild(guild.id)

    if not g:
        g = Guild()
        g.name = guild.name
        g.guild_id = guild.id

        g.welcome_message = messages.DEFAULT_WELCOME_MESSAGE.format(guild.name)
        g.save()


def update_guild_welcome_message(guild: discord.Guild, message) -> str:
    g = Guild.objects().filter(guild_id=guild.id).first()
    if not g:
        create_default_guild(guild)
        r = update_guild_welcome_message(guild, messages)
        return r
    g.welcome_message = message
    g.save()

    return g.welcome_message


def get_welcome_message(g_id: int) -> str:
    g = get_guild(g_id)
    if not g:
        return ""
    return g.welcome_message


def update_should_welcome(g_id) -> bool:
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Couldn't update 'should_welcome'")
    g.should_welcome_members = not g.should_welcome_members
    g.save()
    return g.should_welcome_members


def should_welcome_in_guild(g_id) -> bool:
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        return False
    return g.should_welcome_members


def update_should_save_messages(g_id) -> bool:
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Couldn't update 'should_save_message'")
    g.should_save_messages = not g.should_save_messages
    g.save()
    return g.should_save_messages


def should_save_messages_in_guild(g_id) -> bool:
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        return False
    return g.should_save_messages


def update_log_channel_in_guild(g_id, c_id):
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Couldn't set the log channel")
    g.log_channel = c_id
    g.save()


def update_should_show_deleted(g_id) -> bool:
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Couldn't update 'should_show_deleted'")
    if not g.log_channel:
        raise exceptions.UpdateError("There is no log channel set yet.\n Use `!.slc` to assign a channel to logging")
    g.should_show_deleted = not g.should_show_deleted
    g.save()

    return g.should_show_deleted


def should_show_deleted_in_guild(g_id) -> bool:
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("An error has occured")
    if not g.log_channel:
        raise exceptions.UpdateError("There is no log channel set yet.\n Use `!.slc` to assign a channel to logging")
    return g.should_show_deleted


def update_verification_channel_in_guild(g_id, c_id):
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Couldn't set the verification channel")
    g.verification_channel = c_id
    g.save()


def get_log_channel_in_guild(guild: discord.Guild) -> discord.TextChannel:
    g = Guild.objects().filter(guild_id=guild.id).first()
    if not g:
        raise exceptions.UpdateError("An error has occured")
    if not g.log_channel:
        raise exceptions.UpdateError("There is no log channel set")

    c = guild.get_channel(g.log_channel)
    if not c:
        raise exceptions.UpdateError("Couldn't find the log channel")
    return c


def increment_message_saved(g_id: discord.Guild.id):
    Guild.objects(guild_id=g_id).update_one(inc__message_saved=1)


def increment_message_deleted(g_id: discord.Guild.id):
    Guild.objects(guild_id=g_id).update_one(inc__message_deleted=1)


def increment_message_edited(g_id: discord.Guild.id):
    Guild.objects(guild_id=g_id).update_one(inc__message_edited=1)


def should_show_edited_in_guild(g_id: discord.Guild.id) -> bool:
    g = get_guild(g_id)
    if not g:
        return False
    return g.should_show_edited


def should_verify(g_id: discord.Guild.id) -> bool:
    g = get_guild(g_id)
    if not g:
        return False
    return g.should_verify


def channel_is_verification(ctx: discord.ext.commands.Context) -> bool:
    return Guild.objects(guild_id=ctx.guild.id).first().verification_channel == ctx.channel.id


def get_verified_role_in_guild(guild: discord.Guild) -> discord.Role:
    g = Guild.objects(guild_id=guild.id).first()
    r = Role.objects(id__in=g.roles) \
        .filter(category="verify") \
        .first()

    return guild.get_role(r.role_id)


def get_guild(g_id):
    return Guild.objects().filter(guild_id=g_id).first()


def set_verified_role_in_guild(role: discord.Role):
    r = get_verified_role_in_guild(role.guild)

    if not r:
        r = Role()
        g = get_guild(role.guild.id)
    else:
        g = None

    r.name = role.name
    r.role_id = role.id
    r.category = "verify"

    r.save()

    if g:
        g.roles.append(r.id)
        g.save()

    return r


def get_password_in_guild(g_id) -> str:
    return Guild.objects(guild_id=g_id).first().password


def update_should_verify(g_id):
    g = Guild.objects(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Cannot update should_verify")
    g.should_verify = not g.should_verify
    g.save()
    return g.should_verify


def add_role_to_guild(m_id, role: discord.Role, category: str, idx: int):
    r = Role()
    r.name = role.name
    r.role_id = role.id
    r.message_id = m_id
    r.category = category
    r.reaction = reactions.REACTIONS[idx]

    r.save()

    g = get_guild(role.guild.id)
    g.roles.append(r.id)
    g.save()


def get_role_from_payload(payload: discord.RawReactionActionEvent, guild: discord.Guild) -> discord.Role:
    g = Guild.objects(guild_id=payload.guild_id).first()
    r = Role.objects(id__in=g.roles) \
        .filter(message_id=payload.message_id) \
        .filter(reaction=payload.emoji.name).first()
    if not r:
        return None
    return guild.get_role(r.role_id)


def set_password_for_guild(g_id, psswd):
    g = get_guild(g_id=g_id)
    g.password = psswd
    g.save()


def increment_retarded_user(g_id):
    Guild.objects(guild_id=g_id).update_one(inc__retarded_user=1)


def increment_verified_user(g_id):
    Guild.objects(guild_id=g_id).update_one(inc__verified_user=1)


def increment_underaged_user(g_id):
    Guild.objects(guild_id=g_id).update_one(inc__underaged_user=1)


def update_update_channel_in_guild(g_id, c_id):
    g = Guild.objects().filter(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Couldn't set the log channel")
    g.update_channel = c_id
    g.save()


def update_should_show_leaving(g_id) -> bool:
    g = Guild.objects(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Cannot update should_show_leaving")
    g.should_show_leaving = not g.should_show_leaving
    g.save()
    return g.should_show_leaving


def update_should_show_joining(g_id) -> bool:
    g = Guild.objects(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Cannot update should_show_joining")
    g.should_show_joining = not g.should_show_joining
    g.save()
    return g.should_show_joining


def update_should_show_edited(g_id) -> bool:
    g = Guild.objects(guild_id=g_id).first()
    if not g:
        raise exceptions.UpdateError("Cannot update should_show_edited")
    g.should_show_edited = not g.should_show_edited
    g.save()
    return g.should_show_edited


def get_settings_for_guild(g_id) -> dict:
    g = get_guild(g_id)
    settings = g.to_json()
    settings = json.loads(settings)
    return settings


def set_settings_to_default_in_guild(g_id):
    g = get_guild(g_id)
    if not g:
        raise exceptions.UpdateError("Cannot set the settings to the default values")
    g.should_verify = False
    g.should_show_deleted = False
    g.should_save_messages = False
    g.should_welcome_members = True
    g.should_show_edited = False
    g.should_show_joining = False
    g.should_show_leaving = False
    g.save()


def should_show_joining_in_guild(g_id):
    g = get_guild(g_id)
    if not g:
        return False
    return g.should_show_joining


def should_show_leaving(g_id):
    g = get_guild(g_id)
    if not g:
        return False
    return g.should_show_leaving

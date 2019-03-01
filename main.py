import datetime
import logging
import os
import traceback

import discord
from discord.ext import commands

import Token
import bd_verification
import messages
from data import mongo_setup
from services import data_service as svc, exceptions

# TODO: Load moderation cog
# TODO: Make the code compliant wit Discord dev ToS
mongo_setup.global_init()
# TODO: Get this to work properly
logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=';',
                   description='The official bot of the Furry Hideout!',
                   command_not_found="Command not found",
                   max_message=100000,
                   case_insensitive=True)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(
        name=";help for help",
        start=datetime.datetime.now()
    ))
    print('Logged in as: {}'.format(bot.user.name))
    print('-----------------')


@bot.event
async def on_member_join(member):
    if svc.should_welcome_in_guild(member.guild):
        await member.send(svc.get_welcome_message(member.guild.id))
    if svc.should_show_joining_in_guild(member.guild.id):
        lc = svc.get_log_channel_in_guild(member.guild.id)
        if lc:
            await lc.send(embed=messages.create_member_joined_embed(member))


@bot.event
async def on_member_leave(member):
    if svc.should_show_leaving(member.guild):
        lc = svc.get_log_channel_in_guild(member.guild.id)
        if lc:
            await lc.send(embed=messages.create_member_left_embed(member))


@bot.event
async def on_guild_join(guild: discord.Guild):
    svc.create_default_guild(guild)
    await guild.system_channel.send(messages.ON_GUILD_JOIN_MESSAGE)


@bot.event
async def on_error(event, *args, **kwargs):
    await bot.get_user(152543367937392640).send("```Error in {}\n\n{}```".format(event,
                                                                                 traceback.format_exc()))


@bot.event
async def on_command_error(ctx, error):
    svc.increment_retarded_user(ctx.guild.id)
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.delete()
        await ctx.send(error)


async def create_invite_with_exc_msg(e, channel):
    il = await channel.create_invite(max_uses=1, max_age=86400, unique=True, reason="Needed to reinvite user")
    embed = discord.Embed(color=0xff0000)
    embed.add_field(name=e, value=il)
    return embed


@bot.event
async def on_message(message):
    if type(message.channel) != discord.DMChannel and type(message.channel) != discord.GroupChannel:
        if svc.should_save_messages_in_guild(message.guild.id) and not message.author.bot:
            if message.attachments:
                await messages.save_attachments(message)
                message.content = "[Has attachment]" + message.content + "\n\tAttachments:\n\t\t"
                for a in message.attachments:
                    message.content += str(a.url.split("/")[-1]) + " [ID: {}]\n\t\t".format(a.id)
            svc.increment_message_saved(message.guild.id)
            with open(Token.get_log_path(message), 'a+', encoding="utf-8") as file:
                file.seek(0, os.SEEK_END)
                if not file.tell():
                    file.write(messages.USER_FILE_INFO.format(message.author))
                file.seek(0)
                file.write(messages.USER_NEW_MESSAGE_TO_LOG.format(message))
    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    if type(message.channel) != discord.DMChannel and type(message.channel) != discord.GroupChannel:
        try:
            if svc.should_show_deleted_in_guild(message.guild.id):
                if not message.author.bot:
                    log_channel = svc.get_log_channel_in_guild(message.guild)
                    file_channel = discord.utils.get(bot.guilds, name="zamirynth").text_channels[0]
                    if log_channel:
                        await messages.member_deleted_message(message, log_channel, file_channel)
        except exceptions.UpdateError:
            pass
        if svc.should_save_messages_in_guild(message.guild.id):
            svc.increment_message_deleted(message.guild.id)
            with open(Token.get_log_path(message), 'a+', encoding="utf-8") as file:
                file.seek(0, os.SEEK_END)
                if not file.tell():
                    file.write(messages.USER_FILE_INFO.format(message.author))
                file.seek(0)
                file.write(messages.USER_MESSAGE_DELETED_TO_LOG.format(datetime.datetime.utcnow(), message))


@bot.event
async def on_message_edit(b, a):
    if type(a.channel) != discord.DMChannel and type(a.channel) != discord.GroupChannel:
        if svc.should_show_edited_in_guild(a.guild.id):
            if not a.author.bot and b.content != a.content:
                log_channel = svc.get_log_channel_in_guild(a.guild)
                if log_channel:
                    await log_channel.send(embed=messages.member_edited_message(b, a))

        if svc.should_save_messages_in_guild(a.guild.id):
            svc.increment_message_edited(a.guild.id)
            with open(Token.get_log_path(a), 'a+', encoding="utf-8") as file:
                file.seek(0, os.SEEK_END)
                if not file.tell():
                    file.write(messages.USER_FILE_INFO.format(a.author))
                file.seek(0)
                file.write(messages.USER_MESSAGE_EDITED_TO_LOG.format(b, a))


@bot.command(pass_context=True)
async def verify(ctx: discord.ext.commands.Context, *args):
    """
    To verify yourself in the server using your date of birth.
    To use this command, you may have to use a password, set by the staff. This password may be in the rules.

    Example of this command with a password:
    ;verify password 01/01/0001

    Example of this command without a password (if none is set):
    ;verify 01/01/0001
    should_verify must be enabled in the settings of the bot (use ;svu to enable it).
    A 'verified' role must have been set (;help svr)
    A channel must be marked a the verification channel by using the ;svc command.
    If a log channel is set (;slc), a message will be posted there.
    """
    await ctx.message.delete()
    if svc.should_verify(ctx.guild.id):
        if svc.channel_is_verification(ctx):
            vr = svc.get_verified_role_in_guild(ctx.guild)
            if not vr:
                return await ctx.send("There is no role setup for the verification")
            log_channel = svc.get_log_channel_in_guild(ctx.guild)
            password = svc.get_password_in_guild(ctx.guild.id)
            if password:
                if len(args) != 2:
                    return await ctx.send("Missing/Too many arguments, please make sure you include all arguments in "
                                          "the command")
                dob = 1
                if args[0] != password:
                    return await ctx.send("Password invalid")
            else:
                if len(args) != 1:
                    return await ctx.send("Missing/Too many arguments, please make sure you include all arguments in "
                                          "the command")
                dob = 0
            try:
                bd_verification.verify_birthday(args[dob])
                svc.increment_verified_user(ctx.guild.id)
                await ctx.author.add_roles(vr)
                await ctx.author.send(messages.USER_IS_VERIFIED)
                if log_channel:
                    await log_channel.send(embed=messages.member_is_verified(ctx.message, args[dob]))
            except ValueError:
                await ctx.send(messages.INPUT_NOT_VALID.format("date"))
            except bd_verification.Invalid as e:
                await ctx.send(e)
            except bd_verification.Underaged as e:
                svc.increment_underaged_user(ctx.guild.id)
                await ctx.author.send(e)
                if log_channel:
                    await log_channel.send(embed=messages.member_is_underaged(ctx.message, args[dob]))
                await ctx.message.author.kick(reason=messages.USER_IS_UNDERAGED.format(
                    ctx.message))
        else:
            await ctx.send("You cannot use this command in this channel")
    else:
        await ctx.send("This command is not enabled")


@verify.error
async def verify_error(ctx, error):
    svc.increment_retarded_user(ctx.guild.id)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments, please make sure you include all arguments in the command")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have the permissions required to do this. (missing: {})".format(error.missing_perms))


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id != bot.user.id:
        r = svc.get_role_from_payload(payload, bot.get_guild(payload.guild_id))
        if not r:
            return
        u = bot.get_guild(payload.guild_id).get_member(payload.user_id)
        if not u:
            return await bot.get_user(152543367937392640) \
                .send("User not found in `on_raw_reaction_add`")
        await u.add_roles(r)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.user_id != bot.user.id:
        r = svc.get_role_from_payload(payload, bot.get_guild(payload.guild_id))
        if not r:
            return
        u = bot.get_guild(payload.guild_id).get_member(payload.user_id)
        if not u:
            return await bot.get_user(152543367937392640) \
                .send("User not found in `on_raw_reaction_remove`")
        await u.remove_roles(r)


def main():
    extensions = ['cogs.settings',
                  ]
    for e in extensions:
        try:
            bot.load_extension(e)
        except Exception as error:
            print(f"failed to load extension {e}.")
            traceback.print_exc()
    try:
        token = Token.get_token()
        bot.run(token)
    except FileNotFoundError:
        print("Token not found")


if __name__ == '__main__':
    main()

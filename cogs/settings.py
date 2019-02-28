import logging
import traceback

import discord
from discord.ext import commands

import messages
import reactions
from services import data_service as svc
from services import exceptions as exc


# Things left to do:


class Settings(commands.Cog):
    """
    The setting commands for this guild.
    You need to have the administrator or the manage server permission to use most of these commands.
    Default values:
        - Welcome message:
            "{}"
        - Channels: 
            - log_channel = None
            - verification_channel = None
            - update_channel = None
            - member_update_channel = None
        - Settings:
            - should_show_deleted = False
            - should_show_edited = False
            - should_show_joining = False
            - should_show_leaving = False
            - should_welcome_member = True
            - should_save_messages = False        
    """.format(messages.WELCOME_MESSAGE)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def settings(self, ctx):
        """
        Shows all the settings for the bot in the server.
        """
        await ctx.message.delete()
        em = messages.create_settings_embed(ctx)
        await ctx.send(embed=em)

    @commands.command(aliases=["sd"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def default_settings(self, ctx: commands.Context):
        """
        Sets all the settings to their default values.
        This does not affect the channels and the welcome message.
        """
        svc.set_settings_to_default_in_guild(ctx.guild.id)
        await ctx.send("Done:", embed=messages.create_settings_embed(ctx))

    @commands.command(name="set_message", aliases=['sm', 'setm', 'set_welcome'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def set_message(self, ctx: discord.ext.commands.Context, *, message):
        """
        Sets the welcome message that is sent to all members that joins the server.
        """
        await ctx.message.delete()
        m = messages.format_updated_message(svc.update_guild_welcome_message(ctx.guild, message))
        await ctx.send(m)

    @commands.command(aliases=['swt'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def welcome(self, ctx):
        """
        Toggles the automatic welcoming of members in the server.
        Defaults to True.
        """
        await ctx.message.delete()
        try:
            r = svc.update_should_welcome(ctx.guild.id)
        except exc.UpdateError:
            return await ctx.send('There was an error processing this command')
        await ctx.send('I will {}welcome new members'.format('' if r else 'not '))

    @commands.command(aliases=['sst'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def save(self, ctx):
        """
        Toggles the automatic recording of all messages in this server.
        Defaults to False.
        """
        await ctx.message.delete()
        try:
            r = svc.update_should_save_messages(ctx.guild.id)
        except exc.UpdateError:
            return await ctx.send('There was an error processing this command')
        await ctx.send('I will {}save messages in this server'.format('' if r else 'not '))

    @commands.command(aliases=['slc'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def set_log_channel(self, ctx: discord.ext.commands.Context):
        """
        Sets the channel for my logging.
        Use this command in the channel you want the logging to happen.
        If there is already a log channel set, it will be overwritten.
        Deleted messages, edited messages, user being verified and user leaving the server will be sent here.
        """
        await ctx.message.delete()
        try:
            svc.update_log_channel_in_guild(ctx.guild.id, ctx.channel.id)
        except exc.UpdateError:
            return await ctx.send('There was an error processing this command')
        await ctx.send('I will now log my things in this channel!')

    @commands.command(aliases=['svc'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def set_verification_channel(self, ctx: discord.ext.commands.Context):
        """
        Sets the channel for the verification of users.
        Use this command in the channel you want the verification to happen.
        If there is already a channel set, it will be overwritten.
        I will only react to the verification command in this channel.
        """
        await ctx.message.delete()
        try:
            svc.update_verification_channel_in_guild(ctx.guild.id, ctx.channel.id)
        except exc.UpdateError:
            return await ctx.send('There was an error processing this command')
        await ctx.send('I will now verify members in this channel!')

    @commands.command(aliases=['suc'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def set_update_channel(self, ctx: discord.ext.commands.Context):
        """
        Sets the channel for the updates of the bot.
        Messages sent by other servers will also be sent in that channel.
        If a channel is already set, it will be overwritten
        """
        await ctx.message.delete()
        try:
            svc.update_update_channel_in_guild(ctx.guild.id, ctx.channel.id)
        except exc.UpdateError:
            return await ctx.send('There was an error processing this command')
        await ctx.send('I will now verify members in this channel!')

    @commands.command(aliases=['svr'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def set_verification_role(self, ctx: discord.ext.commands.Context, role_name):
        """
        Set the role given by the !.verify command.
        The role must already exist in the server.
        The name of the role must be between quotes (ex: ';svr "verified"')
        If a role is already set, it will be overwritten
        """
        r = discord.utils.get(ctx.guild.roles, name=role_name)
        print(r)
        if not r:
            return await ctx.send(f"Cannot find a role called '{role_name}' in the server")
        svc.set_verified_role_in_guild(r)
        await ctx.send(f"Set the verification role to '{role_name}'")

    @commands.command(aliases=['ssd'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def show_deleted(self, ctx):
        """
        Toggles the logging of deleted messages in the log channel.
        If no logging channel is set, turning this on won't do anything.
        """
        await ctx.message.delete()
        try:
            r = svc.update_should_show_deleted(ctx.guild.id)
        except exc.UpdateError as e:
            return await ctx.send(e)
        await ctx.send('I will {}log deleted messages in this server'.format('' if r else 'not '))

    @commands.command(aliases=['sse'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def show_edited(self, ctx):
        """
        Toggles the logging of edited messages in the log channel.
        If no logging channel is set, turning this on won't do anything.
        """
        await ctx.message.delete()
        try:
            r = svc.update_should_show_edited(ctx.guild.id)
        except exc.UpdateError as e:
            return await ctx.send(e)
        await ctx.send('I will {}log edited messages in this server'.format('' if r else 'not '))

    @commands.command(aliases=['ssj'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def show_joining(self, ctx):
        """
        Toggles the logging of joining members in the log channel.
        If no logging channel is set, turning this on won't do anything.
        """
        await ctx.message.delete()
        try:
            r = svc.update_should_show_joining(ctx.guild.id)
        except exc.UpdateError as e:
            return await ctx.send(e)
        await ctx.send('I will {}log joining members in this server'.format('' if r else 'not '))

    @commands.command(aliases=['ssl'])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def show_leaving(self, ctx):
        """
        Toggles the logging of leaving members in the log channel.
        If no logging channel is set, turning this on won't do anything.
        """
        await ctx.message.delete()
        try:
            r = svc.update_should_show_leaving(ctx.guild.id)
        except exc.UpdateError as e:
            return await ctx.send(e)
        await ctx.send('I will {}log leaving members in this server'.format('' if r else 'not '))

    @commands.command(aliases=["svm"])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def should_verify(self, ctx):
        """
        Toggle the verification of users in this server.
        To use the verification system, a verification channel must be set (;svc)
        """
        await ctx.message.delete()
        try:
            r = svc.update_should_verify(ctx.guild.id)
        except exc.UpdateError:
            return await ctx.send('There was an error processing this command')
        await ctx.send('I will {}verify new members in this server'.format('' if r else 'not '))

    @commands.command(aliases=["ar"])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def add_roles(self, ctx, *args):
        """
        Add roles to the self-assignation system.
        The first parameter is the category of the roles.
        You must write all the roles you want to be under the same category.
        Up to 10 roles can be added under the same category
        All the roles must already exists in the server.
        Example:
            ;add_roles Gender Male Female Other
        """
        await ctx.message.delete()
        if len(args) < 2:
            return await ctx.send("Invalid input, do `;help add_roles` for help.")
        elif len(args) > 11:
            return await ctx.send("A maximum of 10 roles can be added to one category")
        l = list(args)
        category = l.pop(0)
        message = await ctx.send(messages.create_new_role(category, l, ctx.guild))
        if not message:
            return await ctx.send("Error in the command.")
        for idx, r_name in enumerate(l):
            r = discord.utils.get(ctx.guild.roles, name=r_name)
            svc.add_role_to_guild(message.id, r, category, idx)
            await message.add_reaction(reactions.REACTIONS[idx])

    @commands.command(aliases=["spw"])
    @commands.has_permissions(administrator=True, manage_guild=True)
    async def set_password(self, ctx, psswd):
        """
        Sets the password for the verification system.
        Using this command when there is a password set overwrites it.
        """
        await ctx.message.delete()
        svc.set_password_for_guild(ctx.guild.id, psswd)
        await ctx.send("Password set.")

    async def cog_command_error(self, ctx: discord.ext.commands.Context, error: discord.ext.commands.CommandError):
        await ctx.bot.get_user(152543367937392640).send("There was an error in the Setting cog:\n"
                                                        "```{}```\n```{}```".format(traceback.format_exc(limit=5),
                                                                                    error))
        svc.increment_retarded_user(ctx.guild.id)


def setup(bot):
    logging.info("Loaded settings")
    bot.add_cog(Settings(bot))

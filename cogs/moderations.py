import logging
import os
import random
import string
import subprocess
import traceback

import discord
from discord.ext import commands

import Token
from services import data_service as svc


# TODO: Kick command
# TODO: Report command


class Moderation(commands.Cog):
    """
    The moderation commands.
    These commands requires special permissions to use.
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: discord.ext.commands.Context, error: discord.ext.commands.CommandError):
        await ctx.bot.get_user(152543367937392640).send("There was an error in the Moderation cog:\n"
                                                        "```{}```\n```{}```".format(traceback.format_exc(limit=5),
                                                                                    error))
        svc.increment_retarded_user(ctx.guild.id)

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, user_id: int, reason: str):
        """
        Ban a user across all the guilds the bot is in
        :param user_id: the ID of the user to ban
        :param reason: the reason of the ban, must be between quotes.
        """
        int_user_id = int(user_id)
        user = ctx.bot.get_user(int_user_id)
        for guild in ctx.bot.guilds:
            log_channel = svc.get_log_channel_in_guild(guild)
            if not log_channel:
                pass
            else:
                # noinspection PyStringFormat
                await log_channel.send("Banning user '{0}' with reason '{1}'. The ban was put in place by {"
                                       "2.author.name} in the guild '{2.guild.name}'".format(user, reason, ctx))
            try:
                await guild.ban(user, reason=reason, delete_message_days=7)
            except Exception as e:
                await ctx.send("User not found in {}".format(guild.name))

    @commands.command(aliases=["gf"])
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def get_file(self, ctx: commands.Context, user_id: int):
        """
        Get the file record of a user as a zip file.
        If the file is over 8MB, only the text history will be sent.
        """
        try:
            user: discord.User = await ctx.bot.get_user_info(user_id)
        except discord.NotFound:
            return await ctx.send("A user with this ID does not exist")
        except discord.HTTPException:
            return await ctx.send("Fetching the user failed")
        async with ctx.channel.typing():
            files = Token.get_files_in_user_folder(user.name, ctx.guild.name)
            password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            if not files:
                return await ctx.send(f"Couldn't find any data on user {user.name}")
            rc = subprocess.call(
                ['C:/Program Files/7-Zip/7z', 'a', '-p' + password, Token.get_zip_path(), '-mx9'] + files)
            if os.stat(Token.get_zip_path()).st_size >= 8388608:
                os.remove(Token.get_zip_path())
                rc = subprocess.call(
                    ['C:/Program Files/7-Zip/7z', 'a', '-p' + password, Token.get_zip_path(), '-mx9'] +
                    [Token.get_log_path(ctx.message)])
            try:
                await ctx.author.send(f"Here is the password for the zip file: `{password}`")
                await ctx.send(f"Here is the requested file, the password was sent in your dms {ctx.author.mention}. "
                               f"This message will be deleted in 5 minutes.",
                               file=discord.File(fp=Token.get_zip_path(),
                                                 filename="user.zip"),
                               delete_after=300)
            except discord.Forbidden:
                await ctx.send(f"Couldn't send the password to your dms {ctx.author.mention}. "
                               f"Make sure that your privacy settings allows members of this server to send you "
                               f"private messages")
            except discord.InvalidArgument:
                await ctx.send("The files list is not of the appropriate size or you specified both file and files.")
            os.remove(Token.get_zip_path())


def setup(bot):
    logging.info("loaded moderation cog")
    bot.add_cog(Moderation(bot))

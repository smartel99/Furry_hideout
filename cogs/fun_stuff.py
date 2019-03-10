import discord
from discord.ext import commands

import cogs.utils.eapi
import cogs.utils.sfapi

processapi = cogs.utils.eapi.processapi
processshowapi = cogs.utils.eapi.processshowapi
search = cogs.utils.sfapi.search


class ResultNotFound(Exception):
    """Used if ResultNotFound is triggered by e* API."""
    pass


class InvalidHTTPResponse(Exception):
    """Used if non-200 HTTP Response got from server."""
    pass


class Fun(commands.Cog):
    """The fun and random commands of the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["e6"])
    async def e621(self, ctx, *args):
        """Does this command really need explanations?

        Shoutout to rorre on github for this command
        https://github.com/rorre/gonnarewritebot"""
        if not isinstance(ctx.channel, discord.DMChannel):
            if not isinstance(ctx.channel, discord.GroupChannel):
                if not ctx.channel.is_nsfw():
                    await ctx.send("Cannot be used in non-NSFW channels!")
                    return
        args = ' '.join(args)
        args = str(args)
        netloc = "e621"
        print("------")
        print("Got command with args: " + args)
        if "order:score_asc" in args:
            await ctx.send("I'm not going to fall into that one, silly~")
            return
        if "score:" in args:
            apilink = 'https://e621.net/post/index.json?tags=' + args + '&limit=320'
        else:
            apilink = 'https://e621.net/post/index.json?tags=' + args + ' score:>25&limit=320'
        async with ctx.channel.typing():
            try:
                await processapi(apilink)
            except ResultNotFound:
                await ctx.send("Result not found!")
                return
            except InvalidHTTPResponse:
                await ctx.send("We're getting invalid response from the API, please try again later!")
                return

            await ctx.send(
                """Post link: `https://""" + netloc + """.net/post/show/""" + processapi.imgid + """/`\r\nArtist: `""" + processapi.imgartist + """`\r\nSource: `""" + processapi.imgsource + """`\r\nRating: """ + processapi.imgrating + """\r\nTags: `""" + processapi.imgtags + """` ...and more\r\nImage link: """ + processapi.file_link)


def setup(bot):
    bot.add_cog(Fun(bot))

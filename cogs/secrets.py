import logging

from discord.ext import commands


class Secret(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def message(self, ctx: commands.Context):
        """
        A message for someone.
        """
        if ctx.author.id == 517306517569929216:
            await ctx.author.send("""Hey Charmy, it's Rald! ^^
I'm glad you found this command that I've written just for you!
I hope you are having a nice day :3
I just wanted to tell you thank you.
Thank you for believing in me.
Thank you for giving me a chance.
Thank you for being there.
Thank you for being who you are.
Thank you for everything
You are a great person capable of great things, I believe in you!

I hope you like this bot, I worked hard to make it what it is. ^^
This is my gift to you Charmy, stay awesome *hugs you tightly*

Samuel Martel, aka Raldryniorth the Dragon""")
            await ctx.bot.get_user(152543367937392640).send("Charmy used the command")
        else:
            await ctx.send("This command is not destined to be used by you, sorry... ")


def setup(bot):
    logging.info("Loaded secret")
    bot.add_cog(Secret(bot))

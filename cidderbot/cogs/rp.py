import logging

from discord.ext import commands


class Rp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def test(self, ctx, member: commands.MemberConverter, *, reason=None):
    #     # await ctx.guild.ban(member, reason=reason)
    #     # await ctx.send(f'{member} has been banned.')
    #     pass

def setup(bot):
    bot.add_cog(Rp(bot))

from utils.utils import Timer
import discord

from io import BytesIO
from utils import AvimetryContext, AvimetryBot
from discord.ext import commands


class Animals(commands.Cog):
    def __init__(self, bot: AvimetryBot):
        self.bot = bot

    async def do_animal(self, ctx: AvimetryContext, animal: str):
        async with ctx.channel.typing():
            with Timer() as timer:
                e = await self.bot.sr.get_image(animal)
        file = discord.File(BytesIO(await e.read()), filename=f"{animal}.png")
        embed = discord.Embed(
            title=f"Here is {animal}",
            description=f"Powered by Some Random API\nProcessed in `{timer.total_time:,.2f}ms`"
        )
        embed.set_image(url=f"attachment://{animal}.png")
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def dog(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "dog")

    @commands.command()
    async def cat(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "cat")

    @commands.command()
    async def panda(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "panda")

    @commands.command()
    async def fox(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "fox")

    @commands.command()
    async def koala(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "koala")

    @commands.command()
    async def birb(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "birb")

    @commands.command()
    async def racoon(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "racoon")

    @commands.command()
    async def kangaroo(self, ctx: AvimetryContext):
        await self.do_animal(ctx, "kangaroo")

    @commands.command()
    async def duck(self, ctx: AvimetryContext):
        async with self.bot.session.get("https://random-d.uk/api/v2/random") as resp:
            image = await resp.json()
        embed = discord.Embed(title="Here is a duck")
        embed.set_image(url=image['url'])
        await ctx.send(embed=embed)


def setup(bot: AvimetryBot):
    bot.add_cog(Animals(bot))

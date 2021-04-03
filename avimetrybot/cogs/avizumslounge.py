import discord
from discord.ext import commands
from utils.errors import AvizumsLoungeOnly


class AvizumsLounge(commands.Cog, name="Avizum's Lounge"):
    '''
    Commands for Avizum's Lounge only.
    '''
    def __init__(self, avi):
        self.avi = avi
        self.guild_id = 751490725555994716
        self.joins_and_leaves = 751967006701387827
        self.member_channel = 783960970472456232
        self.bot_channel = 783961050814611476
        self.total_channel = 783961111060938782

    def cog_check(self, ctx):
        if ctx.guild.id != self.guild_id:
            raise AvizumsLoungeOnly("This command only works in a private server.")
        return True

    def get(self, channel_id: int):
        return self.avi.get_channel(channel_id)

    # Counter
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == self.guild_id:
            root = member.guild.get_role(813535792655892481)
            await member.add_roles(root)

        if self.get(self.joins_and_leaves).guild.id == member.guild.id:
            join_message = discord.Embed(
                title="Member Joined",
                description=(
                    f"Hey **{str(member)}**, Welcome to **{member.guild.name}**!\n"
                    f"This server now has a total of **{member.guild.member_count}** members."
                ),
                color=discord.Color.blurple()
            )
            await self.get(self.joins_and_leaves).send(embed=join_message)

        try:
            if member.guild.id == self.get(self.joins_and_leaves).guild.id:
                await self.get(self.total_channel).edit(name=f"Total Members: {member.guild.member_count}")

                true_member_count = len([m for m in member.guild.members if not m.bot])
                await self.get(self.member_channel).edit(name=f"Members: {true_member_count}")

                true_bot_count = len([m for m in member.guild.members if m.bot])
                await self.get(self.bot_channel).edit(name=f"Bots: {true_bot_count}")
        except Exception:
            return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == self.guild_id:
            if self.get(self.joins_and_leaves).guild.id == member.guild.id:
                lm = discord.Embed(
                    title="Member Leave",
                    description=(
                        f"Aww, **{str(member)}** has left **{member.guild.name}**.\n"
                        f"This server now has a total of **{member.guild.member_count}** members."
                    ),
                    color=discord.Color.red()
                )
                await self.get(self.joins_and_leaves).send(embed=lm)

        try:
            if member.guild.id == self.get(self.joins_and_leaves).guild.id:
                await self.get(self.total_channel).edit(name=f"Total Members: {member.guild.member_count}")

                true_member_count = len([m for m in member.guild.members if not m.bot])
                await self.get(self.member_channel).edit(name=f"Members: {true_member_count}")

                true_bot_count = len([m for m in member.guild.members if m.bot])
                await self.get(self.bot_channel).edit(name=f"Bots: {true_bot_count}")
        except Exception:
            return

    @commands.Cog.listener("on_voice_state_update")
    async def vs_update(self, member, before, after):
        if member.guild.id != 751490725555994716:
            return
        if before.channel == after.channel:
            return
        try:
            if after.channel is None:
                channel = discord.utils.get(member.guild.text_channels, name=f"vc-{before.channel.name}")
                await channel.set_permissions(member, overwrite=None)
                return
            else:
                if before.channel:
                    before_channel = discord.utils.get(member.guild.text_channels, name=f"vc-{before.channel.name}")
                    await before_channel.set_permissions(member, overwrite=None)

                channel = discord.utils.get(member.guild.text_channels, name=f"vc-{after.channel.name}")
                if channel is None:
                    return

                if after.channel.name == channel.name[3:]:
                    overwrites = discord.PermissionOverwrite()
                    overwrites.read_messages = True
                    overwrites.read_message_history = True
                    await channel.set_permissions(member, overwrite=overwrites)

        except Exception:
            return

    @commands.Cog.listener("on_member_update")
    async def member_update(self, before, after):
        if after.guild.id != 751490725555994716:
            return
        if not after.nick:
            return
        if "avi" in after.nick.lower():
            if after == self.avi.user:
                return
            if after.id == 750135653638865017:
                return
            try:
                return await after.edit(nick=after.name, reason="Nick can not be \"avi\"")
            except discord.Forbidden:
                pass

    # Update Member Count Command
    @commands.command(
        aliases=["updatemc", "umembercount"],
        brief="Updates the member count if the count gets out of sync.",
    )
    @commands.has_permissions(administrator=True)
    async def refreshcount(self, ctx):
        channel = self.avi.get_channel(783961111060938782)
        await channel.edit(name=f"Total Members: {channel.guild.member_count}")

        channel2 = self.avi.get_channel(783960970472456232)
        true_member_count = len([m for m in channel.guild.members if not m.bot])
        await channel2.edit(name=f"Members: {true_member_count}")

        channel3 = self.avi.get_channel(783961050814611476)
        true_bot_count = len([m for m in channel.guild.members if m.bot])
        await channel3.edit(name=f"Bots: {true_bot_count}")
        await ctx.send("Member Count Updated.")


def setup(avi):
    avi.add_cog(AvizumsLounge(avi))

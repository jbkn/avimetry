import discord
from discord.ext import commands
from utils import AvimetryBot, AvimetryContext, Prefix


class Settings(commands.Cog):
    def __init__(self, avi):
        self.avi: AvimetryBot = avi
        self.map = {
            True: "Enabled",
            False: "Disabled"}

    @commands.group(
        brief="Configure the server's prefixes",
        case_insensitive=True,
        invoke_without_command=True)
    async def prefix(self, ctx: AvimetryContext):
        prefix = await ctx.cache.get_guild_settings(ctx.guild.id)
        if not prefix["prefixes"]:
            return await ctx.send("This server doesn't have a custom prefix set yet. The default prefix is always `a.`")
        else:
            guild_prefix = prefix["prefixes"]
        if len(guild_prefix) == 1:
            return await ctx.send(f"The prefix for this server is `{guild_prefix[0]}`")
        await ctx.send(f"Here are my prefixes for this server: \n`{'` | `'.join(guild_prefix)}`")

    @prefix.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix_add(self, ctx: AvimetryContext, prefix: Prefix):
        await self.avi.pool.execute(
            "UPDATE guild_settings SET prefixes = ARRAY_APPEND(prefixes, $2) WHERE guild_id = $1",
            ctx.guild.id, prefix)
        ctx.cache.guild_settings_cache[ctx.guild.id]["prefixes"].append(prefix)
        await ctx.send(f"Appended `{prefix}` to the list of prefixes.")

    @prefix.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix_remove(self, ctx: AvimetryContext, prefix):
        prefix = prefix.lower()
        guild_cache = await ctx.cache.get_guild_settings(ctx.guild.id)
        if not guild_cache:
            return await ctx.send(
                "You don't have any prefixes set for this server. Set one by using `a.settings prefix add <prefix>`")

        guild_prefix = guild_cache["prefixes"]
        if prefix not in guild_prefix:
            return await ctx.send(f"`{prefix}` is not a prefix of this server.")

        await self.avi.pool.execute(
            "UPDATE guild_settings SET prefixes = ARRAY_REMOVE(prefixes, $2) WHERE guild_id = $1",
            ctx.guild.id, prefix)

        self.avi.temp.guild_settings_cache[ctx.guild.id]["prefixes"].remove(prefix)
        await ctx.send(f"Removed `{prefix}` from the list of prefixes")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def muterole(self, ctx: AvimetryContext, role: discord.Role):
        await self.avi.pool.execute(
            "UPDATE guild_settings SET mute_role = $1 WHERE guild_id = $2",
            role.id, ctx.guild.id)
        self.avi.temp.guild_settings_cache[ctx.guild.id]["mute_role"] = role.id
        for channel in ctx.guild.channels:
            perms = channel.overwrites_for(role)
            perms.update(send_messages=False)
            await channel.set_permissions(
                target=role,
                overwrite=perms,
                reason=f"Mute role set to {role.name} by {ctx.author}"
            )
        await ctx.send(f"Set the mute role to {role.mention}")

    @commands.group(invoke_without_command=True, brief="Configure logging")
    @commands.has_permissions(manage_guild=True)
    async def logging(self, ctx: AvimetryContext, toggle: bool = None):
        if toggle is None:
            config = ctx.cache.logging_cache[ctx.guild.id]
            embed = discord.Embed(
                title="Logging Configuation",
                description=(
                    "```py\n"
                    f"Global Toggle: {config['enabled']}\n"
                    f"Message Delete: {config['message_delete']}\n"
                    f"Message Edit: {config['message_edit']}```"))
            return await ctx.send(embed=embed)
        await self.avi.pool.execute(
            "UPDATE logging SET enabled = $1 WHERE guild_id = $2",
            toggle, ctx.guild.id)
        ctx.cache.logging_cache[ctx.guild.id]["enabled"] = toggle
        await ctx.send(f"{self.map[toggle]} logging")

    @logging.command(name="channel", brief="Configure logging channel")
    @commands.has_permissions(manage_guild=True)
    async def logging_channel(self, ctx: AvimetryContext, channel: discord.TextChannel):
        await self.avi.pool.execute(
            "UPDATE logging SET channel_id = $1 WHERE guild_id = $2",
            channel.id, ctx.guild.id)
        ctx.cache.logging_cache[ctx.guild.id]["channel_id"] = channel.id
        await ctx.send(f"Set logging channel to {channel}")

    @logging.command(
        brief="Configure delete logging",
        name="message_delete",
        aliases=["msgdelete, messagedelete"])
    @commands.has_permissions(manage_guild=True)
    async def message_delete(self, ctx: AvimetryContext, toggle: bool):
        await self.avi.pool.execute(
            "UPDATE logging SET message_delete = $1 WHERE guild_id = $2",
            toggle, ctx.guild.id
        )
        ctx.cache.logging_cache[ctx.guild.id]["message_delete"] = toggle
        await ctx.send(f"{self.map[toggle]} message delete logs")

    @logging.command(
        brief="Configure edit logging",
        name="message_edit",
        aliases=["msgedit", "messageedit"])
    @commands.has_permissions(administrator=True)
    async def edit(self, ctx: AvimetryContext, toggle: bool):
        await self.avi.pool.execute(
            "UPDATE logging SET message_edit = $1 WHERE guild_id = $2",
            toggle, ctx.guild.id
        )
        ctx.cache.logging_cache[ctx.guild.id]["message_edit"] = toggle
        await ctx.send(f"{self.map[toggle]} message edit logs")

    @commands.group(
        brief="Verify system configuration for this server",
        invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def verification(self, ctx: AvimetryContext, toggle: bool = None):
        if toggle is None:
            return await ctx.send_help("settings verify")
        await self.avi.config.upsert(
            {"_id": ctx.guild.id, "verification_gate": toggle}
        )
        await ctx.send(f"Set verify system is set to {toggle}")

    @verification.command(
        brief="Set the role to give when a member finishes verification.")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def role(self, ctx: AvimetryContext, role: discord.Role):
        await self.avi.config.upsert({"_id": ctx.guild.id, "gate_role": role.id})
        await ctx.send(f"The verify role is set to {role}")

    @commands.group(
        invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx):
        return

    @commands.group(invoke_without_command=True, brief="Configure counting settings")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def counting(self, ctx: AvimetryContext):
        await ctx.send_help("config counting")

    @counting.command(brief="Set the count in the counting channel")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def setcount(self, ctx: AvimetryContext, count: int):
        await self.avi.config.upsert({"_id": ctx.guild.id, "current_count": count})
        await ctx.send(f"Set the count to {count}")

    @counting.command(brief="Set the channel for counting")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def channel(self, ctx: AvimetryContext, channel: discord.TextChannel):
        await self.avi.config.upsert(
            {"_id": ctx.guild.id, "counting_channel": channel.id}
        )
        await ctx.send(f"Set the counting channel to {channel}")


def setup(avi):
    avi.add_cog(Settings(avi))
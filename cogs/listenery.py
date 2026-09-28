import asyncio

import nextcord
from nextcord import (
    Message, Embed, utils, TextChannel, CategoryChannel,
    AuditLogAction, VoiceChannel, Member, VoiceState,
)
from nextcord.abc import GuildChannel
from nextcord.ext import commands

from config import (
    FOOTER_TEXT, LOG_CHANNEL_ID, WELCOME_CHANNEL_ID, BOOST_CHANNEL_ID,
    AUTO_DELETE_CHANNEL_ID, STATS_MEMBERS_VC_ID, STATS_BANS_VC_ID,
    STATS_LATEST_VC_ID,
)


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_log_channel(self, guild):
        return guild.get_channel(LOG_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.author.bot:
            return
        channel = self._get_log_channel(before.guild)
        if not channel:
            return

        embed = Embed(
            title="Message edited by:",
            description=str(before.author),
            color=before.author.color,
            timestamp=utils.utcnow(),
        )
        embed.add_field(name="Original message:", value=before.content or "*empty*", inline=False)
        embed.add_field(name="New message:", value=after.content or "*empty*", inline=False)
        embed.set_footer(text=FOOTER_TEXT)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message):
        if message.author.bot:
            return
        channel = self._get_log_channel(message.guild)
        if not channel:
            return

        embed = Embed(
            title="Message deleted by:",
            description=str(message.author),
            color=message.author.color,
            timestamp=utils.utcnow(),
        )
        embed.add_field(name="Deleted message:", value=message.content or "*empty*", inline=False)
        embed.set_footer(text=FOOTER_TEXT)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: GuildChannel):
        log_channel = self._get_log_channel(channel.guild)
        if not log_channel:
            return

        async for entry in channel.guild.audit_logs(limit=10, action=AuditLogAction.channel_create):
            if entry.target == channel:
                if isinstance(channel, CategoryChannel):
                    embed = Embed(
                        title="Category created",
                        description=f"Category **{channel.mention}** was created by {entry.user.mention}.",
                        color=0x00FF00,
                        timestamp=utils.utcnow(),
                    )
                else:
                    embed = Embed(
                        title="Channel created",
                        description=f"Channel {channel.mention} was created by {entry.user.mention}.",
                        color=0x00FF00,
                        timestamp=utils.utcnow(),
                    )
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel):
        log_channel = self._get_log_channel(before.guild)
        if not log_channel:
            return

        async def _get_updater():
            async for entry in after.guild.audit_logs(limit=1, action=AuditLogAction.channel_update):
                return entry.user
            return None

        if isinstance(before, CategoryChannel) and isinstance(after, CategoryChannel):
            if before.name != after.name:
                user = await _get_updater()
                embed = Embed(
                    title="Category edited",
                    description=f"Category **{before.name}** renamed to **{after.name}** by {user.mention if user else 'unknown'}.",
                    color=0xFFA500,
                    timestamp=utils.utcnow(),
                )
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

        if before.overwrites != after.overwrites:
            user = await _get_updater()
            embed = Embed(
                title="Permissions updated",
                description=f"Permissions for **{before.name}** were changed by {user.mention if user else 'unknown'}.",
                color=0xFFA500,
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await log_channel.send(embed=embed)
            return

        if before.position != after.position:
            user = await _get_updater()
            embed = Embed(
                title="Channel moved",
                description=f"**{before.name}** was moved to position **{after.position}**.",
                color=0xFFA500,
                timestamp=utils.utcnow(),
            )
            embed.add_field(name="Moved by:", value=user.mention if user else "unknown")
            embed.set_footer(text=FOOTER_TEXT)
            await log_channel.send(embed=embed)
            return

        if isinstance(before, TextChannel) and isinstance(after, TextChannel):
            if before.name != after.name:
                user = await _get_updater()
                embed = Embed(
                    title="Channel edited",
                    description=f"Channel {before.mention} renamed to **{after.name}**.",
                    color=0xFFA500,
                    timestamp=utils.utcnow(),
                )
                embed.add_field(name="Changed by:", value=user.mention if user else "unknown")
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

            if before.topic != after.topic:
                user = await _get_updater()
                embed = Embed(
                    title="Channel topic changed",
                    description=f"Topic for {after.mention} was updated.",
                    color=0xFFA500,
                    timestamp=utils.utcnow(),
                )
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

        if isinstance(before, VoiceChannel) and isinstance(after, VoiceChannel):
            if before.name != after.name:
                user = await _get_updater()
                embed = Embed(
                    title="Voice channel edited",
                    description=f"Channel {before.mention} renamed to **{after.name}** by {user.mention if user else 'unknown'}.",
                    color=0xFFA500,
                    timestamp=utils.utcnow(),
                )
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

            if before.bitrate != after.bitrate:
                user = await _get_updater()
                embed = Embed(
                    title="Voice channel edited",
                    description=f"Bitrate for **{before.name}** changed to **{after.bitrate / 1000} kbps** by {user.mention if user else 'unknown'}.",
                    color=0xFFA500,
                    timestamp=utils.utcnow(),
                )
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

            if before.user_limit != after.user_limit:
                user = await _get_updater()
                limit_text = "no limit" if after.user_limit == 0 else str(after.user_limit)
                embed = Embed(
                    title="Voice channel edited",
                    description=f"User limit for **{before.name}** changed to **{limit_text}** by {user.mention if user else 'unknown'}.",
                    color=0xFFA500,
                    timestamp=utils.utcnow(),
                )
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        log_channel = self._get_log_channel(channel.guild)
        if not log_channel:
            return

        async for entry in channel.guild.audit_logs(limit=10, action=AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                channel_type = "Category" if isinstance(channel, CategoryChannel) else (
                    "Voice channel" if isinstance(channel, VoiceChannel) else "Channel"
                )
                embed = Embed(
                    title=f"{channel_type} deleted",
                    description=f"**{channel.name}** was deleted by {entry.user.mention}.",
                    color=0xFF0000,
                    timestamp=utils.utcnow(),
                )
                embed.set_footer(text=FOOTER_TEXT)
                await log_channel.send(embed=embed)
                return

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        if before.nick != after.nick:
            log_channel = self._get_log_channel(before.guild)
            if not log_channel:
                return

            embed = Embed(
                title="Nickname change",
                description=f"{after.mention} changed nickname from **{before.nick}** to **{after.nick}**.",
                color=0xFFA500,
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await log_channel.send(embed=embed)

        if before.premium_since is None and after.premium_since is not None:
            boost_channel = self.bot.get_channel(BOOST_CHANNEL_ID)
            if boost_channel:
                embed = Embed(
                    title="🚀 New Server Boost!",
                    description=f"{after.mention} just boosted the server! Thank you 💖!",
                    color=0xFFD700,
                    timestamp=utils.utcnow(),
                )
                embed.set_author(name=after.display_name, icon_url=after.avatar.url if after.avatar else None)
                embed.set_footer(text=FOOTER_TEXT)
                await boost_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        log_channel = self._get_log_channel(member.guild)

        if log_channel and before.channel != after.channel:
            if before.channel is not None and after.channel is not None:
                embed = Embed(
                    title="Voice channel change",
                    description=f"**{member.display_name}** moved from {before.channel.mention} to {after.channel.mention}.",
                    color=0x00FFFF,
                    timestamp=utils.utcnow(),
                )
            elif before.channel is not None:
                embed = Embed(
                    title="Left voice channel",
                    description=f"**{member.display_name}** left {before.channel.mention}.",
                    color=0xFF0000,
                    timestamp=utils.utcnow(),
                )
            elif after.channel is not None:
                embed = Embed(
                    title="Joined voice channel",
                    description=f"**{member.display_name}** joined {after.channel.mention}.",
                    color=0x00FF00,
                    timestamp=utils.utcnow(),
                )
            else:
                return

            avatar_url = member.avatar.url if member.avatar else None
            embed.set_thumbnail(url=avatar_url)
            embed.set_footer(text=FOOTER_TEXT)
            await log_channel.send(embed=embed)

        guild = member.guild
        stats_channels = {
            STATS_MEMBERS_VC_ID: lambda: f"👥│Members: {len(guild.members)}",
            STATS_BANS_VC_ID: None,
            STATS_LATEST_VC_ID: lambda: f"🐧│Latest: {max(guild.members, key=lambda m: m.joined_at).name}",
        }

        for vc_id, name_fn in stats_channels.items():
            if vc_id == 0:
                continue
            vc = guild.get_channel(vc_id)
            if not vc or not isinstance(vc, nextcord.VoiceChannel):
                continue

            if vc_id == STATS_BANS_VC_ID:
                ban_list = []
                async for ban_entry in guild.bans():
                    ban_list.append(ban_entry)
                name = f"🔨│Bans: {len(ban_list)}"
            else:
                name = name_fn()

            if len(name) > 100:
                name = name[:97] + "..."

            try:
                await vc.edit(name=name)
            except nextcord.HTTPException:
                pass

        await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        pos = sum(
            1 for m in member.guild.members
            if m.joined_at is not None and m.joined_at < member.joined_at
        )

        embed = Embed(
            title="👋 Welcome!",
            description=f"{member.mention} Welcome to the server! You are member **#{pos}**!",
            color=nextcord.Color.brand_green(),
            timestamp=utils.utcnow(),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await channel.send(content=f"{member.mention} just joined!", embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        log_channel = self._get_log_channel(message.guild)
        if not log_channel:
            return

        embed = Embed(
            title="Message sent by:",
            description=message.author.mention,
            color=message.author.color,
            timestamp=utils.utcnow(),
        )
        embed.add_field(name="Message:", value=message.content or "*empty*")
        embed.add_field(name="Channel:", value=str(message.channel))
        embed.set_footer(text=FOOTER_TEXT)

        if AUTO_DELETE_CHANNEL_ID and message.channel.id == AUTO_DELETE_CHANNEL_ID:
            try:
                await message.delete()
            except nextcord.HTTPException:
                pass

        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"[Logs] Failed to send log: {e}")

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, exception: Exception):
        print(f"[CMD Error] /{interaction.application_command}: {exception}")


def setup(bot):
    bot.add_cog(Logs(bot))
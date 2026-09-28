import datetime
import asyncio

import nextcord
from nextcord import utils
from nextcord.ext import commands, application_checks

from config import FOOTER_TEXT, ANNOUNCEMENT_CHANNEL_ID, PROMOTION_CHANNEL_ID


promo_message = None


class AnnouncementsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="announce", description="Sends an announcement!")
    @application_checks.has_permissions(administrator=True)
    async def announce(self, interaction: nextcord.Interaction, *, content: str):
        channel = self.bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)

        if not channel or not isinstance(channel, nextcord.TextChannel):
            await interaction.response.send_message(
                "Cannot find the announcement channel. Check ANNOUNCEMENT_CHANNEL_ID in .env.",
                ephemeral=True,
            )
            return

        embed = nextcord.Embed(
            title="📣 Announcement 📣",
            description=f">>> {content}",
            color=nextcord.Color.dark_gold(),
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.set_footer(text=FOOTER_TEXT)

        confirm = nextcord.Embed(
            title="ANNOUNCEMENT CREATED!",
            description="",
            color=0x000000,
            timestamp=utils.utcnow(),
        )
        confirm.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=confirm, ephemeral=True)
        await channel.send(content="||@everyone @here||", embed=embed)

    @nextcord.slash_command(name="promotion", description="Sends a promotion!")
    @application_checks.has_permissions(administrator=True)
    async def promotion(self, interaction: nextcord.Interaction, target: str, discount: str, duration: str):
        global promo_message

        channel = self.bot.get_channel(PROMOTION_CHANNEL_ID)

        if not channel or not isinstance(channel, nextcord.TextChannel):
            await interaction.response.send_message(
                "Cannot find the promotion channel. Check PROMOTION_CHANNEL_ID in .env.",
                ephemeral=True,
            )
            return

        duration_seconds = _parse_duration(duration)

        if duration_seconds <= 0:
            await interaction.response.send_message("Invalid duration format. Use e.g. `1d2h30m0s`.", ephemeral=True)
            return

        expiration = nextcord.utils.utcnow() + datetime.timedelta(seconds=duration_seconds)

        embed = nextcord.Embed(
            title="🔔 Promotion 🔔",
            description=(
                f"> ```{target}```\n"
                f"**Discount**: __-{discount}%__\n"
                f"**Ends in:** <t:{int(expiration.timestamp())}:R>\n"
                f"**Expires:** `{expiration.strftime('%Y-%m-%d %H:%M:%S')}`"
            ),
            color=nextcord.Color.gold(),
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.set_footer(text=FOOTER_TEXT)

        confirm = nextcord.Embed(
            title="PROMOTION CREATED!",
            description="",
            color=0x000000,
            timestamp=nextcord.utils.utcnow(),
        )
        confirm.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=confirm, ephemeral=True)

        promo_message = await channel.send(content="||@everyone @here||", embed=embed)

        await asyncio.sleep(duration_seconds)

        embed.description = (
            f"🛑 **PROMOTION ENDED** 🛑\n"
            f"> **What was on sale:** ```{target}```\n"
            f"> **Discount:** __-{discount}%__"
        )
        embed.set_footer(text=f"{FOOTER_TEXT} — Promotion ended")

        try:
            await promo_message.edit(embed=embed)
        except nextcord.HTTPException:
            pass


def _parse_duration(duration_str):
    duration_str = duration_str.lower()
    try:
        days, rest = duration_str.split("d")
    except ValueError:
        return 0

    hours, minutes, seconds = 0, 0, 0

    if "h" in rest:
        hours, rest = rest.split("h")
    if "m" in rest:
        minutes, rest = rest.split("m")
    if "s" in rest:
        seconds = rest.replace("s", "")

    try:
        return int(days) * 86400 + int(hours) * 3600 + int(minutes) * 60 + int(seconds or 0)
    except ValueError:
        return 0


def setup(bot):
    bot.add_cog(AnnouncementsCog(bot))

import datetime
import random

import nextcord
from nextcord import utils
from nextcord.ext import commands

from config import FOOTER_TEXT

DISCOUNT_CHANCE = 35

last_drop_usage = {}
last_discount_win = {}


class DropCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="daily_drop",
        description="Try your luck and win a discount!",
    )
    async def drop_command(self, interaction: nextcord.Interaction):
        user = interaction.user

        last_usage_time = last_drop_usage.get(user.id)
        last_win_time = last_discount_win.get(user.id)

        if last_usage_time is not None and (utils.utcnow() - last_usage_time) < datetime.timedelta(days=1):
            remaining = datetime.timedelta(days=1) - (utils.utcnow() - last_usage_time)
            embed = nextcord.Embed(
                title="⌛ Wait! ⌛",
                description=(
                    f"> {interaction.user.mention} You can use the \"drop\" command again "
                    f"<t:{int((utils.utcnow() + remaining).timestamp())}:R>\n"
                ),
                color=nextcord.Color.blue(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if last_win_time is not None and (utils.utcnow() - last_win_time) < datetime.timedelta(days=3):
            remaining = datetime.timedelta(days=3) - (utils.utcnow() - last_win_time)
            embed = nextcord.Embed(
                title="⌛ Wait! ⌛",
                description=(
                    f"> {interaction.user.mention} You already won a discount! "
                    f"You can try again <t:{int((utils.utcnow() + remaining).timestamp())}:R>\n"
                ),
                color=nextcord.Color.blue(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        last_drop_usage[user.id] = utils.utcnow()
        roll = random.randint(1, 100)

        if roll <= DISCOUNT_CHANCE:
            discount = "-10%"
            expiration = utils.utcnow() + datetime.timedelta(days=3)
            embed = nextcord.Embed(
                title="🎉 Congratulations! 🎉",
                description=(
                    f"> {interaction.user.mention} You've won a __{discount}__ discount "
                    f"valid until <t:{int(expiration.timestamp())}:R>\n"
                    f"> Expires on `{expiration.strftime('%Y-%m-%d %H:%M:%S')}`!"
                ),
                color=nextcord.Color.green(),
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed)
            last_discount_win[user.id] = utils.utcnow()
        else:
            embed = nextcord.Embed(
                title="😞 Too bad! 😞",
                description=(
                    f"> {interaction.user.mention} You didn't win a discount this time!\n"
                    f"> Try again tomorrow :D"
                ),
                color=nextcord.Color.red(),
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(DropCog(bot))
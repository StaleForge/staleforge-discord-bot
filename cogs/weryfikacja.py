import random

import nextcord
from nextcord import utils
from nextcord.ui import Modal, TextInput
from nextcord.ext import commands

from config import FOOTER_TEXT, VERIFIED_ROLE_ID, MEMBER_ROLE_ID, RULES_CHANNEL_ID


class VerifyModal(Modal):
    def __init__(self):
        super().__init__("Verification!", timeout=None)

        a = random.randint(1, 10)
        b = random.randint(1, 10)
        self.correct_answer = a + b

        self.answer_input = TextInput(
            label=f"Solve: What is {a} + {b}?",
            min_length=1,
            max_length=3,
            required=True,
            placeholder="Enter the answer (numbers only)!",
        )
        self.add_item(self.answer_input)

    async def callback(self, interaction: nextcord.Interaction):
        user = interaction.user

        if VERIFIED_ROLE_ID in [r.id for r in user.roles]:
            embed = nextcord.Embed(title="Already verified!", color=nextcord.Color.blue(), timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            user_answer = int(self.answer_input.value)
        except ValueError:
            embed = nextcord.Embed(
                title="You must enter a number!",
                description="`Try again!`",
                color=nextcord.Color.red(),
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_answer != self.correct_answer:
            embed = nextcord.Embed(
                title="Wrong answer!",
                description="`Try again!`",
                color=nextcord.Color.red(),
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        verified_role = user.guild.get_role(VERIFIED_ROLE_ID)
        member_role = user.guild.get_role(MEMBER_ROLE_ID)

        if verified_role:
            await user.add_roles(verified_role)
        if member_role:
            await user.add_roles(member_role)

        success = nextcord.Embed(title="Verified! ✅", timestamp=utils.utcnow())
        success.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=success, ephemeral=True)

        dm_embed = nextcord.Embed(
            title="✅ Verification Complete!",
            description="> **You have been successfully verified!** 😄",
            timestamp=utils.utcnow(),
            color=nextcord.Color.blue(),
        )
        dm_embed.set_footer(text=FOOTER_TEXT)

        try:
            await user.send(embed=dm_embed)
        except nextcord.Forbidden:
            pass


class VerificationView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="✅ Verify!", custom_id="verify_button", style=nextcord.ButtonStyle.blurple)
    async def verify(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(VerifyModal())


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def initialize(self, ctx):
        rules_channel = ctx.guild.get_channel(RULES_CHANNEL_ID)
        rules_mention = rules_channel.mention if rules_channel else "#rules"

        embed = nextcord.Embed(
            title="✅ Verification!",
            description=(
                f"> **WELCOME!**\n"
                f"> To verify, click the button below!\n\n"
                f"> By clicking below you __accept the rules__\n"
                f"> found at {rules_mention}"
            ),
            color=nextcord.Color.blue(),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await ctx.send(embed=embed, view=VerificationView())


def setup(bot):
    bot.add_cog(Verification(bot))
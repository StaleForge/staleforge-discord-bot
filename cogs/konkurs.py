import datetime
import random
import typing

import nextcord
from nextcord import utils
from nextcord.ui import Button
from nextcord.ext import commands, application_checks

from config import FOOTER_TEXT, GIVEAWAY_CHANNEL_ID, REROLL_ROLE_IDS

import pytz


class GiveawayButton(Button):
    def __init__(self, giveaway_message_id, required_roles=None):
        super().__init__(style=nextcord.ButtonStyle.primary, label="Join!", emoji="🎉")
        self.giveaway_message_id = giveaway_message_id
        self.users = []
        self.leave_button = LeaveGiveawayButton(giveaway_message_id, self.users)
        self.participants_button = ParticipantsButton(giveaway_message_id, self.users)
        self.required_roles = required_roles

    async def callback(self, interaction: nextcord.Interaction):
        view = nextcord.ui.View()
        view.add_item(self.leave_button)

        user_roles = [role.id for role in interaction.user.roles]
        if self.required_roles and not all(role in user_roles for role in self.required_roles):
            embed = nextcord.Embed(
                title="You don't meet the required roles!",
                description="You need specific roles to join this giveaway.",
                color=0xFF0000,
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if interaction.user not in self.users:
            self.users.append(interaction.user)
            embed = nextcord.Embed(title="Joined the giveaway!", description="", color=0x00A822, timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True, view=view)
        else:
            embed = nextcord.Embed(title="You already joined!", description="", color=0xFFCA0A, timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True, view=view)


class LeaveGiveawayButton(Button):
    def __init__(self, giveaway_message_id, users):
        super().__init__(style=nextcord.ButtonStyle.danger, label="Leave", emoji="🚫")
        self.giveaway_message_id = giveaway_message_id
        self.users = users

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user in self.users:
            self.users.remove(interaction.user)
            embed = nextcord.Embed(title="Left the giveaway!", description="", color=0xFF0000, timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(title="You're not in this giveaway!", description="", color=0xFFCA0A, timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class ParticipantsButton(nextcord.ui.Button):
    def __init__(self, giveaway_message_id, users):
        super().__init__(style=nextcord.ButtonStyle.secondary, label="Participants", emoji="👥")
        self.giveaway_message_id = giveaway_message_id
        self.users = users

    async def callback(self, interaction: nextcord.Interaction):
        mentions = ", ".join(user.mention for user in self.users) or "None"
        embed = nextcord.Embed(title="Current participants:", description=mentions, color=0x00A822, timestamp=utils.utcnow())
        embed.add_field(name="Participant count:", value=f"`{len(self.users)}`")
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class RerollButton(nextcord.ui.Button):
    def __init__(self, giveaway_message_id, users, prize, num_winners, required_roles):
        super().__init__(style=nextcord.ButtonStyle.secondary, label="Reroll", emoji="🔄")
        self.giveaway_message_id = giveaway_message_id
        self.users = users
        self.prize = prize
        self.num_winners = num_winners
        self.required_roles = required_roles

    async def callback(self, interaction: nextcord.Interaction):
        if not any(role.id in REROLL_ROLE_IDS for role in interaction.user.roles):
            embed = nextcord.Embed(title="You're not authorized to reroll!", description="", color=0xFF0000, timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not self.users:
            embed = nextcord.Embed(title="No participants in the giveaway!", description="", color=0xFFCA0A, timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        winners = random.sample(self.users, k=min(self.num_winners, len(self.users)))
        winners_str = ", ".join(w.mention for w in winners)

        await interaction.response.send_message(
            f"🎉 Congratulations {winners_str}! You won: 🎁 ***{self.prize}!*** 🎁 Open a ticket to claim!🎉"
        )

        for winner in winners:
            try:
                await winner.send(
                    f"🎉 Congratulations! You won ***{self.prize}*** in a giveaway! Open a ticket to claim!🎉"
                )
            except nextcord.Forbidden:
                pass

        new_embed = self._build_ended_embed(winners_str, interaction.guild)
        giveaway_message = await interaction.channel.fetch_message(self.giveaway_message_id)
        await giveaway_message.edit(embed=new_embed)

    def _build_ended_embed(self, winners_str, guild):
        embed = nextcord.Embed(title="🎉 GIVEAWAY ENDED! 🎉", description="", color=0xFF0000, timestamp=utils.utcnow())
        embed.add_field(name="Winner:", value=winners_str, inline=False)
        embed.add_field(name="Prize:", value=f"🎁 ***{self.prize}*** 🎁", inline=False)
        embed.add_field(name="Max winners:", value=f"`{self.num_winners}`", inline=False)
        embed.add_field(name="Participants:", value=f"`{len(self.users)}`", inline=False)
        if self.required_roles:
            role_mentions = ", ".join(
                guild.get_role(rid).mention for rid in self.required_roles if guild.get_role(rid)
            )
            embed.add_field(name="Required roles:", value=role_mentions, inline=False)
        else:
            embed.add_field(name="Who could participate:", value="`Everyone!`", inline=False)
        embed.set_footer(text=FOOTER_TEXT)
        return embed


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="giveaway", description="Creates a giveaway!")
    @application_checks.has_permissions(administrator=True)
    async def giveaway(
        self,
        interaction: nextcord.Interaction,
        duration: str,
        num_winners: int,
        *,
        prize: str,
        required_roles: typing.Optional[str] = None,
    ):
        tz = pytz.timezone("Europe/Warsaw")
        end_time = datetime.datetime.now(tz) + datetime.timedelta(seconds=self._parse_time(duration))
        channel = self.bot.get_channel(GIVEAWAY_CHANNEL_ID)

        if not channel:
            await interaction.response.send_message(
                "Cannot find the giveaway channel. Check GIVEAWAY_CHANNEL_ID in .env.",
                ephemeral=True,
            )
            return

        embed = nextcord.Embed(title="🎉 GIVEAWAY! 🎉", description="", color=0x000000, timestamp=utils.utcnow())
        embed.add_field(name="Prize:", value=f"🎁 ***{prize}*** 🎁", inline=False)
        embed.add_field(name="Created by:", value=interaction.user.mention, inline=False)
        embed.add_field(name="Max winners:", value=f"`{num_winners}`", inline=False)
        embed.add_field(name="Time remaining:", value=f"<t:{int(end_time.timestamp())}:R>\n", inline=True)
        embed.add_field(name="Ends at:", value=f"`{end_time.strftime('%Y-%m-%d %H:%M:%S')}\n`", inline=True)
        embed.set_footer(text=FOOTER_TEXT)

        parsed_role_ids = None
        if required_roles:
            role_mentions = [role.strip() for role in required_roles.split(",")]
            embed.add_field(name="Required roles:", value=", ".join(role_mentions), inline=False)
            try:
                parsed_role_ids = [int(r.strip().strip("<@&").strip(">")) for r in role_mentions]
            except ValueError:
                parsed_role_ids = None
        else:
            embed.add_field(name="Who can participate:", value="`Everyone!`", inline=False)

        embed.add_field(name="Click ( 🎉 Join! ) to enter the giveaway!", value="", inline=False)
        message = await channel.send("||@everyone @here||", embed=embed)

        join_button = GiveawayButton(message.id, required_roles=parsed_role_ids)
        users = join_button.users
        participants_button = ParticipantsButton(message.id, users)
        reroll_button = RerollButton(message.id, users, prize=prize, num_winners=num_winners, required_roles=parsed_role_ids)

        view = nextcord.ui.View(timeout=None)
        view.add_item(join_button)
        view.add_item(participants_button)
        view.add_item(reroll_button)
        await message.edit(view=view)

        confirm_embed = nextcord.Embed(title="GIVEAWAY CREATED!", description="", color=0x000000, timestamp=utils.utcnow())
        confirm_embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

        await nextcord.utils.sleep_until(end_time)

        view.remove_item(join_button)
        view.remove_item(participants_button)
        await message.edit(view=view)

        if not users:
            ended_embed = nextcord.Embed(title="🎉 GIVEAWAY ENDED! 🎉", description="", color=0xFF0000, timestamp=utils.utcnow())
            ended_embed.add_field(name="Prize was:", value=f"🎁 ***{prize}*** 🎁", inline=False)
            ended_embed.add_field(name="Max winners:", value=f"`{num_winners}`", inline=False)
            ended_embed.add_field(name="Participants:", value="`Nobody joined!`", inline=False)
            ended_embed.set_footer(text=FOOTER_TEXT)
            await message.edit(content="||@everyone @here||", embed=ended_embed)
        else:
            actual_winners = min(num_winners, len(users))
            winners = random.sample(users, actual_winners)
            winners_str = ", ".join(w.mention for w in winners)

            ended_embed = nextcord.Embed(title="🎉 GIVEAWAY ENDED! 🎉", description="", color=0xFF0000, timestamp=utils.utcnow())
            ended_embed.add_field(name="Winner:", value=winners_str, inline=False)
            ended_embed.add_field(name="Prize:", value=f"🎁 ***{prize}*** 🎁", inline=False)
            ended_embed.add_field(name="Max winners:", value=f"`{num_winners}`", inline=False)
            ended_embed.add_field(name="Participants:", value=f"`{len(users)}`", inline=False)
            ended_embed.set_footer(text=FOOTER_TEXT)
            await message.edit(content="||@everyone @here||", embed=ended_embed)

            await channel.send(f"🎉 Congratulations {winners_str}! You won: 🎁 ***{prize}!*** 🎁 Open a ticket to claim!🎉")

            for winner in winners:
                try:
                    await winner.send(f"🎉 You won ***{prize}*** in a giveaway! Open a ticket to claim!🎉")
                except nextcord.Forbidden:
                    pass

    @staticmethod
    def _parse_time(time_str):
        time_converter = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = time_str[-1]
        return int(time_str[:-1]) * time_converter.get(unit, 1)


def setup(bot):
    bot.add_cog(Giveaway(bot))
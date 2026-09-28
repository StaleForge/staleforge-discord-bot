import datetime

import nextcord
from nextcord import utils
from nextcord.ext import commands, application_checks

from config import FOOTER_TEXT, POLL_CHANNEL_ID


class PollOption:
    def __init__(self, label):
        self.label = label
        self.votes = {}

    def add_vote(self, user_id):
        if user_id not in self.votes:
            self.votes[user_id] = 1
        else:
            self.votes[user_id] += 1

    def remove_vote(self, user_id):
        if user_id in self.votes:
            self.votes[user_id] -= 1
            if self.votes[user_id] == 0:
                del self.votes[user_id]


class AdvancedPoll(nextcord.ui.View):
    def __init__(self, question, options, end_time):
        super().__init__(timeout=None)
        self.question = question
        self.options = options
        self.is_ended = False
        self.total_votes = 0
        self.winner_percentage = 0
        self.end_time = end_time

        for option in self.options:
            button = PollButton(option)
            button.callback = lambda i, b=button: self.handle_vote(i, b)
            self.add_item(button)

    async def handle_vote(self, interaction: nextcord.Interaction, button: "PollButton"):
        if self.is_ended:
            embed = nextcord.Embed(
                title="The poll has ended, you can no longer vote!",
                description="",
                color=0xFFA200,
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user_id = str(interaction.user.id)

        for option in self.options:
            if option.label == button.option.label:
                if user_id not in option.votes:
                    for o in self.options:
                        o.remove_vote(user_id)
                    option.add_vote(user_id)
                    button.label = f"{option.label} ({option.votes[user_id]} votes)"
                    embed = nextcord.Embed(
                        title="Your vote has been cast!",
                        description="",
                        color=0x00FF9D,
                        timestamp=utils.utcnow(),
                    )
                    embed.set_footer(text=FOOTER_TEXT)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    option.remove_vote(user_id)
                    button.label = option.label
                    embed = nextcord.Embed(
                        title="Your vote has been removed!",
                        description="",
                        color=0xFF0000,
                        timestamp=utils.utcnow(),
                    )
                    embed.set_footer(text=FOOTER_TEXT)
                    await interaction.response.send_message(embed=embed, ephemeral=True)

        self.total_votes = sum(sum(option.votes.values()) for option in self.options)
        await self.message.edit(embed=self.create_embed())

    def create_embed(self):
        total_votes = sum(sum(option.votes.values()) for option in self.options)

        embed = nextcord.Embed(
            title="📊 POLL 📊",
            description=f"**Question:** ```{self.question}```",
            timestamp=utils.utcnow(),
        )
        embed.add_field(name="Time remaining:", value=f"<t:{int(self.end_time.timestamp())}:R>\n")
        embed.add_field(name="Ends at:", value=f"`{self.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n`")
        embed.set_footer(text=FOOTER_TEXT)

        if self.is_ended:
            if total_votes == 0:
                embed.clear_fields()
                embed.add_field(
                    name="No votes cast:",
                    value="`Nobody participated in the poll!`",
                    inline=False,
                )
                embed.title = "📊 POLL ENDED 📊"
            else:
                embed.clear_fields()
                max_votes = max(sum(option.votes.values()) for option in self.options)
                winners = [option.label for option in self.options if sum(option.votes.values()) == max_votes]
                embed.add_field(
                    name="Poll results:",
                    value=f"***Winning choice:*** `{', '.join(winners)}`",
                    inline=False,
                )
                embed.add_field(name="Total voters:", value=f"`{total_votes}`", inline=False)
                if total_votes != 0:
                    self.winner_percentage = (max_votes / total_votes) * 100
                    embed.add_field(
                        name="Winner percentage:",
                        value=f"`{self.winner_percentage:.2f}%`",
                        inline=False,
                    )
                embed.title = "📊 POLL ENDED 📊"
        else:
            if total_votes == 0:
                embed.add_field(
                    name="No votes yet:",
                    value="`Nobody has voted yet, be the first!`",
                    inline=False,
                )
            else:
                for option in self.options:
                    percentage = (sum(option.votes.values()) / total_votes) * 100
                    embed.add_field(
                        name=f"{option.label}:",
                        value=f"`Votes: {sum(option.votes.values())} ({percentage:.2f}%)`",
                        inline=False,
                    )

        return embed

    def end_poll(self):
        self.is_ended = True
        total_votes = sum(sum(option.votes.values()) for option in self.options)
        if total_votes != 0:
            self.winner_percentage = (
                max(sum(option.votes.values()) for option in self.options) / total_votes
            ) * 100


class PollButton(nextcord.ui.Button["AdvancedPoll"]):
    def __init__(self, option: PollOption):
        super().__init__(style=nextcord.ButtonStyle.primary, label=option.label)
        self.option = option


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="poll", description="Creates a poll!")
    @application_checks.has_permissions(administrator=True)
    async def poll(self, interaction: nextcord.Interaction, duration: str, question: str, options: str):
        options_list = options.split(",")
        if len(options_list) < 2:
            embed = nextcord.Embed(
                title="You must provide at least 2 options for the poll!",
                description="",
                color=0xFF6600,
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        poll_options = [PollOption(opt.strip()) for opt in options_list]
        end_time = utils.utcnow() + datetime.timedelta(seconds=self._parse_time(duration))
        poll_view = AdvancedPoll(question, poll_options, end_time)
        embed = poll_view.create_embed()

        channel = self.bot.get_channel(POLL_CHANNEL_ID)

        if channel is not None:
            confirm_embed = nextcord.Embed(
                title="POLL CREATED SUCCESSFULLY!",
                description="",
                color=0x000000,
                timestamp=utils.utcnow(),
            )
            confirm_embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            message = await channel.send("||@everyone @here||", embed=embed, view=poll_view)
            poll_view.message = message
            await nextcord.utils.sleep_until(end_time)
            poll_view.end_poll()
            await message.edit(embed=poll_view.create_embed())
        else:
            await interaction.response.send_message(
                "Cannot find the poll channel. Check POLL_CHANNEL_ID in your .env file.",
                ephemeral=True,
            )

    @staticmethod
    def _parse_time(time_str):
        time_converter = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = time_str[-1]
        return int(time_str[:-1]) * time_converter.get(unit, 1)


def setup(bot):
    bot.add_cog(Poll(bot))
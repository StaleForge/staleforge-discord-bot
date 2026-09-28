import datetime
import string
import random

import nextcord
from nextcord import utils
from nextcord.ui import View
from nextcord.ext import commands, application_checks

from config import (
    FOOTER_TEXT, RULES_CHANNEL_ID, TICKET_ALERT_CHANNEL_ID,
    TICKET_STAFF_ROLE_IDS, TICKET_LOG_CATEGORY_NAME,
)


class ConfirmDeleteLogView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="✅ Yes", style=nextcord.ButtonStyle.red, custom_id="log_confirm_delete")
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="Ticket log deleted!",
            description="`Deleting...`",
            color=nextcord.Color.dark_green(),
            timestamp=utils.utcnow(),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.channel.delete()

    @nextcord.ui.button(label="❌ No", style=nextcord.ButtonStyle.secondary, custom_id="log_cancel_delete")
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Deletion cancelled!", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.edit_message(embed=embed, view=None)


class DeleteLogButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="📁 Delete Log", style=nextcord.ButtonStyle.danger, custom_id="logdel")
    async def delete_log(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="Are you sure you want to delete this ticket log?",
            color=nextcord.Color.red(),
            timestamp=utils.utcnow(),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed, view=ConfirmDeleteLogView(), ephemeral=True)


class ConfirmCloseView(nextcord.ui.View):
    def __init__(self, original_embed):
        super().__init__(timeout=None)
        self.original_embed = original_embed

    @nextcord.ui.button(label="✅ Yes", style=nextcord.ButtonStyle.red, custom_id="ticket_close_confirm")
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        category = nextcord.utils.get(interaction.guild.categories, name=TICKET_LOG_CATEGORY_NAME)
        channel = interaction.channel
        dt_obj = utils.utcnow().date()

        closed_embed = nextcord.Embed(
            title="Ticket closed!",
            description="Thank you for reaching out!",
            color=nextcord.Color.brand_green(),
            timestamp=utils.utcnow(),
        )
        closed_embed.add_field(name="Closed on:", value=f"`{dt_obj}`")
        closed_embed.set_footer(text=FOOTER_TEXT)

        confirm_embed = nextcord.Embed(
            title="Ticket closed successfully!",
            color=nextcord.Color.dark_green(),
            timestamp=utils.utcnow(),
        )
        confirm_embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.edit_message(embed=confirm_embed, view=None)

        msg = await channel.send(embed=closed_embed, view=DeleteLogButton())

        if category:
            await channel.edit(category=category, sync_permissions=True)
        await channel.set_permissions(channel.guild.default_role, view_channel=False, send_messages=False)
        await msg.pin()

    @nextcord.ui.button(label="❌ No", style=nextcord.ButtonStyle.secondary, custom_id="ticket_close_cancel")
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Close cancelled!", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.edit_message(embed=embed, view=None)


class TicketControlView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed = False
        self.claimed_by = None

    def _has_staff_role(self, user: nextcord.Member) -> bool:
        return any(role.id in TICKET_STAFF_ROLE_IDS for role in user.roles)

    @nextcord.ui.button(label="❌ Close ticket", style=nextcord.ButtonStyle.secondary, custom_id="ticket_close")
    async def close(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="Are you sure you want to close this ticket?",
            color=nextcord.Color.red(),
            timestamp=utils.utcnow(),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed, view=ConfirmCloseView(embed), ephemeral=True)

    @nextcord.ui.button(label="👊 Claim", style=nextcord.ButtonStyle.blurple, custom_id="ticket_claim")
    async def claim(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        user = interaction.user

        if self.claimed:
            embed = nextcord.Embed(
                title="Error",
                description="This ticket is already claimed by another staff member!",
                color=nextcord.Color.dark_red(),
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not self._has_staff_role(user):
            embed = nextcord.Embed(
                title="Error",
                description="Only staff members can claim tickets!",
                color=nextcord.Color.dark_red(),
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.claimed = True
        self.claimed_by = user

        success = nextcord.Embed(
            title="Ticket claimed!",
            description="Handle the user with care! 😁",
            color=nextcord.Color.blue(),
            timestamp=utils.utcnow(),
        )
        success.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=success, ephemeral=True)

        info = nextcord.Embed(
            title="Operator assigned!",
            description=f"Your operator is now {user.mention}!",
            color=nextcord.Color.og_blurple(),
            timestamp=utils.utcnow(),
        )
        info.set_footer(text=FOOTER_TEXT)
        await interaction.channel.send(embed=info)


ticket_counts = {}
ticket_cooldown = datetime.timedelta(minutes=5)


def _generate_ticket_id(length=8):
    return "".join(random.choice(string.digits) for _ in range(length))


class TicketSelectView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.initial_placeholder = "📫 | staleforge.dev — Select a ticket category!"
        self.select = nextcord.ui.Select(
            placeholder=self.initial_placeholder,
            custom_id="ticket_select",
            options=[
                nextcord.SelectOption(label="HELP", value="01", emoji="✅", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 1", value="02", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 2", value="03", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 3", value="04", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 4", value="05", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 5", value="06", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 6", value="07", emoji="💱", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 7", value="08", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 8", value="09", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 9", value="10", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 10", value="11", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Category 11", value="12", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="OTHER", value="13", emoji="✨", description="made by staleforge ~2023"),
            ],
        )
        self.select.callback = self._on_select
        self.add_item(self.select)

    async def _on_select(self, interaction: nextcord.Interaction):
        guild = interaction.guild

        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
            interaction.user: nextcord.PermissionOverwrite(view_channel=True),
            guild.me: nextcord.PermissionOverwrite(view_channel=True),
        }
        for role_id in TICKET_STAFF_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(view_channel=True)

        category_mapping = {
            "01": "( Help )", "02": "( Category 1 )", "03": "( Category 2 )",
            "04": "( Category 3 )", "05": "( Category 4 )", "06": "( Category 5 )",
            "07": "( Category 6 )", "08": "( Category 7 )", "09": "( Category 8 )",
            "10": "( Category 9 )", "11": "( Category 10 )", "12": "( Category 11 )",
            "13": "( Other )",
        }

        category_key = interaction.data["values"][0]
        if category_key not in category_mapping:
            return

        category_name = category_mapping[category_key]
        user_id = interaction.user.id
        category = nextcord.utils.get(guild.categories, name=category_name)

        if category is None:
            await interaction.response.send_message(content="Category not found!", ephemeral=True)
            return

        if user_id in ticket_counts:
            last_ticket_time = ticket_counts[user_id]
            if utils.utcnow() - last_ticket_time < ticket_cooldown:
                embed = nextcord.Embed(
                    title="Please wait before opening another ticket!",
                    description="> You can open a new ticket after **5 minutes**!",
                    color=nextcord.Color.red(),
                )
                embed.set_footer(text=FOOTER_TEXT)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.select.placeholder = self.initial_placeholder
                await interaction.message.edit(view=self)
                return

        ticket_id = _generate_ticket_id()
        channel = await guild.create_text_channel(
            f"{ticket_id}-ticket",
            category=category,
            overwrites=overwrites,
        )
        ticket_counts[user_id] = utils.utcnow()

        opened_embed = nextcord.Embed(
            title=f"Opened ticket - <#{channel.id}>",
            color=0x07B404,
            timestamp=utils.utcnow(),
        )
        opened_embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=opened_embed, ephemeral=True)

        welcome_embed = nextcord.Embed(
            title="WELCOME!",
            description=f"> Ticket ID: `{ticket_id}`",
            color=0x000000,
            timestamp=utils.utcnow(),
        )
        welcome_embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None,
        )
        welcome_embed.add_field(name="Created:", value=f"<t:{int(utils.utcnow().timestamp())}:R>\n")
        welcome_embed.add_field(name="SOMEONE WILL BE WITH YOU SHORTLY!", value="`~please wait patiently :)`", inline=False)
        welcome_embed.set_footer(text=FOOTER_TEXT)

        pinned_msg = await channel.send(embed=welcome_embed, view=TicketControlView())
        await pinned_msg.pin()

        alert_channel = guild.get_channel(TICKET_ALERT_CHANNEL_ID)
        if alert_channel:
            alert_embed = nextcord.Embed(
                title="⚠️ New ticket created! ⚠️",
                description=f"New ticket at {channel.mention}, category: {category.name}!",
                color=nextcord.Color.purple(),
                timestamp=utils.utcnow(),
            )
            alert_embed.set_footer(text=FOOTER_TEXT)
            await alert_channel.send(content="||@here||", embed=alert_embed)

        self.select.placeholder = self.initial_placeholder
        await interaction.message.edit(view=self)


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticket")
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx):
        rules_channel = ctx.guild.get_channel(RULES_CHANNEL_ID)
        rules_mention = rules_channel.mention if rules_channel else "#rules"

        embed = nextcord.Embed(title="🎫 staleforge.dev ▸ Tickets!", color=0x000000)
        embed.add_field(
            name="ABOUT TICKETS!",
            value=(
                f"> • Spamming tickets will result in a **permanent ban**!\n"
                f"> • Staff response hours: `10:00–22:00`!\n"
                f"> • By opening a ticket you accept the __server rules__ at {rules_mention}!"
            ),
            inline=False,
        )
        embed.set_footer(text=FOOTER_TEXT)
        view = TicketSelectView()
        await ctx.send(embed=embed, view=view)

    @nextcord.slash_command(name="close", description="Closes a ticket!")
    async def close(self, interaction: nextcord.Interaction):
        channel = interaction.channel
        if not channel.name.endswith("-ticket"):
            error = nextcord.Embed(
                title="Error",
                description="This command can only be used in ticket channels!",
                color=nextcord.Color.red(),
                timestamp=utils.utcnow(),
            )
            error.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=error, ephemeral=True)
            return

        embed = nextcord.Embed(
            title="Are you sure you want to close this ticket?",
            color=nextcord.Color.red(),
            timestamp=utils.utcnow(),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed, view=ConfirmCloseView(embed), ephemeral=True)

    @nextcord.slash_command(name="change_operator", description="Changes the ticket operator!")
    @application_checks.has_permissions(administrator=True)
    async def change_operator(self, interaction: nextcord.Interaction, new_operator: nextcord.Member):
        channel = interaction.channel
        if not channel.name.endswith("-ticket"):
            error = nextcord.Embed(
                title="Error",
                description="This command can only be used in ticket channels!",
                color=nextcord.Color.red(),
                timestamp=utils.utcnow(),
            )
            error.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=error, ephemeral=True)
            return

        success = nextcord.Embed(
            title="Operator changed!",
            description=f"New operator: {new_operator.mention}! 😁",
            color=nextcord.Color.blue(),
            timestamp=utils.utcnow(),
        )
        success.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=success, ephemeral=True)

        info = nextcord.Embed(
            title="Operator changed!",
            description=f"Your new operator is {new_operator.mention}!",
            color=nextcord.Color.blurple(),
            timestamp=utils.utcnow(),
        )
        info.set_footer(text=FOOTER_TEXT)
        await interaction.channel.send(embed=info)


def setup(bot):
    bot.add_cog(Ticket(bot))
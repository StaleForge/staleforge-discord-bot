import nextcord
from nextcord import utils
from nextcord.ext import commands, application_checks

from config import FOOTER_TEXT, PRICING_CHANNEL_ID


class CennikView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.initial_placeholder = "💸 | staleforge.dev — Select a service!"
        self.select = nextcord.ui.Select(
            placeholder=self.initial_placeholder,
            custom_id="pricing_select",
            options=[
                nextcord.SelectOption(label="Service 1", value="01", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 2", value="02", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 3", value="03", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 4", value="04", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 5", value="05", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 6", value="06", emoji="💱", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 7", value="07", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 8", value="08", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 9", value="09", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 10", value="10", emoji="🛒", description="made by staleforge ~2023"),
                nextcord.SelectOption(label="Service 11", value="11", emoji="🛒", description="made by staleforge ~2023"),
            ],
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: nextcord.Interaction):
        value = interaction.data["values"][0]

        embed_data = {
            "01": self._service_embed, "02": self._service_embed, "03": self._service_embed,
            "04": self._service_embed, "05": self._service_embed, "06": self._service_embed,
            "07": self._service_embed, "08": self._service_embed, "09": self._service_embed,
            "10": self._service_embed, "11": self._service_embed,
        }

        builder = embed_data.get(value)
        if builder:
            label = None
            for option in self.select.options:
                if option.value == value:
                    label = option.label
                    break
            embed = builder(label or f"Service {value}")
            self.select.placeholder = self.initial_placeholder
            await interaction.message.edit(view=self)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @staticmethod
    def _service_embed(service_name):
        embed = nextcord.Embed(
            title="========================",
            description=f"» {service_name}",
            color=0x000000,
        )
        embed.add_field(
            name="staleforge.dev",
            value=(
                "> This is an example service listing.\n"
                "> Configure your own services and pricing here.\n"
                "> Visit **staleforge.dev** for more info."
            ),
            inline=False,
        )
        embed.set_footer(text=FOOTER_TEXT)
        return embed


class Cennik(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pricing")
    @commands.has_permissions(administrator=True)
    async def cennik(self, ctx):
        target_channel = ctx.guild.get_channel(PRICING_CHANNEL_ID)
        channel_mention = target_channel.mention if target_channel else "#pricing"

        embed = nextcord.Embed(title="💸 staleforge.dev ▸ Pricing!", color=nextcord.Color.blue())
        embed.add_field(
            name="💡 __PLACING ORDERS__",
            value=f"> To place an order, go to {channel_mention} and create a ticket!",
            inline=False,
        )
        embed.add_field(
            name="💸 __OUR OFFERS__",
            value=(
                "> `-` Service 1\n"
                "> `-` Service 2\n"
                "> `-` Service 3\n"
                "> `-` Service 4\n"
                "> `-` Service 5\n"
                "> `-` Service 6\n"
                "> `-` Service 7\n"
                "> `-` Service 8\n"
                "> `-` Service 9\n"
                "> `-` Service 10\n"
                "> `-` Service 11\n\n"
                "> **staleforge.dev** — Staff will respond ASAP! :)"
            ),
            inline=False,
        )
        embed.set_footer(text=FOOTER_TEXT)
        view = CennikView()
        await ctx.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Cennik(bot))
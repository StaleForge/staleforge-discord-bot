import nextcord
from nextcord.ext import commands, application_checks
from nextcord import utils

from config import FOOTER_TEXT

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="Wyświetla listę wszystkich dostępnych komend bota.")
    @application_checks.has_permissions(administrator=True)
    async def help_command(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="🛠️ staleforge.dev ▸ Panel Pomocy",
            description="> Poniżej znajduje się lista wszystkich dostępnych komend administracyjnych, przypisanych do odpowiednich systemów bota.",
            color=nextcord.Color.blue(),
            timestamp=utils.utcnow()
        )
        
        embed.add_field(
            name="🎫 System Ticketów",
            value=(
                "`/ticket` - Wysyła panel wyboru ticketów\n"
                "`/close` - Zamyka otwarty ticket"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎉 System Konkursów (Giveaways)",
            value=(
                "`/giveaway` - Tworzy i wysyła nowy konkurs\n"
                "`/reroll` - Losuje nowego zwycięzcę konkursu\n"
                "`/end` - Natychmiast kończy trwający konkurs"
            ),
            inline=False
        )

        embed.add_field(
            name="🎨 Edytor Embedów",
            value=(
                "`/embed_create` - Otwiera UI (Modal) do stworzenia customowego Embedu\n"
                "`/embed_edit` - Otwiera UI do edycji już wysłanej wiadomości Embed"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📣 System Promocji i Ogłoszeń",
            value=(
                "`/sale` - Tworzy czasową promocję i pinguje odpowiednie role\n"
                "`/promo` - Generuje ogłoszenie o trwającej promocji"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠️ Inne Narzędzia",
            value=(
                "`/pricing` - Wysyła skonfigurowany panel cennika (w #pricing)\n"
                "`/verify` - Wysyła panel weryfikacji captcha dla nowych graczy\n"
                "`/drop` - (O ile skonfigurowane) pozwala losować dropy/zniżki\n"
                "`/poll` - Tworzy zaawansowaną ankietę"
            ),
            inline=False
        )

        embed.set_footer(text=FOOTER_TEXT)
        
        # Wysłanie panelu tylko dla osoby wywołującej
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Help(bot))

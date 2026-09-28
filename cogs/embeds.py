import nextcord
from nextcord import utils
from nextcord.ui import View, Select, Modal, TextInput
from nextcord.ext import commands, application_checks

from config import FOOTER_TEXT


class EmbedModalChannel(Modal):
    def __init__(self):
        super().__init__("Send embed to channel!", timeout=None)

        self.channel_ids = TextInput(
            label="Channel IDs (comma separated)",
            min_length=1,
            max_length=4000,
            required=False,
            placeholder="Enter channel IDs separated by commas!",
        )
        self.add_item(self.channel_ids)

        self.user_ids = TextInput(
            label="User IDs (comma separated)",
            min_length=1,
            max_length=4000,
            required=False,
            placeholder="Enter user IDs separated by commas!",
        )
        self.add_item(self.user_ids)

    async def callback(self, interaction: nextcord.Interaction):
        channel_ids = self.channel_ids.value.split(",")
        user_ids = self.user_ids.value.split(",")
        embed = interaction.message.embeds[0]

        success_channels = []
        error_channels = []
        success_users = []
        error_users = []

        for channel_id in channel_ids:
            channel_id = channel_id.strip()
            if not channel_id:
                continue
            try:
                channel = interaction.guild.get_channel(int(channel_id))
                if channel:
                    await channel.send(embed=embed)
                    success_channels.append(channel)
                else:
                    error_channels.append(channel_id)
            except (ValueError, nextcord.HTTPException):
                error_channels.append(channel_id)

        for user_id in user_ids:
            user_id = user_id.strip()
            if not user_id:
                continue
            try:
                user = interaction.guild.get_member(int(user_id))
                if user:
                    await user.send(embed=embed)
                    success_users.append(user)
                else:
                    error_users.append(user_id)
            except (ValueError, nextcord.Forbidden, nextcord.HTTPException):
                error_users.append(user_id)

        result_embed = nextcord.Embed(color=nextcord.Color.blue(), timestamp=utils.utcnow())
        result_embed.set_footer(text=FOOTER_TEXT)

        if success_channels:
            result_embed.title = "SUCCESS! Embed sent to the following channels:"
            result_embed.description = "\n".join(ch.mention for ch in success_channels)
        elif error_channels:
            result_embed.title = "ERROR! Could not find channels with the given IDs:"
            result_embed.description = "\n".join(error_channels)

        if success_users:
            result_embed.add_field(
                name="SUCCESS! Embed sent to the following users:",
                value="\n".join(u.mention for u in success_users),
                inline=False,
            )
        if error_users:
            result_embed.add_field(
                name="ERROR! Could not find users with the given IDs:",
                value="\n".join(error_users),
                inline=False,
            )

        await interaction.response.send_message(embed=result_embed, ephemeral=True)


class EmbedModalContent(Modal):
    def __init__(self):
        super().__init__("Edit content!", timeout=None)
        self.em_content = TextInput(
            label="Embed content",
            min_length=1,
            max_length=4000,
            required=False,
            placeholder="Enter embed content!",
        )
        self.add_item(self.em_content)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.message.edit(content=self.em_content.value)
        embed = nextcord.Embed(
            title="SUCCESS! Content updated!",
            description="😁",
            color=nextcord.Color.blue(),
            timestamp=utils.utcnow(),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class EmbedModalThumbnail(Modal):
    def __init__(self):
        super().__init__("Edit thumbnail!", timeout=None)
        self.em_thumbnail = TextInput(
            label="Thumbnail URL",
            min_length=1,
            max_length=124,
            required=False,
            placeholder="Enter the thumbnail URL!",
        )
        self.add_item(self.em_thumbnail)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        if self.em_thumbnail.value:
            embed.set_thumbnail(url=self.em_thumbnail.value)
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(
            title="SUCCESS! Thumbnail updated!",
            description="😁",
            color=nextcord.Color.blue(),
            timestamp=utils.utcnow(),
        )
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalTitle(Modal):
    def __init__(self):
        super().__init__("Edit title!", timeout=None)
        self.em_title = TextInput(
            label="Embed title",
            min_length=1,
            max_length=124,
            required=False,
            placeholder="Enter the embed title!",
        )
        self.add_item(self.em_title)
        self.em_desc = TextInput(
            label="Embed description",
            min_length=1,
            max_length=4000,
            required=False,
            placeholder="Enter the embed description!",
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.em_desc)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed.title = self.em_title.value
        embed.description = self.em_desc.value
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(
            title="SUCCESS! Title updated!",
            description="😁",
            color=nextcord.Color.blue(),
            timestamp=utils.utcnow(),
        )
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalColor(Modal):
    def __init__(self):
        super().__init__("Edit embed color!", timeout=None)
        self.em_color = TextInput(
            label="Embed color (hex or color name)",
            min_length=1,
            max_length=124,
            required=False,
            placeholder="Enter a color (e.g. 0xFF0000 or red)!",
        )
        self.add_item(self.em_color)

    async def callback(self, interaction: nextcord.Interaction):
        color = self.em_color.value
        embed = interaction.message.embeds[0]

        color_mapping = {
            "black": 0x000000, "white": 0xFFFFFF, "red": 0xFF0000,
            "green": 0x00FF00, "blue": 0x0000FF, "light blue": 0x0088FF,
            "yellow": 0xFFFF00, "orange": 0xFFA500, "purple": 0x800080,
            "pink": 0xFFC0CB, "gray": 0x808080, "brown": 0xA52A2A,
            "silver": 0xC0C0C0, "gold": 0xFFD700, "teal": 0x40E0D0,
            "navy": 0x000080, "coral": 0xFF7F50, "indigo": 0x4B0082,
        }

        try:
            if color.lower() in color_mapping:
                color_value = nextcord.Color(color_mapping[color.lower()])
            elif color.startswith("0x"):
                hex_val = int(color, 16)
                color_value = nextcord.Colour.from_rgb(
                    (hex_val >> 16) & 0xFF,
                    (hex_val >> 8) & 0xFF,
                    hex_val & 0xFF,
                )
            else:
                await interaction.response.send_message("Invalid color format.", ephemeral=True)
                return
        except (ValueError, TypeError):
            await interaction.response.send_message("Invalid color format.", ephemeral=True)
            return

        embed.color = color_value
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(
            title="SUCCESS! Color updated!",
            description="😁",
            color=nextcord.Color.blue(),
            timestamp=utils.utcnow(),
        )
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalAuthor(Modal):
    def __init__(self):
        super().__init__("Edit author!", timeout=None)
        self.em_author_name = TextInput(label="Author name", min_length=1, max_length=124, required=False, placeholder="Author name")
        self.em_author_url = TextInput(label="Author URL", min_length=1, max_length=124, required=False, placeholder="Author URL")
        self.em_author_icon = TextInput(label="Author icon URL", min_length=1, max_length=124, required=False, placeholder="Author icon URL")
        self.add_item(self.em_author_name)
        self.add_item(self.em_author_url)
        self.add_item(self.em_author_icon)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed.set_author(
            name=self.em_author_name.value,
            icon_url=self.em_author_icon.value,
            url=self.em_author_url.value,
        )
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(title="SUCCESS! Author updated!", description="😁", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalImage(Modal):
    def __init__(self):
        super().__init__("Edit image!", timeout=None)
        self.em_image = TextInput(label="Image URL", min_length=1, max_length=124, required=False, placeholder="Enter image URL!")
        self.add_item(self.em_image)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed.set_image(url=self.em_image.value)
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(title="SUCCESS! Image updated!", description="😁", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalFooter(Modal):
    def __init__(self):
        super().__init__("Edit footer!", timeout=None)
        self.em_footer_text = TextInput(label="Footer text", min_length=1, max_length=124, required=False, placeholder="Footer text")
        self.add_item(self.em_footer_text)
        self.em_footer_icon = TextInput(label="Footer icon URL", min_length=1, max_length=124, required=False, placeholder="Footer icon URL")
        self.add_item(self.em_footer_icon)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        embed.set_footer(text=self.em_footer_text.value, icon_url=self.em_footer_icon.value)
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(title="SUCCESS! Footer updated!", description="😁", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalFieldAdd(Modal):
    def __init__(self):
        super().__init__("Add field!", timeout=None)
        self.em_field_name = TextInput(label="Field name", min_length=1, max_length=256, required=True, placeholder="Field name")
        self.em_field_value = TextInput(label="Field value", min_length=1, max_length=1024, required=False, placeholder="Field value", style=nextcord.TextInputStyle.paragraph)
        self.em_field_inline = TextInput(label="Inline? (True/False)", min_length=1, max_length=5, required=True, placeholder="True or False")
        self.add_item(self.em_field_name)
        self.add_item(self.em_field_value)
        self.add_item(self.em_field_inline)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        inline = self.em_field_inline.value.lower() == "true"
        embed.add_field(name=self.em_field_name.value, value=self.em_field_value.value, inline=inline)
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(title="SUCCESS! Field added!", description="😁", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalFieldEdit(Modal):
    def __init__(self):
        super().__init__("Edit field!", timeout=None)
        self.em_current_name = TextInput(label="Current field name", min_length=1, max_length=256, required=True, placeholder="Name of the field to edit")
        self.em_new_name = TextInput(label="New field name", min_length=1, max_length=256, required=False, placeholder="New name (leave empty to keep)")
        self.em_field_value = TextInput(label="Field value", min_length=1, max_length=1024, required=False, placeholder="New value", style=nextcord.TextInputStyle.paragraph)
        self.em_field_inline = TextInput(label="Inline? (True/False)", min_length=1, max_length=5, required=True, placeholder="True or False")
        self.add_item(self.em_current_name)
        self.add_item(self.em_new_name)
        self.add_item(self.em_field_value)
        self.add_item(self.em_field_inline)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        inline = self.em_field_inline.value.lower() == "true"
        for i, field in enumerate(embed.fields):
            if field.name == self.em_current_name.value:
                name = self.em_new_name.value if self.em_new_name.value else field.name
                embed.set_field_at(i, name=name, value=self.em_field_value.value, inline=inline)
                break
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(title="SUCCESS! Field updated!", description="😁", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class EmbedModalFieldRemove(Modal):
    def __init__(self):
        super().__init__("Remove field!", timeout=None)
        self.em_field_name = TextInput(label="Field name", min_length=1, max_length=256, required=True, placeholder="Name of the field to remove")
        self.add_item(self.em_field_name)

    async def callback(self, interaction: nextcord.Interaction):
        embed = interaction.message.embeds[0]
        for i, field in enumerate(embed.fields):
            if field.name == self.em_field_name.value:
                embed.remove_field(i)
                break
        await interaction.message.edit(embed=embed)

        result = nextcord.Embed(title="SUCCESS! Field removed!", description="😁", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        result.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=result, ephemeral=True)


class ConfirmCancelView(nextcord.ui.View):
    def __init__(self, original_embed, message):
        super().__init__(timeout=None)
        self.original_embed = original_embed
        self.message = message

    @nextcord.ui.button(label="✅ Yes", style=nextcord.ButtonStyle.red, custom_id="embed_confirm")
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.message.delete()
        embed = nextcord.Embed(title="Embed editor closed!", color=nextcord.Color.dark_green(), timestamp=utils.utcnow())
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.edit_message(embed=embed, view=None)

    @nextcord.ui.button(label="❌ No", style=nextcord.ButtonStyle.secondary, custom_id="embed_cancel")
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Cancelled!", color=nextcord.Color.blue(), timestamp=utils.utcnow())
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.edit_message(embed=embed, view=None)


class EmbedEditorSelect(View):
    def __init__(self, message, expected_user_id):
        super().__init__(timeout=None)
        self.message = message
        self.expected_user_id = expected_user_id
        self.initial_placeholder = "🖌️ Edit Embed!"

        self.select = Select(
            placeholder=self.initial_placeholder,
            custom_id="embed_editor_select",
            options=[
                nextcord.SelectOption(label="Edit title", value="01", emoji="🖌️"),
                nextcord.SelectOption(label="Edit color", value="02", emoji="🖌️"),
                nextcord.SelectOption(label="Edit author", value="03", emoji="🖌️"),
                nextcord.SelectOption(label="Edit thumbnail", value="04", emoji="🖌️"),
                nextcord.SelectOption(label="Edit image", value="05", emoji="🖌️"),
                nextcord.SelectOption(label="Edit footer", value="06", emoji="🖌️"),
                nextcord.SelectOption(label="Add field", value="07", emoji="🖌️"),
                nextcord.SelectOption(label="Edit field", value="08", emoji="🖌️"),
                nextcord.SelectOption(label="Remove field", value="09", emoji="🖌️"),
                nextcord.SelectOption(label="Edit content", value="10", emoji="🖌️"),
            ],
        )
        self.select.callback = self._on_select
        self.add_item(self.select)

        self.send_button = nextcord.ui.Button(label="📡 Send", style=nextcord.ButtonStyle.blurple)
        self.send_button.callback = self._on_send
        self.add_item(self.send_button)

        self.close_button = nextcord.ui.Button(label="🗡️ Close Editor", style=nextcord.ButtonStyle.danger)
        self.close_button.callback = self._on_close
        self.add_item(self.close_button)

    async def _check_user(self, interaction: nextcord.Interaction) -> bool:
        if interaction.user.id != self.expected_user_id:
            embed = nextcord.Embed(title="Error! You cannot edit someone else's embed!", color=nextcord.Color.red(), timestamp=utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    async def _on_select(self, interaction: nextcord.Interaction):
        if not await self._check_user(interaction):
            return

        modal_map = {
            "01": EmbedModalTitle, "02": EmbedModalColor, "03": EmbedModalAuthor,
            "04": EmbedModalThumbnail, "05": EmbedModalImage, "06": EmbedModalFooter,
            "07": EmbedModalFieldAdd, "08": EmbedModalFieldEdit, "09": EmbedModalFieldRemove,
            "10": EmbedModalContent,
        }

        value = interaction.data["values"][0]
        modal_cls = modal_map.get(value)
        if modal_cls:
            self.select.placeholder = self.initial_placeholder
            await interaction.message.edit(view=self)
            await interaction.response.send_modal(modal_cls())

    async def _on_send(self, interaction: nextcord.Interaction):
        if not await self._check_user(interaction):
            return
        await interaction.response.send_modal(EmbedModalChannel())

    async def _on_close(self, interaction: nextcord.Interaction):
        if not await self._check_user(interaction):
            return
        embed = nextcord.Embed(title="Are you sure you want to close the editor?", color=nextcord.Color.red(), timestamp=utils.utcnow())
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed, view=ConfirmCancelView(embed, self.message), ephemeral=True)


class EmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="embed", description="Creates an interactive embed editor!")
    @application_checks.has_permissions(administrator=True)
    async def embed(self, interaction: nextcord.Interaction):
        loading_embed = nextcord.Embed(title="Loading...", color=nextcord.Color.green(), timestamp=utils.utcnow())
        loading_embed.set_footer(text=FOOTER_TEXT)
        message = await interaction.response.send_message(embed=loading_embed)
        view = EmbedEditorSelect(message, interaction.user.id)

        editor_embed = nextcord.Embed(
            title="Welcome to the Embed Creator!",
            description="`Use the menu below to edit and send embeds to channels or users (you'll need their IDs).`",
            color=nextcord.Color.og_blurple(),
        )
        editor_embed.set_footer(text=FOOTER_TEXT)
        await interaction.edit_original_message(embed=editor_embed, view=view)


def setup(bot):
    bot.add_cog(EmbedCog(bot))
import asyncio
import io
import re
from typing import List

import discord

from oobabot.fancy_logging import get_logger
from oobabot.sd_client import StableDiffusionClient
from oobabot.templates import TemplateStore
from oobabot.types import TemplateToken
from oobabot.types import Templates


async def image_task_to_file(image_task: asyncio.Task[bytes], image_request: str):
    await image_task
    img_bytes = image_task.result()
    file_of_bytes = io.BytesIO(img_bytes)
    file = discord.File(file_of_bytes)
    file.filename = "photo.png"
    file.description = f"image generated from '{image_request}'"
    return file


class StableDiffusionImageView(discord.ui.View):
    """
    A View that displays buttons to regenerate an image
    from Stable Diffusion with a new seed, or to lock
    in the current image.
    """

    def __init__(
        self,
        sd_client: StableDiffusionClient,
        is_channel_nsfw: bool,
        image_prompt: str,
        requesting_user_id: int,
        requesting_user_name: str,
        template_store: TemplateStore,
    ):
        super().__init__(timeout=120.0)

        self.template_store = template_store

        # only the user who requested generation of the image
        # can have it replaced
        self.requesting_user_id = requesting_user_id
        self.requesting_user_name = requesting_user_name
        self.image_prompt = image_prompt
        self.photo_accepted = False

        #####################################################
        # "Try Again" button
        #
        btn_try_again = discord.ui.Button(
            label="Try Again",
            style=discord.ButtonStyle.blurple,
            row=1,
        )
        self.image_message = None

        async def on_try_again(interaction: discord.Interaction):
            result = await self.diy_interaction_check(interaction)
            if not result:
                # unauthorized user
                return

            try:
                # generate a new image
                regen_task = sd_client.generate_image(image_prompt, is_channel_nsfw)
                regen_file = await image_task_to_file(regen_task, image_prompt)
                await interaction.response.defer()
                await self.get_image_message().edit(attachments=[regen_file])
            except Exception as e:
                get_logger().error("Could not regenerate image: " + str(e))

        btn_try_again.callback = on_try_again

        #####################################################
        # "Accept" button
        #
        btn_lock_in = discord.ui.Button(
            label="Accept",
            style=discord.ButtonStyle.success,
            row=1,
        )

        async def on_lock_in(interaction: discord.Interaction):
            result = await self.diy_interaction_check(interaction)
            if not result:
                # unauthorized user
                return
            await interaction.response.defer()
            await self.detach_view_keep_img()

        btn_lock_in.callback = on_lock_in

        #####################################################
        # "Delete" button
        #
        btn_delete = discord.ui.Button(
            label="Delete",
            style=discord.ButtonStyle.danger,
            row=1,
        )

        async def on_delete(interaction: discord.Interaction):
            result = await self.diy_interaction_check(interaction)
            if not result:
                # unauthorized user
                return
            await interaction.response.defer()
            await self.delete_image()

        btn_delete.callback = on_delete

        super().add_item(btn_try_again).add_item(btn_lock_in).add_item(btn_delete)

    def set_image_message(self, image_message: discord.Message):
        self.image_message = image_message

    def get_image_message(self) -> discord.Message:
        if self.image_message is None:
            raise ValueError("image_message is None")
        return self.image_message

    async def delete_image(self):
        await self.detach_view_delete_img(self.get_detach_message())

    async def detach_view_delete_img(self, detach_msg: str):
        await self.get_image_message().edit(
            content=detach_msg,
            view=None,
            attachments=[],
        )

    async def detach_view_keep_img(self):
        self.photo_accepted = True
        await self.get_image_message().edit(
            content=None,
            view=None,
        )

    async def on_timeout(self):
        if not self.photo_accepted:
            await self.delete_image()

    async def diy_interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Only allow the requesting user to interact with this view.
        """
        if interaction.user.id == self.requesting_user_id:
            return True
        error_mesage = self._get_message(Templates.IMAGE_UNAUTHORIZED)
        await interaction.response.send_message(
            content=error_mesage,
            ephemeral=True,
        )
        return False

    def get_image_message_text(self) -> str:
        return self._get_message(Templates.IMAGE_CONFIRMATION)

    def get_detach_message(self) -> str:
        return self._get_message(Templates.IMAGE_DETACH)

    def _get_message(self, message_type: Templates) -> str:
        return self.template_store.format(
            message_type,
            {
                TemplateToken.USER_NAME: self.requesting_user_name,
                TemplateToken.IMAGE_PROMPT: self.image_prompt,
            },
        )


class ImageGenerator:
    def __init__(
        self,
        stable_diffusion_client: StableDiffusionClient,
        image_words: List[str],
        template_store: TemplateStore,
    ):
        self.stable_diffusion_client = stable_diffusion_client
        self.template_store = template_store
        self.image_patterns = [
            re.compile(
                r"^.*\b" + image_word + r"\b[\s]*(of|with)?[\s]*[:]?(.*)$",
                re.IGNORECASE,
            )
            for image_word in image_words
        ]

    async def _generate_image(
        self, image_prompt: str, raw_message: discord.Message
    ) -> discord.Message:
        is_channel_nsfw = False
        if isinstance(raw_message.channel, discord.TextChannel):
            is_channel_nsfw = raw_message.channel.is_nsfw()

        image_task = self.stable_diffusion_client.generate_image(
            image_prompt, is_channel_nsfw=is_channel_nsfw
        )
        file = await image_task_to_file(image_task, image_prompt)

        regen_view = StableDiffusionImageView(
            self.stable_diffusion_client,
            is_channel_nsfw=is_channel_nsfw,
            image_prompt=image_prompt,
            requesting_user_id=raw_message.author.id,
            requesting_user_name=raw_message.author.display_name,
            template_store=self.template_store,
        )

        image_message = await raw_message.channel.send(
            content=regen_view.get_image_message_text(),
            reference=raw_message,
            file=file,
            view=regen_view,
        )
        regen_view.image_message = image_message
        return image_message

    async def maybe_generate_image_from_message(
        self, raw_message: discord.Message
    ) -> asyncio.Task[discord.Message] | None:
        """
        If the message contains a photo word, kick off a task
        to generate an image, post it to the channel, and return
        the generated message.

        If the message does not contain a photo word, return None.
        """
        image_prompt = None
        for image_pattern in self.image_patterns:
            match = image_pattern.search(raw_message.content)
            if match:
                image_prompt = match.group(2)
                break
        if image_prompt is None:
            return None

        get_logger().debug("Found image prompt: %s", image_prompt)
        create_image_task = asyncio.create_task(
            self._generate_image(image_prompt, raw_message)
        )
        return create_image_task

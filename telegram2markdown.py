#! /usr/bin/env python3

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    MessageEntityBold, MessageEntityItalic, MessageEntityTextUrl,
    MessageEntityMention, MessageEntityCode, MessageEntityPre
)
import os
from datetime import datetime
import unicodedata

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
channel_username = os.getenv('TELEGRAM_CHANNEL_USERNAME')

# Connect to the client
client = TelegramClient('session_name', api_id, api_hash)


def format_message_text(message_text, entities):
    """Formats a text with entities to Markdown."""
    if not message_text:
        return "[No text content]"

    # Normalize the text to NFC form
    text = unicodedata.normalize('NFC', message_text)

    markdown = ""
    offset = 0

    for entity in entities:
        # Correctly handle multi-byte characters (emoji and complex symbols)
        part_without_formatting = text[offset:entity.offset]
        part_formatted = text[entity.offset:entity.offset + entity.length]

        # Handle different types of entities
        if isinstance(entity, MessageEntityBold):
            markdown += part_without_formatting + f"**{part_formatted}**"
        elif isinstance(entity, MessageEntityItalic):
            markdown += part_without_formatting + f"*{part_formatted}*"
        elif isinstance(entity, MessageEntityTextUrl):
            markdown += part_without_formatting + f"[{part_formatted}]({entity.url})"
        elif isinstance(entity, MessageEntityMention):
            markdown += part_without_formatting + f"[{part_formatted}](https://t.me/{text[entity.offset:entity.offset + entity.length]})"
        elif isinstance(entity, MessageEntityCode):
            markdown += part_without_formatting + f"`{part_formatted}`"
        elif isinstance(entity, MessageEntityPre):
            markdown += part_without_formatting + f"```{part_formatted}```"
        else:
            markdown += part_without_formatting + part_formatted

        # Update the offset for the next entity
        offset = entity.offset + entity.length

    # Add the remaining text after the last entity
    markdown += text[offset:]
    return markdown


async def main():
    # Start the client
    await client.start()
    channel = await client.get_entity(channel_username)

    # Get message history
    history = await client(GetHistoryRequest(
        peer=channel,
        offset_date=None,
        offset_id=0,
        add_offset=0,
        limit=1,
        max_id=0,
        min_id=0,
        hash=0
    ))

    # Create a folder to store data
    if not os.path.exists('channel_export'):
        os.makedirs('channel_export')

    # Save each message in a separate Markdown file
    for message in history.messages:
        if message.message or message.media:
            # Save message text and links
            with open(f'channel_export/message_{message.id}.md', 'w', encoding='utf-8') as file:
                # Format the main message text
                formatted_text = format_message_text(message.message, message.entities)

                # Format media captions, if present
                if message.media and hasattr(message.media, 'caption') and message.media.caption:
                    caption_text = format_message_text(message.media.caption, message.media.entities)
                    formatted_text += f"\n\n*Media Caption:* {caption_text}"

                # Handle media-specific attributes (like alt text)
                if message.media and hasattr(message.media, 'document') and message.media.document.attributes:
                    for attribute in message.media.document.attributes:
                        if hasattr(attribute, 'alt') and attribute.alt:
                            formatted_text += f"\n\n*Alt Text:* {attribute.alt}"

                if not formatted_text.strip():
                    formatted_text = "[No text content]"

                # Write the formatted text
                file.write(formatted_text + '\n')

                # Add buttons and links
                if message.reply_markup and message.reply_markup.rows:
                    for row in message.reply_markup.rows:
                        for button in row.buttons:
                            file.write(f"[{button.text}]({button.url})\n")

                # Add original post link and date
                file.write("\n---\n")
                post_link = f"https://t.me/{channel_username}/{message.id}"
                post_date = message.date.strftime('%Y-%m-%d')
                file.write(f"[Original Post]({post_link})\n")
                file.write(f"Date: {post_date}\n")


with client:
    client.loop.run_until_complete(main())
#! /usr/bin/env python3
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel
import os

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
channel_username = os.getenv('TELEGRAM_CHANNEL_USERNAME')

# Connect to Telegram API
with TelegramClient('session_name', api_id, api_hash) as client:
    # get information about the channel
    channel = client.get_entity(channel_username)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0

    with open('index.md', 'w', encoding='utf-8') as file:
        file.write(f"# Index of Telegram Channel: {channel_username}\n\n")

        while True:
            messages = client.iter_messages(channel, limit=limit, offset_id=offset_id)
            messages = list(messages)
            if not messages:
                break

            for message in messages:
                if message.message or message.media:
                    text = message.message

                    # if it is a media message, get the text from the media description
                    if message.media:
                        if hasattr(message.media, 'document') and message.media.document.attributes:
                            for attribute in message.media.document.attributes:
                                if hasattr(attribute, 'alt'):
                                    text = attribute.alt
                        elif hasattr(message.media, 'video') and message.media.video.attributes:
                            for attribute in message.media.video.attributes:
                                if hasattr(attribute, 'alt'):
                                    text = attribute.alt
                        elif hasattr(message.media, 'file') and message.media.caption:
                            text = message.media.caption

                    # Write to markdown file if text is not empty
                    if text:
                        file.write(f"- [{text.split('\n')[0][:200]}]({message.id}.md)\n")

            total_messages += len(messages)
            offset_id = messages[-1].id
            print(f"Processed messages {total_messages - len(messages) + 1} to {total_messages}")

    print(f"Data are stored to 'index.md'")

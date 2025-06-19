from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import re
import os
import json
import asyncio

# 1. Telegram API credentials
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone_number = 'YOUR_PHONE_NUMBER'  # Only needed for first-time login

client = TelegramClient('ethio_session', api_id, api_hash)

# 2. Normalize Amharic text
def normalize_amharic(text):
    text = re.sub(r"[፡።፤፥፦፧፨]", " ", text)
    text = re.sub(r"[^\u1200-\u137F\s]", "", text)
    return text.strip()

# 3. Download media
async def download_media(msg, download_dir='downloads'):
    os.makedirs(download_dir, exist_ok=True)
    if msg.media:
        return await msg.download_media(file=download_dir)
    return None

# 4. Fetch messages and preprocess
async def fetch_and_process(channel_username, limit=50):
    await client.start(phone=phone_number)
    entity = await client.get_entity(channel_username)
    messages = await client(GetHistoryRequest(peer=entity, limit=limit, offset_date=None,
                                              offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
    processed = []

    for msg in messages.messages:
        if msg.message:
            cleaned_text = normalize_amharic(msg.message)
            media_path = await download_media(msg)
            entry = {
                "channel": channel_username,
                "message_id": msg.id,
                "sender": str(msg.sender_id),
                "timestamp": str(msg.date),
                "original_text": msg.message,
                "text_clean": cleaned_text,
                "media_type": msg.media.__class__.__name__ if msg.media else None,
                "media_path": media_path
            }
            processed.append(entry)

    # Save results
    with open(f'{channel_username}_data.json', 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

# 5. Main
if __name__ == "__main__":
    channel_usernames = ['@AddisMarket', '@EthioShopOnline']  # Add more channels
    with client:
        for channel in channel_usernames:
            asyncio.run(fetch_and_process(channel))

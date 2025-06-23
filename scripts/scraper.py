import os
import re
import asyncio
import pandas as pd
from dotenv import load_dotenv
from telethon.sync import TelegramClient

# Load credentials from .env

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Clean Amharic text

def clean_amharic_text(text):
    if not text:
        return ''
    # Keep Amharic characters, some punctuation, English letters, and numbers
    text = re.sub(r'[^\u1200-\u137F\s0-9a-zA-Z፡።፣]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# Fetch messages from one channel

async def fetch_channel_messages(api_id, api_hash, channel_username, limit=100):
    async with TelegramClient('session', api_id, api_hash) as client:
        messages = []
        async for msg in client.iter_messages(channel_username, limit=limit):
            messages.append({
                'channel': channel_username,
                'date': msg.date,
                'sender_id': msg.sender_id,
                'message': msg.message,
                'views': msg.views,
                'has_image': msg.media is not None
            })
        return pd.DataFrame(messages)


# Run scraper for multiple channels

def run_scraper(api_id, api_hash, channel_list, limit=100, save_path="../data/structured_telegram_data.csv"):
    all_data = []
    status_report = []

    for channel in channel_list:
        print(f"Scraping channel: {channel}")
        try:
            df = asyncio.run(fetch_channel_messages(api_id, api_hash, channel, limit))
            df['clean_text'] = df['message'].apply(clean_amharic_text)
            all_data.append(df)
            print(f"{channel}: {len(df)} messages fetched.")
            status_report.append((channel, "Success", len(df)))
        except Exception as e:
            print(f"{channel}: Failed. Error: {str(e)}")
            status_report.append((channel, "Failed", 0))

    if not all_data:
        raise ValueError("No valid data collected from any channels.")

    final_df = pd.concat(all_data, ignore_index=True)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    final_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"\nSaved {len(final_df)} messages from {len(all_data)} channels to {save_path}")
    
    return final_df, status_report
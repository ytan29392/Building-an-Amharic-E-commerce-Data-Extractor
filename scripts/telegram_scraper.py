from telethon.sync import TelegramClient
import pandas as pd
import asyncio
import re
import os

# --- Configurations ---
# api_id = YOUR_API_ID
# api_hash = 'YOUR_API_HASH'
# channel_username = 'shageronlinestore'  # Change as needed
limit = 200

# --- Clean Amharic text ---
def clean_amharic_text(text):
    if not text:
        return ''
    text = re.sub(r'[^\u1200-\u137F\s0-9a-zA-Z፡።፣]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- Fetch Telegram Messages ---
async def fetch_messages():
    # async with TelegramClient('session', api_id, api_hash) as client:
        messages = []
        # async for msg in client.iter_messages(channel_username, limit=limit):
            messages.append({
                # 'channel': channel_username,
                'date': msg.date,
                'sender_id': msg.sender_id,
                'message': msg.message,
                'views': msg.views,
                'has_image': msg.media is not None
            })
        return pd.DataFrame(messages)

# --- Main Function ---
def main():
    df = asyncio.run(fetch_messages())
    df['clean_text'] = df['message'].apply(clean_amharic_text)
    os.makedirs('../data', exist_ok=True)
    df.to_csv('../data/structured_telegram_data.csv', index=False)
    print(f"Saved {len(df)} messages to structured_telegram_data.csv")

if __name__ == "__main__":
    main()

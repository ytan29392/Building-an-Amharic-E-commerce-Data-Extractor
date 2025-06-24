import pandas as pd
from datetime import datetime
from collections import defaultdict
import numpy as np

# Load your telegram_data.csv scraped from Telegram
telegram_df = pd.read_csv("../data/telegram_data.csv")

# Columns expected: ['vendor', 'message', 'views', 'timestamp']

# Convert timestamp if it's a string
telegram_df['timestamp'] = pd.to_datetime(telegram_df['timestamp'])

# Load your fine-tuned NER model pipeline
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
model_name = "Davlan/afro-xlmr-base"  # or your fine-tuned model path
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
ner_pipeline = pipeline("token-classification", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Define Metric Calculators
def get_posting_frequency(df):
    weeks = (df['timestamp'].max() - df['timestamp'].min()).days / 7.0
    return round(len(df) / weeks, 2) if weeks > 0 else len(df)

def get_avg_views(df):
    return round(df['views'].mean(), 2)

def get_top_post_info(df):
    top_post = df.loc[df['views'].idxmax()]
    message = top_post['message']
    price = extract_avg_price_from_ner(message)
    return message, price, top_post['views']

def extract_avg_price_from_ner(message):
    predictions = ner_pipeline(message)
    price_tokens = [pred['word'] for pred in predictions if 'PRICE' in pred['entity']]
    prices = []
    for token in price_tokens:
        try:
            prices.append(float(token.replace('ETB', '').replace('ብር', '').strip()))
        except:
            continue
    return round(np.mean(prices), 2) if prices else 0.0

def get_avg_price(df):
    prices = []
    for msg in df['message']:
        price = extract_avg_price_from_ner(msg)
        if price > 0:
            prices.append(price)
    return round(np.mean(prices), 2) if prices else 0.0

def compute_lending_score(avg_views, posts_per_week):
    return round((avg_views * 0.5) + (posts_per_week * 0.5), 2)

# Run the Vendor Analytics Engine
vendors = telegram_df['vendor'].unique()

vendor_scorecards = []
for vendor in vendors:
    vendor_data = telegram_df[telegram_df['vendor'] == vendor]
    posts_per_week = get_posting_frequency(vendor_data)
    avg_views = get_avg_views(vendor_data)
    avg_price = get_avg_price(vendor_data)
    top_post, top_price, top_views = get_top_post_info(vendor_data)
    lending_score = compute_lending_score(avg_views, posts_per_week)

    vendor_scorecards.append({
        "Vendor": vendor,
        "Posts/Week": posts_per_week,
        "Avg. Views/Post": avg_views,
        "Avg. Price (ETB)": avg_price,
        "Top Post Snippet": top_post[:50] + "...",
        "Top Post Price": top_price,
        "Top Post Views": top_views,
        "Lending Score": lending_score
    })

# Display Final Vendor Scorecard
df_scorecard = pd.DataFrame(vendor_scorecards)
df_scorecard = df_scorecard.sort_values("Lending Score", ascending=False)
df_scorecard.to_csv("vendor_scorecard.csv", index=False)
df_scorecard

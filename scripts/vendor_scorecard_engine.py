
import pandas as pd
from collections import defaultdict
from datetime import datetime
from transformers import pipeline
from collections import defaultdict
from tqdm import tqdm


def extract_prices(ner_pipeline, text):
    entities = ner_pipeline(text)
    prices = []
    current_price = []

    for ent in entities:
        # Use 'entity_group' if present (aggregated mode), else fallback to 'entity'
        label = ent.get("entity", "") or ent.get("entity_group", "")

        if "PRICE" in label:
            current_price.append(ent["word"])
        elif current_price:
            try:
                # Join tokens, remove common currency symbols/words, convert to float
                joined = "".join(current_price).replace("ብር", "").replace(",", "").strip()
                prices.append(float(joined))
            except:
                pass
            current_price = []

    # Final flush if text ends with a PRICE
    if current_price:
        try:
            joined = "".join(current_price).replace("ብር", "").replace(",", "").strip()
            prices.append(float(joined))
        except:
            pass

    return prices


def extract_prices_from_texts(ner_pipeline, texts, batch_size=32):
    """
    Batched NER processing of texts for price extraction.
    """
    all_prices = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Extracting prices"):
        batch = texts[i:i + batch_size]
        ner_results = ner_pipeline(batch)
        for entities in ner_results:
            prices = []
            current_price = []
            for ent in entities:
                if "PRICE" in ent["entity_group"]:
                    current_price.append(ent["word"])
                elif current_price:
                    try:
                        joined = "".join(current_price).replace("ብር", "").replace(",", "")
                        prices.append(float(joined))
                    except:
                        pass
                    current_price = []
            all_prices.append(prices)
    return all_prices


def score_vendors(df, ner_pipeline):
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['week'] = df['timestamp'].dt.to_period('W').astype(str)

    # Precompute all prices in batch
    df = df.dropna(subset=['text'])
    df = df.reset_index(drop=True)  # Ensure index matches for batched assignment
    df['extracted_prices'] = extract_prices_from_texts(ner_pipeline, df['text'].tolist())

    vendor_stats = defaultdict(dict)

    for vendor, group in df.groupby('vendor'):
        total_posts = len(group)
        weeks = group['week'].nunique()
        posts_per_week = total_posts / weeks if weeks else 0

        avg_views = group['views'].mean()
        top_post = group.loc[group['views'].idxmax()]
        top_text = top_post['text']
        top_views = top_post['views']

        # Flatten list of prices
        all_prices = [price for prices in group['extracted_prices'] for price in prices]
        avg_price = sum(all_prices) / len(all_prices) if all_prices else 0

        lending_score = (avg_views * 0.5) + (posts_per_week * 0.5)

        vendor_stats[vendor] = {
            'Avg. Views/Post': round(avg_views, 1),
            'Posts/Week': round(posts_per_week, 1),
            'Avg. Price (ETB)': round(avg_price, 2),
            'Top Post': top_text,
            'Top Views': top_views,
            'Lending Score': round(lending_score, 2)
        }

    return pd.DataFrame.from_dict(vendor_stats, orient='index').reset_index(names='Vendor')
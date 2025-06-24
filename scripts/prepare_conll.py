import pandas as pd
from preprocessing import remove_emojis, remove_english_words
from labeling import label_message_utf8_with_birr

# Load telegram messages
df = pd.read_csv('telegram_data.csv')
df.dropna(subset=['Message'], inplace=True)

#  Clean the messages
df['Cleaned'] = df['Message'].apply(remove_emojis).apply(remove_english_words)

#  Apply your NER labeling logic
df['Labeled'] = df['Cleaned'].apply(label_message_utf8_with_birr)

# Save as CoNLL format
with open("ner_data.conll", "w", encoding="utf-8") as f:
    for row in df['Labeled']:
        f.write(row + "\n\n")  # double newline to separate sentences

# scripts/evaluate_model.py

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from seqeval.metrics import classification_report, f1_score

def evaluate_model(model_name, dataset_dict):
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)

    # Create token classification pipeline
    ner_pipeline = pipeline(
        task="token-classification",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple"
    )

    true_labels = []
    pred_labels = []

    for item in dataset_dict:
        tokens = item["tokens"]
        ner_tags = item["ner_tags"]

        preds = ner_pipeline(" ".join(tokens))

        # Initialize with "O"
        pred_tag_seq = ["O"] * len(tokens)
        for pred in preds:
            word_index = pred.get("index", 1) - 1  # pipeline token index starts at 1
            if word_index < len(pred_tag_seq):
                pred_tag_seq[word_index] = pred["entity"]

        pred_labels.append(pred_tag_seq)
        true_labels.append(ner_tags)

    print(f"\nModel: {model_name}")
    print(classification_report(true_labels, pred_labels))

    return {
        "model": model_name,
        "f1": f1_score(true_labels, pred_labels)
    }

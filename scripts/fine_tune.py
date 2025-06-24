

def parse_conll(file_path):
    sentences = []
    tokens, labels = [], []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                if tokens:
                    sentences.append({'tokens': tokens, 'ner_tags': labels})
                    tokens, labels = [], []
            else:
                splits = line.strip().split()
                if len(splits) == 2:
                    token, tag = splits
                    tokens.append(token)
                    labels.append(tag)
    return sentences

data = parse_conll("ner_auto_labels.conll")
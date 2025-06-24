

def parse_conll_file(filepath):
    dataset = []
    tokens = []
    tags = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if tokens:
                    dataset.append({"tokens": tokens, "ner_tags": tags})
                    tokens = []
                    tags = []
            else:
                splits = line.split()
                if len(splits) == 2:
                    token, tag = splits
                    tokens.append(token)
                    tags.append(tag)

    return dataset

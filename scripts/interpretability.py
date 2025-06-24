from transformers import pipeline
import shap
from lime.lime_text import LimeTextExplainer

def explain_with_shap(ner_pipeline, input_text):
    explainer = shap.Explainer(ner_pipeline)
    shap_values = explainer([input_text])
    return shap_values

def explain_with_lime(ner_pipeline, input_text):
    def predict_proba(texts):
        results = []
        for t in texts:
            out = ner_pipeline(t)
            labels = [ent["entity"] for ent in out]
            results.append([labels.count(l) for l in ner_pipeline.model.config.id2label.values()])
        return results

    explainer = LimeTextExplainer(class_names=list(ner_pipeline.model.config.id2label.values()))
    exp = explainer.explain_instance(input_text, predict_proba, num_features=10)
    return exp

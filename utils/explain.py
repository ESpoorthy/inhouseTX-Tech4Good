from utils.preprocess import normalise_text

def explain_prediction(text, model, tfidf):
    try:
        import shap
    except ImportError as exc:
        raise RuntimeError("SHAP explanations are available only for the retained legacy model; install the optional legacy dependencies.") from exc
    clean = normalise_text(text)
    vec = tfidf.transform([clean])

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(vec)
  
    return shap_values[0].tolist()

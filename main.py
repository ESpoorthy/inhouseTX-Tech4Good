"""Train the synthetic baseline and print a sample prediction."""
from model.train import train_model
from api.categorization import Categorizer

if __name__ == "__main__":
    _, _, metrics = train_model()
    print("Selected model:", metrics["selected_model"])
    print("Synthetic holdout macro F1:", round(metrics["models"][metrics["selected_model"]]["macro_f1"], 3))
    result = Categorizer().predict("Starbucks Coffee")
    print("Sample prediction:", result["category"], "confidence:", round(result["confidence"], 3))
    print("Explanation:", result["explanation"]["summary"])

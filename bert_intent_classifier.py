from transformers import pipeline


class BERTIntentClassifier:
    _instance = None
    _classifier = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        print(
            "[BERT] Initializing HuggingFace BERT / DistilBART Zero-Shot Transformer Intent Engine..."
        )
        try:
            self._classifier = pipeline(
                "zero-shot-classification", model="valhalla/distilbart-mnli-12-3"
            )
            print("[BERT] BERT / DistilBART Intent Transformer Engine Active!")
        except Exception as e:
            print(f"[BERT] Failed to load BERT Intent Transformer: {e}")
            self._classifier = None

    def classify_intent(self, user_prompt: str):
        """
        Classifies user prompt using BERT/DistilBART Transformer into one of 6 Intent Categories:
        - home_automation
        - vision_camera
        - ml_training
        - pc_brain
        - system_diagnostics
        - general_chat
        """
        if not self._classifier or not user_prompt.strip():
            return None, 0.0

        candidate_labels = [
            "home_automation",
            "vision_camera",
            "ml_training",
            "pc_brain",
            "system_diagnostics",
            "general_chat",
        ]

        try:
            res = self._classifier(user_prompt, candidate_labels=candidate_labels)
            top_label = res["labels"][0]
            top_score = float(res["scores"][0])
            return top_label, top_score
        except Exception as e:
            print(f"[BERTIntentClassifier] Classification error: {e}")
            return None, 0.0


def predict_user_intent_bert(user_prompt: str):
    classifier = BERTIntentClassifier.get_instance()
    label, confidence = classifier.classify_intent(user_prompt)
    return label, confidence


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    test_queries = [
        "turn on my room lights to green",
        "detect my facial expressions and hand signs",
        "train supervised and unsupervised models",
        "show me the neural network brain of this pc",
        "what is my cpu and ram usage right now",
    ]
    for q in test_queries:
        label, conf = predict_user_intent_bert(q)
        print(f"Query: '{q}' -> Intent: {label} (Confidence: {conf*100:.1f}%)")

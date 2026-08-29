from app.nlp.transformer_model import TransformerModel

class BiasClassifier:
    def __init__(self):
        self.model = TransformerModel()

    def classify(self, text: str) -> dict:
        return self.model.predict(text)
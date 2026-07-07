import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences

from preprocessing import clean_text
from modeling import MAX_LEN, MODEL_PATH, TOKENIZER_PATH, probabilities_to_labels

INPUT_PATH = "test.csv"
OUTPUT_PATH = "test_result.csv"


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    with open(TOKENIZER_PATH, encoding="utf-8") as f:
        tokenizer = tokenizer_from_json(f.read())

    cleaned_texts = df["text"].astype(str).map(clean_text)
    sequences = tokenizer.texts_to_sequences(cleaned_texts)
    padded = pad_sequences(sequences, maxlen=MAX_LEN, padding="pre", truncating="pre")

    model = load_model(MODEL_PATH)
    probabilities = model.predict(padded).ravel()
    labels = probabilities_to_labels(probabilities)

    df["sentiment"] = [label for label in labels]
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

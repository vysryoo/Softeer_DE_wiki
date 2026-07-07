import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Embedding, Bidirectional, LSTM, Dropout, Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.text import tokenizer_from_json

VOCAB_SIZE = 10_000
MAX_LEN = 100
EMBEDDING_DIM = 128
LSTM_UNITS = 64
DROPOUT_RATE = 0.5
EPOCHS = 7
BATCH_SIZE = 256

NEUTRAL_LOW = 0.4
NEUTRAL_HIGH = 0.6

DATASET_PATH = "train_val_dataset.npz"
TOKENIZER_PATH = "tokenizer.json"
MODEL_PATH = "sentiment_model.keras"



def load_dataset(path: str = DATASET_PATH):
    data = np.load(path)
    return data["X_train"], data["X_val"], data["y_train"], data["y_val"]


def load_vocab_size(path: str = TOKENIZER_PATH) -> int:
    with open(path, encoding="utf-8") as f:
        tokenizer = tokenizer_from_json(f.read())
    return min(VOCAB_SIZE, len(tokenizer.word_index) + 1)


def build_model(vocab_size: int) -> Sequential:
    model = Sequential([
        Input(shape=(MAX_LEN,)),
        Embedding(input_dim=vocab_size, output_dim=EMBEDDING_DIM),
        Bidirectional(LSTM(LSTM_UNITS, return_sequences=False)),
        Dropout(DROPOUT_RATE),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    return model


def probabilities_to_labels(
    probabilities: np.ndarray,
    low: float = NEUTRAL_LOW,
    high: float = NEUTRAL_HIGH,
) -> np.ndarray:
    return np.select(
        [probabilities < low, probabilities > high],
        [0, 4],
        default=2,
    )




def main() -> None:
    X_train, X_val, y_train, y_val = load_dataset()
    vocab_size = load_vocab_size()

    model = build_model(vocab_size)
    model.summary()

    early_stopping = EarlyStopping(
        monitor="val_loss", patience=3, restore_best_weights=True
    )


    model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[early_stopping],
        verbose=1,
    )

    val_loss, val_accuracy = model.evaluate(X_val, y_val)
    print(f"loss: {val_loss:.4f}, accuracy: {val_accuracy:.4f}")

    val_probabilities = model.predict(X_val).ravel()
    val_return_labels = probabilities_to_labels(val_probabilities)
    labels, counts = np.unique(val_return_labels, return_counts=True)

    for label, count in zip(labels, counts):
        print(f"  {label}: {count:,}개 ({count / len(val_return_labels):.1%})")

    model.save(MODEL_PATH)



if __name__ == "__main__":
    main()
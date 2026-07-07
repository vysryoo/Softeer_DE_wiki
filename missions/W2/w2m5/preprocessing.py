
import re 
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


INPUT_PATH = "training.csv"
SAMPLED_PATH = "sampled_100k.csv"
CLEANED_PATH = "cleaned_100k.csv"
TOKENIZER_PATH = "tokenizer.json"
OUTPUT_PATH = "train_val_dataset.npz"

RANDOM_STATE = 42
SAMPLE_SIZE = 500_000
COLUMNS = ["target", "ids", "date", "flag", "user", "text"]

VOCAB_SIZE = 10_000
MAX_LEN = 100
OOV_TOKEN = "<OOV>"
TEST_SIZE = 0.2


URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
MENTION_PATTERN = re.compile(r"@\w+")
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # 이모티콘/기호 전반
    "\U00002600-\U000027BF"  # 기타 기호/딩뱃
    "\U0001F1E6-\U0001F1FF"  # 국기
    "]+"
)
NON_ALPHA_PATTERN = re.compile(r"[^a-z\s]")
MULTI_SPACE_PATTERN = re.compile(r"\s+")

CONTRACTIONS = {
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "can't": "can not", "won't": "will not", "wouldn't": "would not",
    "couldn't": "could not", "shouldn't": "should not", "mustn't": "must not",
    "isn't": "is not", "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "haven't": "have not", "hasn't": "has not", "hadn't": "had not", "ain't": "am not",
    "i'm": "i am", "you're": "you are", "he's": "he is", "she's": "she is",
    "it's": "it is", "we're": "we are", "they're": "they are",
    "i've": "i have", "you've": "you have", "we've": "we have", "they've": "they have",
    "i'll": "i will", "you'll": "you will", "he'll": "he will", "she'll": "she will",
    "we'll": "we will", "they'll": "they will",
    "i'd": "i would", "you'd": "you would", "he'd": "he would", "she'd": "she would",
    "we'd": "we would", "they'd": "they would",
    "that's": "that is", "what's": "what is", "let's": "let us",
    "who's": "who is", "there's": "there is", "here's": "here is",
}
CONTRACTIONS_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in CONTRACTIONS) + r")\b"
)


def expand_contractions(text: str) -> str:
    return CONTRACTIONS_PATTERN.sub(lambda m: CONTRACTIONS[m.group(0)], text)


def get_balanced(
    df: pd.DataFrame,
    sample_size: int = SAMPLE_SIZE,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    per_class = sample_size // 2
    negative = df[df["target"] == 0].sample(n=per_class, random_state=random_state)
    positive = df[df["target"] == 4].sample(n=per_class, random_state=random_state)
    balanced = pd.concat([negative, positive])
    return balanced

def get_sampled(
    df: pd.DataFrame,
    frac: float = 1.0,
    random_state: int = RANDOM_STATE
) -> pd.DataFrame:
    sampled = df.sample(frac=frac, random_state=random_state).reset_index(drop=True)
    return sampled

def sampling(input_path, sampled_path):
    df = pd.read_csv(input_path, header=None, names=COLUMNS, encoding="latin-1")
    balanced = get_balanced(df)
    sampled = get_sampled(balanced)
    sampled.to_csv(sampled_path, index=False)




def clean_text(text: str) -> str:
    text = text.lower()
    text = URL_PATTERN.sub(" ", text)
    text = MENTION_PATTERN.sub(" ", text)
    text = EMOJI_PATTERN.sub(" ", text)
    text = expand_contractions(text)
    text = NON_ALPHA_PATTERN.sub(" ", text)
    text = MULTI_SPACE_PATTERN.sub(" ", text).strip()
    return text


def get_cleaned(df) -> pd.DataFrame:
    df["clean_text"] = df["text"].astype(str).map(clean_text)

    df["label"] = (df["target"] == 4).astype(int)
    df = df.drop(columns=["target"])

    before = len(df)
    df = df[df["clean_text"].str.len() > 0].reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"Remove empty text after cleaning: {dropped}")
    return df

def cleaning(sampled_path, cleaned_path):
    df = pd.read_csv(sampled_path)
    cleaned = get_cleaned(df)
    cleaned.to_csv(cleaned_path, index=False)





def tokenize_and_pad(texts: pd.Series) -> tuple[Tokenizer, np.ndarray]:
    tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token=OOV_TOKEN)
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=MAX_LEN, padding="pre", truncating="pre")

    # tokenizer를 반환하는 이유는 테스트 데이터가 들어왔을 때 똑같은 규칙으로 번역해야하기 때문
    return tokenizer, padded



def preprocessing(cleaned_path, tokenizer_path, output_path):
    df = pd.read_csv(cleaned_path)
    tokenizer, padded = tokenize_and_pad(df["clean_text"])
    vocab_size = min(VOCAB_SIZE, len(tokenizer.word_index) + 1)
    labels = df["label"].to_numpy()
    X_train, X_val, y_train, y_val = train_test_split(
        padded,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )
    np.savez(
        output_path,
        X_train=X_train,
        X_val=X_val,
        y_train=y_train,
        y_val=y_val,
    )
    with open(tokenizer_path, "w", encoding="utf-8") as f:
        f.write(tokenizer.to_json())


if __name__ == "__main__":
    sampling(INPUT_PATH, SAMPLED_PATH)
    cleaning(SAMPLED_PATH, CLEANED_PATH)
    preprocessing(CLEANED_PATH, TOKENIZER_PATH, OUTPUT_PATH)
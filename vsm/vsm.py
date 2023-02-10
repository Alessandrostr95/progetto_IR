import json
import numpy as np

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import Counter

# CONSTANTS
JSON_FILE = 'series_data.json'
TITLE = 'Series_Title'
OVERVIEW = 'Overview'

# COLOR FOR LOGGING
RED='\033[0;31m'
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
END='\033[0m'

# PROCESS DATA
def load_data() -> list[dict]:
    """
        Load the dataset as a list of dictionaries.
    """
    with open(JSON_FILE, 'r', encoding='utf8') as f:
        return json.load(f)

def load_processed_data(log=False) -> list[dict]:
    data = load_data()

    N = len(data)
    c = 0
    for i in range(N):
        d = data[i]
        d['id'] = i
        title_tokens = word_tokenize(str(preprocess(d[TITLE])))
        overview_tokens = word_tokenize(str(preprocess(d[OVERVIEW])))
        d['title_tokens'] = title_tokens 
        d['overview_tokens'] = overview_tokens
        
        c += 1
        if log and c % 100 == 0:
            print(f'{CYAN}[LOAD]{END}\t{c} of {N} document processed.')
    
    if log:
        print(f'{GREEN}[DONE]{END}')

    return data


def compute_df(data : list[dict]) -> dict:
    DF = {}
    N = len(data)
    for i in range(N):
        tokens = data[i]['title_tokens'] + data[i]['overview_tokens']
        for w in tokens:
            s = DF.get(w, set())
            s.add(i)
            DF[w] = s

    for k in DF.keys():
        DF[k] = len(DF[k])

    return DF

def compute_tfidf(data : list[dict], DF : dict | None = None) -> dict:
    if DF == None:
        DF = compute_df(data)

    N = len(data)
    TF_IDF = {}

    for i in range(N):
        tokens = data[i]['title_tokens'] + data[i]['overview_tokens']
        counter = Counter(tokens)
        for t in np.unique(tokens):     # rappresentazione densa
            tf = counter[t] / len(counter)
            df = DF.get(t, 0)   # e' sempre > 0, pero' non si sa mai ...
            idf = np.log((N+1)/(df+1))
            TF_IDF[data[i]['id'], t] = tf * idf
    return TF_IDF

# VECTOR SPACE MODEL
def vector_space(data : list[dict]):
    DF = compute_df(data)
    VOCABULARY = list(DF.keys())
    TF_IDF = compute_tfidf(data, DF)

    N = len(data)
    D = np.zeros((N, len(VOCABULARY)))
    
    for doc, term in TF_IDF:
        ind = VOCABULARY.index(term)
        D[doc][ind] = TF_IDF[(doc, term)]
    
    return D

def cosine_similarity(a,b):
    return np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b))

## STRING PROCESSING
def lower_case(text: str | np.ndarray) -> np.ndarray:
    return np.char.lower(text)

def remove_stopwords(text : str | np.ndarray, lang : str = 'english') -> np.ndarray:
    stop_words = stopwords.words(lang)
    tokens = word_tokenize(str(text))
    return np.array(' '.join([word for word in tokens if not word in stop_words]))

def remove_punctuation(text: str | np.ndarray) -> np.ndarray:
    symbols = '!"#$%&()*+-./:;<=>?@[]\\^_~`{}|\n£°'
    for s in symbols:
        text = np.char.replace(text, s, '')
    text = np.char.replace(text, ',', '')
    return text

def remove_apostrophe(text : str | np.ndarray) -> np.ndarray:
    return np.char.replace(text, "'", '')

def stemming(text : str | np.ndarray) -> np.ndarray:
    stemmer = PorterStemmer()
    tokens = word_tokenize(str(text))
    return np.array(' '.join([stemmer.stem(w) for w in tokens]))

def preprocess(text: str | np.ndarray) -> np.ndarray:
    text = lower_case(text)
    text = remove_punctuation(text)
    text = remove_apostrophe(text)
    text = remove_stopwords(text)
    text = stemming(text)
    text = remove_punctuation(text)
    text = remove_apostrophe(text)
    return text

# MAIN
if __name__ == "__main__":
    data = load_processed_data(log=True)
    D = vector_space(data)
    print(D)

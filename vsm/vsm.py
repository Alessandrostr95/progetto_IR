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
        Loads the dataset as a list of dictionaries.
    """
    with open(JSON_FILE, 'r', encoding='utf8') as f:
        return json.load(f)

def load_processed_data(log=False) -> list[dict]:
    """
        Loads & Process the dataset as a list of dictionaries.
        It adds this extra field in datas:
            - `id`: an unique integer identifier.
            - `title_tokens`: a list of title's **processed** tokens.
            - `overview_tokens`: a list of overview's **processed** tokens.
    """
    data = load_data()

    N = len(data)
    c = 0
    for d in data:
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
    """
        Computes the **document frequency** of each term of our collection `data`.
        The structure of the map is {`term`->`df`}.
    """
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
    """
        Computes the **tf-idf** representation of each document in our collection `data`.
        The structure of the map is {`docID`->{`term`->`tf-idf`}}.
        It is a **sparse representation** of our space vector model.
    """
    if DF == None:
        DF = compute_df(data)

    N = len(data)
    TF_IDF = {}

    for i in range(N):
        vec = TF_IDF.setdefault(data[i]['docID'], dict())
        tokens = data[i]['title_tokens'] + data[i]['overview_tokens']
        counter = Counter(tokens)
        for t in np.unique(tokens):     # rappresentazione sparsa
            tf = counter[t] / len(counter)
            df = DF.get(t, 0)   # e' sempre > 0, pero' non si sa mai ...
            idf = np.log((N+1)/(df+1))
            vec[t] = tf * idf
    return TF_IDF

# VECTOR SPACE MODEL
def vector_space(data : list[dict]) -> np.ndarray:
    """
        Returns a **dense** matrix with all TF_IDF vector.
    """
    DF = compute_df(data)
    VOCABULARY = list(DF.keys())
    TF_IDF = compute_tfidf(data, DF)

    N = len(data)
    M = np.zeros((N, len(VOCABULARY)))
    
    for doc_id in TF_IDF:
        for term in TF_IDF[doc_id]:
            ind = VOCABULARY.index(term)
            M[doc_id][ind] = TF_IDF[doc_id][term]
    
    return M

def query2vec(query : str | np.ndarray, DF : dict | None = None, collection_size : int | float = 2000) -> dict:
    """
        Returns a **sparse** tf-idf vecotr of the string `query`.
    """
    
    # Load DF if missing
    if DF == None:
        print(f"{PURPLE}[WARNING]{END}\tMissing document frequency.")
        data = load_processed_data(log=True)
        DF = compute_df(data)
        print(f"{GREEN}[DONE]{END}\tDocs frequency computed.")
        collection_size = len(data)

    tokens = word_tokenize(str(preprocess(query)))
    VEC = {}
    counter = Counter(tokens)
    for t in np.unique(tokens):     # rappresentazione sparsa
        tf = counter[t] / len(counter)
        df = DF.get(t, 0)   # potrebbe essere pari a 0 se nella query ci sono termini non presenti nel mio vocabolario
        idf = np.log((collection_size+1)/(df+1))
        VEC[t] = tf * idf

    return VEC

def cosine_similarity(a, b) -> float:
    """
        Dense & Sparse implementation of cosine similarity.
    """
    if type(a) == type(b) == np.ndarray:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    elif type(a) == type(b) == dict:
        norm_a = np.linalg.norm(list(a.values()))
        norm_b = np.linalg.norm(list(b.values()))

        terms = list(set(a.keys()) & set(b.keys()))
        s = 0
        for t in terms:
            s += a[t] * b[t]
        
        return s / (float(norm_a) * float(norm_b))
    else:
        return 0

def add(x : dict, y : dict) -> dict:
    """
        **Sparse** implementation of add operator.
    """
    terms = list(set(x.keys()) | set(y.keys()))
    return {t : x.get(t, 0) + y.get(t, 0) for t in terms}

def mult(x : dict, t : int | float) -> dict:
    """
        **Sparse** implementation of scalar multiplication operator.
    """
    return {k: v*t for k, v in x.items()}

def sub(x : dict, y : dict) -> dict:
    """
        **Sparse** implementation of subtract operator.
    """
    return add(x, mult(y, -1))

def mean(vectors : list[dict]) -> dict:
    """
        **Sparse** implementation of mean vector.
    """
    mu = dict()

    if (N := len(vectors)) == 0:
        return mu
    
    for v in vectors:
        mu = add(mu, v)

    return mult(mu, 1/N)
    

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

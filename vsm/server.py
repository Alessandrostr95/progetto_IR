from flask import Flask, abort, request 
import requests
import vsm

app = Flask(__name__)

DATA = vsm.load_processed_data(log=True)
DF = vsm.compute_df(DATA)
TF_IDF = vsm.compute_tfidf(DATA, DF)

URL = 'http://127.0.0.1:5000'

def get_vector(ids) -> dict:
    """
        Given a list of **docID**s returns their **sparse** vectore representation.
    """
    result = {}
    for id in ids:
        if (vec := TF_IDF.get(id, None)):
            result[id] = vec
    return result

def rocchio(
        query : dict,
        relevants : list[dict] = [],
        non_relevants : list[dict] = [],
        alpha : float = .3,
        beta : float = .3,
        gamma : float = .3
    ) -> dict:

    C_r = vsm.mean(relevants)
    C_nr = vsm.mean(non_relevants)
    
    q = vsm.mult(query, alpha)

    C_r = vsm.mult(C_r, beta)
    q = vsm.add(q, C_r)

    C_nr = vsm.mult(C_nr, gamma)
    q = vsm.add(q, C_nr)
    
    return q


#### APIs

@app.route('/rf_score', methods=['POST'])
def rf_score():

    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        abort(400)
    
    if not (data := request.get_json()):
        abort(400)

    query = data.get('fields', dict())
    relevants = data.get('relevants', [])
    non_relevants = data.get('non-relevants', [])
    
    query_str = query.get(vsm.TITLE, '') + query.get(vsm.OVERVIEW, '')
    query_vec = vsm.query2vec(query_str, DF)

    headers = {'Content-Type' : 'application/json'}
    r = requests.post(
        f'{URL}/rocchio',
        json = {
            'query' : query_vec,
            'relevants' : relevants,
            'non-relevants' : non_relevants
        },
        headers = headers
    )

    if r.status_code != 200:
        abort(r.status_code)

    new_query_vec = r.json()

    r = requests.post(
        f'{URL}/score',
        json = { 'query' : new_query_vec },
        headers = headers
    )

    if r.status_code != 200:
        abort(r.status_code)

    score = r.json()

    return score


@app.route('/score', methods=['POST'])
def score():
    """
        The post body is a json with this content:
            - `query`: a **sparse** representation of the query.
        Returns a **map** s.t. for each docID we have the **cosine similarity**.
    """
    content_type = request.headers.get('Content-Type')

    if content_type != 'application/json':
        abort(400)
    
    if not (data := request.get_json()):
        abort(400)

    query = data.get('query', dict())
    result = {}
    for doc in DATA:
        id = doc['docID']
        if (vec := TF_IDF.get(id, None)):
            result[id] = vsm.cosine_similarity(query, vec)

    return result

@app.route('/rocchio', methods=['POST'])
def relevance_feedback():
    """
        The post body is a json with this content:
            - `query`: a **sparse** representation of the query.
            - `relevants`: a list of relevant document's doc ids.
            - `non-relevants`: a list of relevant document's doc ids.
        Returns a new query vecotr computed with [Rocchio's algorithm](https://en.wikipedia.org/wiki/Rocchio_algorithm).
    """
    content_type = request.headers.get('Content-Type')

    if content_type != 'application/json':
        abort(400)
    
    if not (data := request.get_json()):
        abort(400)

    query_vec = data.get('query', dict())
    relevants = data.get('relevants', [])
    non_relevants = data.get('non-relevants', [])

    relevant_vec = list(get_vector(relevants).values())
    non_relevant_vec = list(get_vector(non_relevants).values())

    new_query = rocchio(query_vec, relevant_vec, non_relevant_vec)
    return new_query

@app.route('/vectorize', methods=['POST'])
def vectorize():
    """
        Posting a **query** as:
            1. a **text/plain** string.
            2. an **application/json** json, like this `{ "query" : "my query string" }`
        returns its **sparse** vector representation.
    """
    content_type = request.headers.get('Content-Type')
    query = ''

    if content_type == 'application/json':
        payload = request.get_json()
        if payload == None:
            return '{}'
        query = payload['query']
    elif content_type == 'text/plain':
        query = request.get_data(as_text=True)

    query_vec = vsm.query2vec(query, DF, len(TF_IDF))
    return query_vec

@app.route('/', methods=['POST'])
def get_vectors():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        abort(400)

    ids = request.get_json()
    vectors = get_vector(ids)

    return vectors

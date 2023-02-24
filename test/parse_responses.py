import csv
from re import findall

# List of queries
queries = ["family"]
# Relevance judgments, e.g.: {"family": [2,3,4]} indicates that for "family" query, docID 2,3,4 are relevants
judgments = {}

for query in queries:
    judgments[query] = []
    with open(f'risposte/solr/Serie che parlano di {query}.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Itera su tutte le coppie (chiave, valore)
            for item in row.items():
                # Se la serie è rilevante, inserisci il docID nella lista dei giudizi relativa alla serie in questione
                if item[1] == "Rilevante":
                    judgments[query].append(int(findall(r".*docID:(\d+)", item[0])[0]))
print(judgments)
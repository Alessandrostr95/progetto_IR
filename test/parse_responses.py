import os
import csv
from re import findall

SOLR_DIR = "judgments/solr/"
RF_DIR = "judgments/rf/"

def parse_responses(dir : str = SOLR_DIR) -> dict:
    '''
    Params:
    - dir: directory of csv files

    Returns: a dict of <query, list of relevants docIDs>
    '''
    # Relevance judgments, e.g.: {"family": [2,3,4]} indicates that for "family" query, docID 2,3,4 are relevants
    judgments = {}

    with os.scandir(dir) as csv_dir:
        # Iterate over directory files
        for file in csv_dir:
            # Read only csv files from directory
            _, file_extension = os.path.splitext(file.name)
            if file_extension != ".csv":
                continue
            query = findall(r"Serie che parlano di (.*)\.csv", file.name)[0]
            judgments[query] = []
            with open(file.path) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Itera su tutte le coppie (chiave, valore)
                    for item in row.items():
                        # Se la serie è rilevante, inserisci il docID nella lista dei giudizi relativa alla serie in questione
                        if item[1] == "Rilevante":
                            judgments[query].append(int(findall(r".*docID:(\d+)", item[0])[0]))
    return judgments

if __name__ == "__main__":
    print(parse_responses())
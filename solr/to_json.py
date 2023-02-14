import pandas as pd

CSV_PATH = "./series_data.csv"
JSON_PATH = "./series_data.json"

if __name__ == "__main__":
    data = pd.read_csv(CSV_PATH)
    
    data['Genre'] = data['Genre'].apply(lambda x: x.split(", "))
    data['docID'] = range(len(data))   # ADD DOC_ID
    data['Actors'] = data[['Star1', 'Star2', 'Star3', 'Star4']].values.tolist()

    del data['Star1']
    del data['Star2']
    del data['Star3']
    del data['Star4']

    json_data = data.to_json(orient="records", indent=4)

    with open(JSON_PATH, "w") as f:
        f.write(json_data)


import pandas as pd

CSV_PATH = "./series_data.csv"
JSON_PATH = "./series_data.json"

if __name__ == "__main__":
    data = pd.read_csv(CSV_PATH)
    
    data["Genre"] = data["Genre"].apply(lambda x: x.split(", "))

    json_data = data.to_json(orient="records", indent=4)

    with open(JSON_PATH, "w") as f:
        f.write(json_data)


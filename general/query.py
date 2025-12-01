import requests

def query_data():
    try:
        r = requests.get("http://127.0.0.1:5001/data", timeout=1)
        return r.json()
    except Exception as e:
        print("Query failed:", e)
        return None


if __name__ == "__main__":
    while True:
        data = query_data()
        if data is not None:
            print("Queried data:", data)
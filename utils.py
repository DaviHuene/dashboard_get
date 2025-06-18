import requests
import pandas as pd

def consultar_api(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return pd.DataFrame(response.json())
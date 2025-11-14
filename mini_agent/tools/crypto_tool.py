# tools/crypto_tool.py
import requests

def crypto_tool():
    """
    Fetch current Bitcoin price in USD.
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        price = data["bitcoin"]["usd"]
        return f"Bitcoin price is ${price} USD."
    except Exception as e:
        return f"Error fetching Bitcoin price: {e}"

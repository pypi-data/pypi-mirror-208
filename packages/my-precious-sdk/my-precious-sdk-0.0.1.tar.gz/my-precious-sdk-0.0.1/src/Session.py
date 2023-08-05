import requests
from .config import API_KEY

session = requests.Session()
session.headers.update(
    {"Accept": "application/json", "Authorization": f"Bearer {API_KEY}"}
)
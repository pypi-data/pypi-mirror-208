import datetime
import random
import requests
import json
from .config import UNSPLASH_ACCESS_KEY


def dailyimg():
    fecha_actual = datetime.date.today().strftime('%Y-%m-%d')
    url = f'https://api.unsplash.com/photos/random?query=landscape&orientation=landscape&client_id={UNSPLASH_ACCESS_KEY}'
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        foto = json.loads(respuesta.text)
        return {
            'id': foto['id'],
            'url': foto['urls']['regular'],
            'autor': foto['user']['name'],
            'fecha': fecha_actual,
        }
    else:
        return None

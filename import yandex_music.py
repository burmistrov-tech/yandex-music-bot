import yandex_music
from yandex_music import Client

client = Client()

result = client.search('платина - бандана')

print(result)
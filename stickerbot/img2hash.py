import json
import imagehash
from PIL import Image
from io import BytesIO
import requests

# Parse emoji files
filename = "emojis.txt"

with open(filename) as json_file:
    image_urls = (json.load(json_file))

image_hashes = {}

for key, url in image_urls['all'].items():
    r = requests.get(url)

    try:
        i = Image.open(BytesIO(r.content))
        image_hashes[key] = (url, str(imagehash.average_hash(i)))
    except Exception as e:
        image_hashes[key] = url
        print(f"For image {key} with url={url}, Error: {e} ")

image_urls['all'] = image_hashes
with open(f"{filename}_hashes.json", 'w') as outfile:
    json.dump(image_urls, outfile)

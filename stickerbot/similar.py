import imagehash
from PIL import Image
import json

# Parameters: image in BytesIO, path for hashes to check, cutoff default = 15, minimum bit differenxe
# Returns: most similar image's path if it exists, if not returns False
def is_similar(source_img, target_path="emojis.txt_hashes.json", cutoff=15):

    # Convert BytesIO to PIL
    source_img = Image.open(source_img)

    # Fix transparency issue
    source_img = source_img.convert('RGB')

    # Get hash of source img
    hash0 = imagehash.average_hash(source_img) 

    # Target hashes to compare against
    with open(target_path) as file:
        target_imgs = (json.load(file))['all']

    # Iterate through all images in db
    for name, value in target_imgs.items():
        
        # Unpack value
        url = value[0]
        hash1 = imagehash.hex_to_hash(value[1])

        # maximum bits that could be different between the hashes. 
        if hash0 - hash1 < cutoff:
            return url, str(hash0), name
    
    # No similar image found
    return False, str(hash0)
#create a favourite category in the filters list

emojifile = 'emojis.txt_hashes.json'
import json


with open(emojifile) as json_file:
    data = (json.load(json_file))
data['filters']['favourites'] = dict.fromkeys(data['all'].keys(), 0)

with open(emojifile, 'w') as outfile:
    json.dump(data, outfile)
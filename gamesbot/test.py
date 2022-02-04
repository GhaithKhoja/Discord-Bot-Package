import json

# a = {"mahz": {"wins": 1, "wins/X": 1, "wins/O":0}}
# b = {"huss": {"wins": 3, "wins/X": 2, "wins/O":1}}


test_dict = {"Leaderboard": "xoxo"}
# test_dict.update(a)
# test_dict.update(b)

# print(test_dict)


# json.dumps(test_dict, "leaderboard.json")


with open('leaderboard.json', 'w') as fp:
    json.dump(test_dict, fp)

# with open('leaderboard.json', 'r') as fp:
#     data = json.load(fp)

# for key, value in data.items():
#     print(key, value)

# for key in data.keys():
#     print(key)
# print(data['user'])
# print(type(data))
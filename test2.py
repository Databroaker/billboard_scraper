import pickle

with open("1990-rock-songs.pkl", "rb") as f:
    data = pickle.load(f)
    print(data)


import json
import pickle




def save_pickle(fpath: str,
                data: dict):
    with open(fpath, 'wb') as obj:
        pickle.dump(data, obj, protocol=pickle.HIGHEST_PROTOCOL)

def load_pickle(fpath: str) -> dict:
    with open(fpath, 'rb') as obj:
        return pickle.load(obj)

def save_json(fpath, obj):
    with open(fpath, 'w') as fp:
        json.dump(obj, fp, sort_keys=True, indent=4)

def load_json(fpath):
    with open(fpath, 'r') as fp:
        return json.load(fp)
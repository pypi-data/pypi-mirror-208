import json
import os

FILE_PATH = "users.json"


def create_file(file_path=FILE_PATH):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write()


def load_user_data(user_id, file_path=FILE_PATH):
    with open(file_path, "r") as f:
        users = json.load(f)
    try:
        return users[user_id]
    except KeyError:
        return {}


def dump_user(user_id, user_data, file_path=FILE_PATH):
    user_attributes = ["skill_score", "state", "start", "stop", "step", "answer"]
    with open(file_path, "r") as f:
        users = json.load(f)
    users[user_id] = {}
    for attr in user_attributes:
        try:
            users[user_id][attr] = user_data[attr]
        except KeyError:
            pass
    with open(file_path, "w") as f:
        f.write(json.dumps(users))

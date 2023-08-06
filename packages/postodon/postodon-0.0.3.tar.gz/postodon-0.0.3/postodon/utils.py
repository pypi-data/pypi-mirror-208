import json
import shutil


def read_db(post_list):
    with open(post_list, "r") as file_pointer:
        data = json.load(file_pointer)
    return data


def write_db(post_list, data):
    shutil.copy(post_list, post_list + ".bup")
    with open(post_list, "w") as file_pointer:
        json.dump(data, file_pointer, sort_keys=True, indent=4)

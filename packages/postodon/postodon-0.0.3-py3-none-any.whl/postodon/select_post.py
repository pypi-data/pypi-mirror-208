import random
import sys

from . import utils


def get_candidates(data, status):
    candidates = [item["id"] for item in data if item["status"] == status]
    return candidates


def select_post_from(candidates):
    element = random.randrange(0, len(candidates))
    return candidates[element]


def get_index_from_id(data, selected_id):
    filtered_list = filter(lambda d: d["id"] == selected_id, data)
    # Only returns the first element (where "id" == selected_id) but "id" is unique
    return data.index(next(filtered_list))


def get_post(data):
    update_database_after = not "-n" in sys.argv

    # Select from the already-posted list as a backup if the unposted list is empty
    candidates = get_candidates(data, "unposted")

    if len(candidates) == 0:
        candidates = get_candidates(data, "posted")

    if len(candidates) == 0:
        print("No candidate posts")
        sys.exit()

    # Select an item to post
    selected_id = select_post_from(candidates)

    # Get the list element of the post which has this id
    selected_index = get_index_from_id(data, selected_id)

    selected_post = data[selected_index]["content"]

    if len(selected_post) > 500:
        print("Post too long:", selected_id)
        sys.exit()

    if ".png" in selected_post:
        print("Posting images not available yet", selected_id)
        sys.exit()

    if update_database_after:
        data[selected_index]["status"] = "posted"

    return selected_post


def main(post_list):
    data = utils.read_db(post_list)
    post = get_post(data)
    utils.write_db(post_list, data)
    return post

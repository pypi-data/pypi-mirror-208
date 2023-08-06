from . import utils


def main(post_list, post_text):
    data = utils.read_db(post_list)
    item = {
        "id": max([iitem["id"] for iitem in data]) + 1,
        "status": "unposted",
        "content": post_text,
    }
    data.append(item)
    utils.write_db(post_list, data)
    return

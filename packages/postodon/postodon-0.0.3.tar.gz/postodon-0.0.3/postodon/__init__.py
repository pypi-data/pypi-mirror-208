#!/usr/bin/env python3

import json
import sys

from . import append_post
from . import select_post
from . import submit_post

CONFIG_FILENAME = "config.json"


# Helpers


def read_config():
    with open(CONFIG_FILENAME, "r") as file_pointer:
        config = json.load(file_pointer)
    return config


# Actions


def post():
    config = read_config()
    post = select_post.main(config["post_list"])
    print(post)
    if "-n" not in sys.argv:
        submit_post.main(config["instance_name"], post)


def add(post_text):
    config = read_config()
    append_post.main(config["post_list"], post_text)


# Main - entry point


def main(action="post"):
    try:
        action = sys.argv[1]
    except IndexError:
        action = "post"
    try:
        post_text = sys.argv[2]
    except IndexError:
        if action == "add":
            print("Provide post text")
            sys.exit()
    if action == "post":
        post()
    elif action == "add":
        add(post_text)
    else:
        print("Unknown action:", action)
        sys.exit()

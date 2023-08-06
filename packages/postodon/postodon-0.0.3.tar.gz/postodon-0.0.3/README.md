# postodon

[![PyPI](https://img.shields.io/pypi/v/postodon.svg)](https://pypi.org/project/postodon/)
[![Changelog](https://img.shields.io/github/v/release/msleigh/postodon?include_prereleases&label=changelog)](https://github.com/msleigh/postodon/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/msleigh/postodon/blob/main/LICENSE)

Randomly posts things to Mastadon from a list using the API.

The list of posts is a JSON file:

    [
        {"content": "Text of the post", "id": 1, "status": "unposted"},
        ...,
    ]

The command `postodon` randomly selects an unposted post, posts it to Mastodon, and marks it as posted in the list. If there are no unposted items, an already-posted item is used instead.

## Installation

Install:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install postodon

## Usage

### Setup

 - Register an application as described here: https://docs.joinmastodon.org/client/token/#app
 - Get an access token as described here: https://docs.joinmastodon.org/client/authorized/#flow
 - Securely store the returned `access_token` for future reference
 - Edit `config.json` to include the name of the Mastodon instance and the name of the posts file, e.g. `posts.json`

### Use

To use, put the access token in an environment variable called `AUTH_TOKEN`:

    export AUTH_TOKEN=<your_access_token_here>

To publicly post a random post, marked as English, and update the list (mark the post having been posted):

    postodon

(This is a shortcut for `postodon post`). NB if there are no unposted posts left in the list, this will return a random post from the 'posted' selection.

To select a random post from the list without either updating the list or posting (dry-run mode):

    postodon post -n

To add new posts to the list for future posting:

    postodon add "Text of post"

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

    cd postodon
    python -m venv .venv
    source .venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[dev,tests]'

To run the tests:

    pytest

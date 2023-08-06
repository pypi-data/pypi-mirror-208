import json
import os
import requests
import sys


def output(response):
    print()
    print(json.dumps(json.loads(response.text), indent=4))
    print()
    print("Status code = ", response.status_code)


def main(instance_name, text):
    url = "https://" + instance_name + "/api/v1/statuses"
    data = {"status": text}
    headers = {"Authorization": "Bearer " + os.environ["AUTH_TOKEN"]}

    response = requests.post(url, data=data, headers=headers)

    if response.status_code != 200:
        output(response)

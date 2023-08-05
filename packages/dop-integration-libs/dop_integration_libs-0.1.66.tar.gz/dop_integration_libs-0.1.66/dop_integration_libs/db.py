
import requests
from dop_integration_libs.environment import Environment
from typing import List
from typing import Union


class Db(object):
    def __init__(self, db_name: str, env: Environment):
        self.db = db_name
        self.env = env

    def insert(self, data: dict) -> Union[bool, None]:
        url = f"{self.env.LOG_API_BASE_URL}/remote-cache/db"
        print(f"DB URL: {url}")
        headers = {
            "Authorization": f"Bearer {self.env.LOG_API_TOKEN}",
            "Content-Type": "application/json"
        }
        body = {
            "meta":
            {
                "id_field": "id",
                "db_name": self.db
            },
            "data": data
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return True
        else:
            print(f"Error: {response.text} - {response.status_code}")
            return None

    def update(self, filters: Union[dict, List[dict]], data: dict):
        url = f"{self.env.LOG_API_BASE_URL}/remote-cache/db/update"
        headers = {
            "Authorization": f"Bearer {self.env.LOG_API_TOKEN}",
            "Content-Type": "application/json"
        }
        body = {
            "db_name": self.db,
            "filters": filters,
            "data": data
        }
        response = requests.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return True
        else:
            print(f"Error: {response.text} - {response.status_code}")
            return None

    def find(self, filters: Union[dict, list[dict]]) -> Union[list[dict], None]:
        url = f"{self.env.LOG_API_BASE_URL}/remote-cache/db"
        headers = {
            "Authorization": f"Bearer {self.env.LOG_API_TOKEN}"
        }
        body = {
            "db_name": self.db,
            "filters": filters
        }
        response = requests.put(url, headers=headers, json=body)
        if response.status_code == 200:
            return response.json()
        else:
            return None

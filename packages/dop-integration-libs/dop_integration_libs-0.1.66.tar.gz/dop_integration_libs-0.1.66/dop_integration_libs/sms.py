import json
import requests
from requests.auth import HTTPBasicAuth
from .environment import Environment


class Sms(object):
    def __init__(self, env: Environment):
        self.env = env

    def send(self, to: str, message: str):
        url = f"{self.env.SMS_URL}/Submit"
        print(f"SMS URL: {url}")
        print(self.env.SMS_USERNAME, self.env.SMS_PASSWORD)
        print(self.env.SMS_TITLE)
        body = {
            "Credential": {
                "Username": self.env.SMS_USERNAME,
                "Password": self.env.SMS_PASSWORD
            },
            "DataCoding": "Default",
            "Header": {
                "From": self.env.SMS_TITLE,
                "ValidityPeriod": 0
            },
            "To": [to],
            "Message": message
        }
        print(body)
        response = requests.post(url, json=body)
        print("===SMS====")
        print(f"SMS Response: {response.status_code}")
        print(f"SMS Body: {response.text}")
        return True

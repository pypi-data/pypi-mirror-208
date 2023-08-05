import requests
import json
from typing import Union


class PublicApiResponse(object):
    def __init__(self):
        self.TOKEN = ""
        self.public_api_url = ""
        self.CATALOG = 0
        self.MENU = 0

    def __str__(self):
        return f"TOKEN: {self.TOKEN}, CATALOG: {self.CATALOG}, MENU:\
        {self.MENU} {self.public_api_url}"

    def update_service_number(self, service_id: int, new_service_number: int) -> Union[bool, None]:
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        data = {"service_id": service_id,
                "new_service_number": new_service_number}
        api_endpoint = f"{self.public_api_url}/publicapi/order/update-service-number"
        print(api_endpoint)
        response = requests.post(api_endpoint, json=data, headers=headers)
        if response.status_code == 200:
            return True
        else:
            print(f"Error fetching orders: {response.status_code}")
            return None

    def accept_table(self, service_id: int) -> Union[bool, None]:
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        api_endpoint = f"{self.public_api_url}/publicapi/product/accept-table/{service_id}"
        response = requests.get(api_endpoint, headers=headers)
        if response.status_code == 200:
            return True
        else:
            print(f"Error accepting table: {response.status_code}")
            return None

    def cancel_table(self, service_id: int) -> Union[bool, None]:
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        api_endpoint = f"{self.public_api_url}/publicapi/product/cancel-table/{service_id}"
        response = requests.get(api_endpoint, headers=headers)
        if response.status_code == 200:
            return True
        else:
            print(f"Error canceling table: {response.status_code}")
            return None

    def fetch_orders(self, last_service_id):
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        data = {"last_service_id": last_service_id}
        api_endpoint = f"{self.public_api_url}/publicapi/product/table-orders"
        response = requests.post(api_endpoint, json=data, headers=headers)
        if response.status_code == 200:
            # data = response.json()
            data = json.loads(response.text)
            return data.get("data", [])
        else:
            print(f"Error fetching orders: {response.status_code}")
            return None

    def save_product(self, data: dict) -> Union[bool, None]:
        url = f"{self.public_api_url}/publicapi/product"
        headers = {
            "Authorization": f"Bearer {self.TOKEN}"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return True
        else:
            print(f"Error: {response.text} - {response.status_code}")
            return None

    def cancel_service_products(self, data: dict) -> Union[bool, None]:
        url = f"{self.public_api_url}/publicapi/order/cancel-service-products"
        headers = {
            "Authorization": f"Bearer {self.TOKEN}"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return True
        else:
            print(f"Cancel Error: {response.text} - {response.status_code}")
            return None

    def complete_sync(self, service_id):
        """
        ilgili servis için senkronizasyonu tamamlandı olarak işaretler
        """
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        api_endpoint = f"{self.public_api_url}/publicapi/product/sync-complete/{service_id}"
        response = requests.get(api_endpoint, headers=headers)
        print(f"--> response: {response.status_code}")
        return response.status_code == 200

    def trigger_cancel(self):
        """
        Cancel işlemlerini trigger eder
        """
        headers = {"Authorization": f"Bearer {self.TOKEN}"}
        api_endpoint = f"{self.public_api_url}/publicapi/system/trigger-cancels"
        response = requests.get(api_endpoint, headers=headers)
        print(f"--> trigger cancel response: {response.status_code}")
        return response.status_code == 200


class PublicApi(object):
    def __init__(self, api_key: str, secret_key: str, public_api_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.public_api_url = public_api_url

    def fetch(self) -> Union[PublicApiResponse, None]:

        url = f"{self.public_api_url}/publicapi/auth/login"
        body = {
            "apikey": self.api_key,
            "secretkey": self.secret_key,
        }
        response = requests.post(url, json=body)
        if response.status_code == 200:
            response = response.json()
            response_obj = PublicApiResponse()
            response_obj.TOKEN = response.get("access_token", "")
            response_obj.CATALOG = response.get("catalog", 0)
            response_obj.MENU = response.get("menu", 0)
            response_obj.public_api_url = self.public_api_url
            return response_obj
        else:
            return None

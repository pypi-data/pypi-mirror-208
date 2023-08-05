import requests
from stf.test_case.base import BaseTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import string
import random
from random import randint

import yaml
with open("xpath.yml", 'r') as ymlfile:
    xpath = yaml.full_load(ymlfile)


class MagentoApi(BaseTestCase):

    def delete_cookies(self):
        self.driver.delete_all_cookies()
        self.driver.refresh()
        time.sleep(5)

    # ----------------------------------------------------------------------------------------------------------------------

    def generate_admin_token(self):
        """Genera el bearer token"""

        admin_user = self.config['api_url']['admin_user']
        url_token = self.config['api_url']['host'] + self.config['api_url']['url_token']

        response = requests.post(url_token, json=admin_user)
        if response.status_code == 200:
            access_token = response.json()
            return access_token
        else:
            self.assertTrue(False, "Error token")

    def generate_user_token(self, customer_user):
        """Genera token de usuario"""

        url = self.config['api_url']['host_user'] + self.config['api_url']['user_token']

        headers = {
            "Authorization": "Bearer " + str(self.generate_admin_token()),
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=customer_user, headers=headers)
        if response.status_code == 200:
            access_token = response.json()
            return access_token
        else:
            return False
    def get_user_cart(self, customer_user):
        """trae el carrito del usuario pedido"""

        cart_endpoint = self.config['api_url']['host_user'] + self.config['api_url']['cart_endpoint']

        headers = {
            "Authorization": "Bearer " + str(self.generate_user_token(customer_user)),
            "Content-Type": "application/json"
        }
        response = requests.get(cart_endpoint, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data

    def delete_user_items(self, customer_user):
        """borra los elementos del carrito de un usuario"""

        deleted_cart_endpoint = self.config['api_url']['host_user'] + self.config['api_url']['delete_endpoint']

        headers = {
            "Authorization": "Bearer " + str(self.generate_user_token(customer_user)),
            "Content-Type": "application/json"
        }

        cart = self.get_user_cart(customer_user)

        if cart:
            if cart["items_count"] != 0:
                for item in cart['items']:
                    print("user_cart items: " + str(item["item_id"]))
                    cart_item = deleted_cart_endpoint + str(item["item_id"])
                    requests.delete(cart_item, headers=headers)
            else:
                print("sin items")
        else:
            print("carrito no existe")

    def get_product_salable_quantity(self, url):
        """Muestra la cantidad de stock disponible para la venta"""

        headers = {"Authorization": "Bearer " + str(self.generate_admin_token()) + ""}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            qty = response.text
            return qty
        else:
            self.assertTrue(False, "Error qty stock")

    def verify_product_salable(self, url):
        """Muestra si el producto esta disponible para la venta: devuelve un boolean"""

        headers = {"Authorization": "Bearer " + str(self.generate_admin_token()) + ""}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            product_salable = response.text
            return product_salable
        else:
            self.assertTrue(False, 'error when showing if the product is sellable')

    def update_source_stock(self, url, api_data_sku):
        """Actualiza el stock del source"""

        headers = {"Authorization": "Bearer " + str(self.generate_admin_token()) + ""}
        data = {
            "sourceItems": [
                {
                    "sku": api_data_sku["sku"],
                    "source_code": api_data_sku["source_code"],
                    "quantity": api_data_sku["quantity"],
                    "status": api_data_sku["status"]
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            source_items = response.text
            return source_items
        else:
            self.assertTrue(False, 'error in the update of the salable quantity')

    def create_customer(self, url, api_data_customer):
        """crea el cliente"""

        headers = {"Authorization": "Bearer " + str(self.generate_admin_token()) + ""}
        data = {
                "customer": {

                    "email": api_data_customer["email"],
                    "firstname": api_data_customer["firstname"],
                    "lastname": api_data_customer["lastname"],
                    "addresses": [
                        {
                            "region": {
                                "region_code": api_data_customer["region_code"],
                                "region": api_data_customer["region"],
                                "region_id": api_data_customer["region_id"]
                            },
                            "region_id": api_data_customer["region_id"],
                            "country_id": api_data_customer["country_id"],
                            "street": [
                                api_data_customer["street"]
                            ],
                            "telephone": api_data_customer["telephone"],
                            "postcode": api_data_customer["postcode"],
                            "city": api_data_customer["city"],
                            "firstname": api_data_customer["firstname"],
                            "lastname": api_data_customer["lastname"],
                            "vat_id": api_data_customer["vat_id"],
                            "default_shipping": api_data_customer["default_shipping"],
                            "default_billing": api_data_customer["default_billing"],
                            "custom_attributes": [
                                {
                                    "attribute_code": api_data_customer["numero"],
                                    "value": api_data_customer["value_number"]
                                },
                                {
                                    "attribute_code": api_data_customer["city_id"],
                                    "value": api_data_customer["value_city_id"]
                                },
                                {
                                    "attribute_code": api_data_customer["district_id"],
                                    "value": api_data_customer["value_district_id"]
                                },
                                {
                                    "attribute_code": api_data_customer["telephone_2"],
                                    "value": api_data_customer["value_telephone_2"]
                                }
                            ]
                        }
                    ]
                },
                "password": api_data_customer["password"]
                }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            customer_data = response.text
            return customer_data
        else:
            self.assertTrue(False, 'error create customer')

    def create_customer_account(self, url_customer_token, url_create_customer, customer, api_data_customer):
        """Verifica si el cliente existe y si no existe lo crea"""
        customer_status = self.verify_customer_exists(url_customer_token, customer)
        if not customer_status:
            self.create_customer(url_create_customer, api_data_customer)


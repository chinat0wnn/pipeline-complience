import requests
import json
from utils.logger import logger

class GrafanaService:
    def __init__(self, url, api_token):
        self.url = url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {api_token}"
        }

    def check_user_exists(self, email, login):
        """
        Verifica se um usuário existe usando /api/users/lookup.
        A API do Grafana permite buscar por loginOrEmail.
        """
        try:
            # Check by email
            response = requests.get(f"{self.url}/api/users/lookup", params={'loginOrEmail': email}, headers=self.headers)
            if response.status_code == 200:
                return True
            elif response.status_code == 401 or response.status_code == 403:
                raise Exception(f"Grafana Auth error ({response.status_code}): Unauthorized. Verifique as credenciais no .env.")
            
            # Check by login
            response = requests.get(f"{self.url}/api/users/lookup", params={'loginOrEmail': login}, headers=self.headers)
            if response.status_code == 200:
                return True
            elif response.status_code == 401 or response.status_code == 403:
                raise Exception(f"Grafana Auth error ({response.status_code}): Unauthorized. Verifique as credenciais no .env.")

            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking Grafana user existence: {e}")
            raise Exception(f"Failed to communicate with Grafana: {str(e)}")

    def create_user(self, name, email, login, password):
        """
        Cria um novo usuário via /api/admin/users.
        Requer privilégios de Admin (Basic Auth).
        """
        payload = {
            "name": name,
            "email": email,
            "login": login,
            "password": password
        }

        try:
            response = requests.post(
                f"{self.url}/api/admin/users",
                json=payload,
                headers=self.headers
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 412:
                raise Exception("Precondition Failed. User already exists or invalid data.")
            else:
                try:
                    error_msg = response.json().get('message', response.text)
                except ValueError:
                    error_msg = response.text
                raise Exception(f"Grafana API error ({response.status_code}): {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Grafana user: {e}")
            raise Exception(f"Failed to communicate with Grafana: {str(e)}")

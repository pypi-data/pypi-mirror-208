import requests
import os
from dotenv.main import load_dotenv
load_dotenv()

DOMAIN: str = os.getenv('DOMAIN', 'default-url')


class RemoteCirclesStorage:
    def __init__(self, base_url: str) -> None:
        self.base_url = DOMAIN

    def put(self, file_name: str, local_path: str, created_user_id: str, entity_type_id: str, profile_id: str) -> str:
        response = requests.post(f"{self.base_url}/graphql", json={
            "query": f'''
        mutation {{
          put(
            fileName: "{file_name}",
            local_path: "{local_path}",
            created_user_id: "{created_user_id}",
            entity_type_id: "{entity_type_id}",
            profile_id: "{profile_id}"
          )
        }}
      '''
        })

        response_data = response.json().get("data", {})
        if "errors" in response_data:
            raise Exception(response_data["errors"][0]["message"])

        return response_data["put"]

    def download(self, file_name: str, entity_type_id: str, profile_id: str, local_path: str) -> str:
        response = requests.post(f"{self.base_url}/graphql", json={
            "query": f'''
        mutation {{
          download(
            fileName: "{file_name}",
            entity_type_id: "{entity_type_id}",
            profile_id: "{profile_id}",
            localPath: "{local_path}"
          )
        }}
      '''
        })

        response_data = response.json().get("data", {})
        if "errors" in response_data:
            raise Exception(response_data["errors"][0]["message"])

        return response_data["download"]

import requests

from requests.exceptions import HTTPError


class DatasetService:
    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.api_url}/{self.client.api_version_snippet}/{self.client.api_myorg_snippet}"

    def refresh_dataset_in_group(self, dataset_id, group_id):
        refresh_url = self.base_url + f"/groups/{group_id}/datasets/{dataset_id}/refreshes"
        headers = self.client.auth_header
        response = requests.post(refresh_url, headers=headers)

        if response.status_code != 202:
            raise HTTPError(
                response, f"Failed when trying to refresh dataset {dataset_id}:\n{response.json()}"
            )

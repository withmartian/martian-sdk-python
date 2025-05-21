import httpx

from martian_apart_hack_sdk.backend_clients.judges import JudgesClient


class Backend:
    @property
    def _headers(self) -> dict[str, str]:
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
    def __init__(self, api_url, api_key, org_id):
        self.api_url = api_url
        self.org_id  = org_id
        self.api_key = api_key
        # TODO set base_url, api_key and org_id
        # http://127.0.0.1:8000/api/v1/organizations/{organization_id}/
        self.base_url = f"{api_url}/v1/organizations/{self.org_id}/"
        self._client = httpx.Client(base_url=self.base_url, headers=self._headers)
        # Lazy-load endpoint helpers
        self.judges: JudgesClient  = JudgesClient(self._client, self)
        # self.routers = RoutersClient(self._client)
        # self.jobs    = JobsClient(self._client)
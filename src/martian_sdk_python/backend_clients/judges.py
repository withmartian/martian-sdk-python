from martian_sdk_python.resources.judge import Judge


class JudgesClient:
    def __init__(self, httpx, backend):
        self._httpx = httpx
        self._backend = backend

    # C
    # def create(self, rubrics, llm) -> "Judge": …

    # R
    # def list(self, *, limit=100, cursor=None) -> list["Judge"]:
    #     resp = self._client.get("/judges", params=dict(limit=limit, cursor=cursor))
    #     return [Judge(**j, _http=self._client) for j in resp.json()["items"]]

    def get(self, judge_id: str) -> Judge:
        resp = self._httpx.get(f"/judges/{judge_id}")
        resp.raise_for_status()
        return Judge(**resp.json(), _backend=self._backend)

    # # U  (full or PATCH-style partial)
    # def update(self, judge_id: str, **fields) -> "Judge":
    #     resp = self._client.patch(f"/judges/{judge_id}", json=fields).json()
    #     return Judge(**resp, _http=self._client)
    #
    # # D
    # def delete(self, judge_id: str) -> None:
    #     self._client.delete(f"/judges/{judge_id}")
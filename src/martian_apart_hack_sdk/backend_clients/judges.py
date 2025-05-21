from martian_apart_hack_sdk.resources.judge import Judge


class JudgesClient:
    def __init__(self, httpx, backend):
        self._httpx = httpx
        self._backend = backend

    # C
    def create_rubric_judge(self, rubrics, llm) -> Judge:
        pass

    def list(self) -> list[Judge]:
        resp = self._httpx.get("/judges")
        return [self._init_judge(j) for j in resp.json()["judges"]]

    def get(self, judge_id: str, version=None) -> Judge:
        params = dict(version=version) if version else None
        resp = self._httpx.get(f"/judges/{judge_id}", params=params)
        resp.raise_for_status()
        print(resp.json())
        return self._init_judge(resp.json())

    def _init_judge(self, json_data):
        return Judge(name=json_data["name"],
                     version=json_data["version"],
                     description=json_data["description"],
                     createTime=json_data["createTime"],
                     judgeSpec=json_data.get("judgeSpec"),
                     _backend=self._backend)

    # # U  (full or PATCH-style partial)
    # def update(self, judge_id: str, **fields) -> "Judge":
    #     resp = self._client.patch(f"/judges/{judge_id}", json=fields).json()
    #     return Judge(**resp, _http=self._client)
    #
    # # D
    # def delete(self, judge_id: str) -> None:
    #     self._client.delete(f"/judges/{judge_id}")

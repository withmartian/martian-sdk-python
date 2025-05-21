from typing import Dict, Optional, Any

from martian_apart_hack_sdk.resources.judge import Judge


class JudgesClient:
    def __init__(self, httpx, backend):
        self._httpx = httpx
        self._backend = backend

    def _init_judge(self, json_data):
        return Judge(name=json_data["name"],
                     version=json_data["version"],
                     description=json_data["description"],
                     createTime=json_data["createTime"],
                     judgeSpec=json_data.get("judgeSpec"),
                     _backend=self._backend)

    def create_judge(self, judge_id: str, judge_spec: Dict[str, Any], description: Optional[str] = None) -> Judge:
        # TODO check that judge with judge_id is not exists before creating one (otherwise unclear 500 is returned
        # Another idea is to implement upsert_judge() method and/or get_or_create_judge() method

        payload: Dict[str, Any] = {
            "judgeSpec": {
                "judgeSpec": judge_spec
            }
        }
        if description is not None:
            payload["description"] = description
        print(payload)
        params = {"judgeId": judge_id}
        resp = self._httpx.post("/judges", params=params, json=payload)
        resp.raise_for_status()
        return self._init_judge(json_data=resp.json())

    # TODO Create simple builder to create judge spec
    def create_rubric_judge(self,
                            judge_id: str,
                            rubric: str,
                            model: str,
                            min_score: float,
                            max_score: float,
                            prescript: Optional[str] = None,
                            postscript: Optional[str] = None,
                            extract_variables: Optional[Dict[str, Any]] = None,
                            extract_judgement: Optional[Dict[str, Any]] = None,
                            description: Optional[str] = None
                            ) -> Judge:
        """
        Create a 'rubric_judge' using explicit parameters.
        """
        judge_spec: Dict[str, Any] = {
            "model_type": "rubric_judge",
            "rubric": rubric,
            "model": model,
            "min_score": min_score,
            "max_score": max_score,
        }
        for optional_field in ("prescript", "postscript", "extract_variables", "extract_judgement"):
            if locals()[optional_field] is not None:
                judge_spec[optional_field] = locals()[optional_field]
        return self.create_judge(judge_id, judge_spec, description)

    def list(self) -> list[Judge]:
        resp = self._httpx.get("/judges")
        return [self._init_judge(j) for j in resp.json()["judges"]]

    def get(self, judge_id: str, version=None) -> Judge:
        params = dict(version=version) if version else None
        resp = self._httpx.get(f"/judges/{judge_id}", params=params)
        resp.raise_for_status()
        print(resp.json())
        return self._init_judge(resp.json())

    def evaluate(self, judge_id: str, request, response) -> Judge:
        pass
    # # U  (full or PATCH-style partial)
    # def update(self, judge_id: str, **fields) -> "Judge":
    #     resp = self._client.patch(f"/judges/{judge_id}", json=fields).json()
    #     return Judge(**resp, _http=self._client)
    #
    # # D
    # def delete(self, judge_id: str) -> None:
    #     self._client.delete(f"/judges/{judge_id}")

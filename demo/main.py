import os

from martian_apart_hack_sdk.backend import Backend
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("MARTIAN_API_URL")
API_KEY = os.getenv("MARTIAN_API_KEY")
ORG_ID = os.getenv("MARTIAN_ORG_ID")



def main():
    back = Backend(api_url=API_URL, api_key=API_KEY, org_id=ORG_ID)
    print("Getting Judge by ID and version 1")
    judge_id = "new-quality-rubric-judge"
    judge = back.judges.get(judge_id, version=1)
    print(judge)
    print("Refreshing Judge to get the latest version:")
    refreshed_judge = judge.refresh()
    print(refreshed_judge.to_dict())

    print("Listing judges:")
    all_judges = back.judges.list()
    print("Found %d judges" % len(all_judges))

    print("Creating rubric judge")
    new_judge_id = 'my_cool_judge'
    rubric = "You are helpful assistant to evaluate restaurant recommendation response."
    judge_model = "openai/openai/gpt-4o"
    new_judge = back.judges.create_rubric_judge(new_judge_id,
                                    rubric=rubric,
                                    model=judge_model,
                                    min_score=1,
                                    max_score=5,
                                    description="This is a new judge description.",
                                    )
    # judge = back.judges.get("j1").evaluate()
    # # Create ------------------------------------------------------
    # judge = back.judges.create(
    #     rubrics=[Rubric("accuracy", "facts correct").as_dict()],
    #     llm="gpt-4o-mini",
    # )


if __name__ == "__main__":
    main()

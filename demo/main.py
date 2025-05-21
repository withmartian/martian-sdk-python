from martian_sdk_python.backend import Backend


# # Create ------------------------------------------------------
# judge = back.judges.create(
#     rubrics=[Rubric("accuracy", "facts correct").as_dict()],
#     llm="gpt-4o-mini",
# )

def main():
    back = Backend("https://localhost:8000/", api_key="sk-test-123")
    # judge = back.judges.get("j1").evaluate()



if __name__ == "__main__":
    main()

from build_chain import build_chain


def is_response_valid(response: str) -> tuple[bool, list[str]]:
    errors = []

    if not isinstance(response, str):
        errors.append("Response must be a string.")
        return False, errors

    if not response.strip():
        errors.append("Response must not be empty after trimming spaces.")

    word_count = len(response.split())
    if word_count > 100:
        errors.append(
            f"Response exceeds 100 words ({word_count} words found)."
        )

    return len(errors) == 0, errors


def main():
    chain = build_chain()

    test_cases = [
        {
            "topic": "LangChain Expression Language",
            "analogy_domain": "school assembly line",
        },
        {
            "topic": "Prompt Templates",
            "analogy_domain": "wedding invitation cards",
        },
        {
            "topic": "Output Parsers",
            "analogy_domain": "food delivery packaging",
        },
    ]

    for index, test_input in enumerate(test_cases, start=1):
        print("=" * 60)
        print(f"Test Case {index}")
        print("Input Dictionary:")
        print(test_input)

        try:
            response = chain.invoke(test_input)

            print("\nGenerated Response:")
            print(response)

            is_valid, errors = is_response_valid(response)

            print("\nValidation Result:")
            print(is_valid)

            if errors:
                print("\nValidation Errors:")
                for error in errors:
                    print(f"- {error}")
            else:
                print("\nValidation Errors:")
                print("None")

        except Exception as exc:
            print("\nError while generating response:")
            print(exc)


if __name__ == "__main__":
    main()
import sys

from rag.pipeline import answer_question


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print('Usage: python -m scripts.ask "your question"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = answer_question(question)

    print(result["answer"])
    print()
    print("Sources:", ", ".join(result["sources"]) if result["sources"] else "none")


if __name__ == "__main__":
    main()

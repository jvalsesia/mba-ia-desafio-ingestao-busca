import sys
from search import search_prompt


def main():
    print("Chat iniciado. Digite sua pergunta ou Ctrl+C para sair.\n")
    while True:
        try:
            question = input("PERGUNTA: ")
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o chat. Até logo!")
            sys.exit(0)
        if not question.strip():
            continue
        response = search_prompt(question)
        print(f"RESPOSTA: {response}\n")


if __name__ == "__main__":
    main()

from config import get_config
from search import search_prompt


def main():
    cfg = get_config()
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    pass


if __name__ == "__main__":
    main()
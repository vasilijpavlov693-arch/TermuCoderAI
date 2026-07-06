import os


VERSION_FILE = "VERSION"


def get_version():

    if not os.path.exists(VERSION_FILE):

        return "unknown"


    with open(
        VERSION_FILE,
        "r"
    ) as f:

        return f.read().strip()



def show_version():

    print(
        f"TermuCoderAI {get_version()}"
    )

    print()

    print(
        "✓ llama-server manager"
    )

    print(
        "✓ model manager"
    )

    print(
        "✓ doctor"
    )

    print(
        "✓ setup"
    )

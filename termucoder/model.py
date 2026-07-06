import os
import json


CONFIG_FILE = "settings.json"
MODELS_DIR = os.path.expanduser(
    "~/AI/models"
)



def load_config():

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



def save_config(cfg):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cfg,
            f,
            indent=4,
            ensure_ascii=False
        )



def list_models():

    if not os.path.exists(MODELS_DIR):

        print(
            "Папка моделей не найдена"
        )

        return


    files = os.listdir(
        MODELS_DIR
    )


    models = [
        x for x in files
        if x.endswith(".gguf")
    ]


    if not models:

        print(
            "Модели не найдены"
        )

        return


    print(
        "📦 Доступные модели:"
    )


    for m in models:

        print(
            " -",
            m
        )



def info_model():

    cfg = load_config()

    model = cfg.get(
        "model",
        {}
    )


    print(
        "🤖 Текущая модель:"
    )

    print(
        model.get(
            "name",
            "нет"
        )
    )

    print()

    print(
        model.get(
            "path",
            ""
        )
    )



def use_model(name):

    path = os.path.join(
        MODELS_DIR,
        name
    )


    if not os.path.exists(path):

        print(
            "❌ Модель не найдена:",
            name
        )

        return


    cfg = load_config()


    cfg["model"]["name"] = name

    cfg["model"]["path"] = (
        "~/AI/models/" + name
    )


    save_config(
        cfg
    )


    print(
        "✅ Выбрана модель:",
        name
    )

    print(
        "Перезапусти сервер:"
    )

    print(
        "termucoder server restart"
    )

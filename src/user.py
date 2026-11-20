import os
import json

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATABASE_DIR = os.path.join(
    BASE_DIR, "database", "personas"
)


def register_user(name, user_id):

    os.makedirs(DATABASE_DIR, exist_ok=True)

    file_path = os.path.join(
        DATABASE_DIR, f"{user_id}.json"
    )

    if os.path.exists(file_path):
        raise ValueError("El usuario ya está registrado.")

    user_data = {
        "id": user_id,
        "name": name
    }

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4, ensure_ascii=False)

    return user_data


def get_user(user_id):

    file_path = os.path.join(
        DATABASE_DIR, f"{user_id}.json"
    )

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_all_users():

    os.makedirs(DATABASE_DIR, exist_ok=True)

    users = []

    for filename in os.listdir(DATABASE_DIR):

        if filename.endswith(".json"):

            with open(
                os.path.join(DATABASE_DIR, filename),
                "r",
                encoding="utf-8"
            ) as file:
                users.append(json.load(file))

    return users

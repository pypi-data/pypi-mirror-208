from dotenv import load_dotenv
import os
from pureml.schema import Env
from rich import print


def generate_env_dict(env_path):
    load_dotenv(dotenv_path=env_path)

    org_id = os.getenv(Env.ORG_ID.value)
    access_token = os.getenv(Env.ACCESS_TOKEN.value)
    api_token = os.getenv(Env.API_TOKEN.value)

    env_dict = {}

    if org_id is None:
        print("[red]", Env.ORG_ID.value, "is not set in .env")
    else:
        env_dict[Env.ORG_ID.value] = org_id

    if access_token is None:
        print("[red]", Env.ACCESS_TOKEN.value, "is not set in .env")
    else:
        env_dict[Env.ACCESS_TOKEN.value] = access_token

    if api_token is None:
        print("[red]", Env.API_TOKEN.value, "is not set in .env")
    else:
        env_dict[Env.API_TOKEN.value] = api_token

    return env_dict


def validate_env_docker(env_dict):
    env_dict_set = set(list(env_dict.keys()))
    env_dict_docker = set([Env.ORG_ID.value, Env.API_TOKEN.value])

    if env_dict_docker.issubset(env_dict_set):
        return True

    return False

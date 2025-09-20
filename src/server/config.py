import os
from pathlib import Path

import yaml


cwd = Path(os.getcwd())


def load_config():
    config_path = "server_config"
    if not os.getenv("RUNNING_DOCKER"):
        config_path += "_local"
    config_path = Path(f"{cwd}/resources/server/{config_path}.yaml")
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as config_load_exception:
        raise Exception(f"Error loading configuration file {config_path}: {config_load_exception}")


config: dict = load_config()


class Config:
    class MODELS:
        __default = {
            "core": "qwen2.5:7b",
            "embed": "nomic-embed-text",
            "url": "http://localhost",
            "port": 11434
        }
        CORE: str = config.get("models", __default)["core"]
        EMBED: str = config.get("models", __default)["embed"]
        HOST: str = config.get("models", __default)["url"]
        PORT: int = config.get("models", __default)["port"]
        URL: str = f"http://{HOST}:{PORT}"

    class CSV:
        __default = {
            "directory": "csvs"
        }
        DIRECTORY: Path = cwd / config.get("csv", __default)["directory"]

        class MAX:
            __default = {
                "max": {
                    "files": 5,
                    "size": 10000
                }
            }
            FILES: int = config.get("csv", __default)["max"]["files"]
            SIZE: int = config.get("csv", __default)["max"]["size"]

    class CLEANUP:
        __default = {
            "interval_seconds": 900
        }
        INTERVAL_SECONDS: int = config.get("cleanup", __default)["interval_seconds"]

    class REDIS:
        __default = {
            "host": "localhost",
            "port": 6379,
            "db": 0
        }
        URL: str = config.get("redis", __default)["host"]
        PORT: int = config.get("redis", __default)["port"]
        DB: int = config.get("redis", __default)["db"]
        EXPIRE_SECONDS: int = config.get("redis", __default)["expire_seconds"]

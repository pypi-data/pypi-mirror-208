import os


def is_containerized(
    env_name: str = "CONTAINERIZED", env_value: str = "0", env_default_value="1"
) -> bool:
    value2 = os.environ.get(env_name, env_default_value)
    return env_value is value2

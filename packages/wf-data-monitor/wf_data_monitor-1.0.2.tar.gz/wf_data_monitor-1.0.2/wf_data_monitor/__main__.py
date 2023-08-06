import os
import sys

from dotenv import load_dotenv


def load_env_vars():
    env_file = os.path.join(os.getcwd(), ".env")

    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)


def main():
    load_env_vars()

    from .scheduler import Scheduler

    Scheduler().start()


if __name__ == "__main__":
    sys.exit(main())

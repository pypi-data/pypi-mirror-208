import os
from dotenv import load_dotenv
from pathlib import Path

XAPI_KEY_NAME = 'XAPI_API_TOKEN'


def initialize(api_key: str, save=False) -> None:
    """Saves the Nitrado API key in a local .env file"""
    os.environ[XAPI_KEY_NAME] = api_key
    if not save:
        return
    if not Path('.env').exists():
        Path('.env').touch()
    with open('.env', 'r+') as r:
        content = []
        found = False
        for line in r.readlines():
            if line.find(f'{XAPI_KEY_NAME}=') == 0:
                content += [f"{XAPI_KEY_NAME}={api_key}\n"]
                found = True
            else:
                content += [line]
        if not found:
            content = [f"{XAPI_KEY_NAME}={api_key}\n"] + content
        r.seek(0)
        r.write(''.join(content))
        load_dotenv()

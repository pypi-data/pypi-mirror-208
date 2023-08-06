import os
from bardapi import Bard  # type: ignore


def set_key(key: str):
    '''
    - set your `__Secure-1PSID` value to key
    - detail info: https://github.com/dsdanielpark/Bard-API
    - amazing prompt: https://github.com/dsdanielpark/amazing-bard-prompts
    '''
    os.environ['_BARD_API_KEY'] = key


def get_response(
    prompt: str) -> dict[{'content': str, 'choices': list[dict[{'id': str, 'content': list[str]}]]}]: return Bard().get_answer(prompt)


def get_content(prompt: str) -> str: return get_response(prompt)['content']

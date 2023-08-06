import requests
import json
from material_zui.regex import value

url = "https://chatgpt.chatgptvietnam.org/api/chat-process"
headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://chatgpt.chatgptvietnam.org',
    'referer': 'https://chatgpt.chatgptvietnam.org/',
}


def gpt_call(prompt: str) -> str:
    payload = json.dumps({
        "prompt": prompt,
        "systemMessage": "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown.",
        "temperature": 0.8,
        "top_p": 1
    })
    response = requests.post(url, headers=headers, data=payload)
    return response.text


def gpt_last_result(prompt: str) -> dict[{'text': str}] | None:
    data = gpt_call(prompt)
    last_value = value(data, '.+"finish_reason":"stop".+')
    return json.loads(last_value) if last_value else None


def gpt_last_text_result(prompt: str) -> str:
    data = gpt_last_result(prompt)
    return data['text'] if data else ''

import re

# The string we want to search
# text = '''{"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"role":"assistant"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello","delta":"Hello","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"Hello"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again","delta":" again","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":" again"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again!","delta":"!","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"!"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How","delta":" How","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":" How"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How can","delta":" can","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":" can"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How can I","delta":" I","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":" I"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How can I help","delta":" help","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":" help"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How can I help you","delta":" you","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":" you"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How can I help you today","delta":" today","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":" today"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How can I help you today?","delta":"?","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"?"},"index":0,"finish_reason":null}]}}
# {"role":"assistant","id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","parentMessageId":"00b954a2-da94-4c07-9641-4ff6b702d6f5","text":"Hello again! How can I help you today?","detail":{"id":"chatcmpl-7BcGlt1VxezpfB3C8lJDZUmTq0nNp","object":"chat.completion.chunk","created":1683003071,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}}
# '''

# # The regular expression we want to use
# regex = '.+"finish_reason":"stop".+'

# # Create a regular expression object
# pattern = re.compile(regex)

# # Search the string for the regular expression
# match = pattern.search(text)

# # Check if the match was found
# if match:
#     # The match was found, so print the matched text
#     json_data = json.loads(match.group())
#     print(json_data['text'])
# else:
#     # The match was not found, so print a message
#     print("No match found")


def check(value: str, regex: str):
    pattern = re.compile(regex)
    return pattern.search(value)


def value(value: str, regex: str) -> str:
    match = check(value, regex)
    return match.group() if match else ''

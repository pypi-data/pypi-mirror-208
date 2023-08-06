# humanloop@0.4.0a4


## Requirements

Python >=3.7

## Installing

```sh
pip install humanloop==0.4.0a4
```

## Getting Started

```python
from pprint import pprint
from humanloop import Humanloop, ApiException

humanloop = Humanloop(
    # Defining the host is optional and defaults to https://api.humanloop.com/v4
    # See configuration.py for a list of all supported configuration parameters.
    host="https://api.humanloop.com/v4",
    api_key="YOUR_API_KEY",
)

try:
    # Chat
    chat_response = humanloop.chat(
        project="sdk-example",
        messages=[
            {
                "role": "user",
                "content": "Explain asynchronous programming.",
            }
        ],
        model_config={
            "model": "gpt-3.5-turbo",
            "max_tokens": -1,
            "temperature": 0.7,
            "chat_template": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant who replies in the style of {{persona}}.",
                },
            ],
        },
        inputs={
            "persona": "the pirate Blackbeard",
        },
        stream=False,
    )
    pprint(chat_response.body)
    pprint(chat_response.body["project_id"])
    pprint(chat_response.body["data"][0])
    pprint(chat_response.body["provider_responses"])
    pprint(chat_response.headers)
    pprint(chat_response.status)
    pprint(chat_response.round_trip_time)
except ApiException as e:
    print("Exception when calling .response: %s\n" % e)
    pprint(e.body)
    if e.status == 422:
        pprint(e.body["detail"])
    pprint(e.headers)
    pprint(e.status)
    pprint(e.reason)
    pprint(e.round_trip_time)

try:
    # Complete
    complete_response = humanloop.complete(
        project="sdk-example",
        inputs={
            "text": "Llamas that are well-socialized and trained to halter and lead after weaning and are very friendly and pleasant to be around. They are extremely curious and most will approach people easily. However, llamas that are bottle-fed or over-socialized and over-handled as youth will become extremely difficult to handle when mature, when they will begin to treat humans as they treat each other, which is characterized by bouts of spitting, kicking and neck wrestling.[33]",
        },
        model_config={
            "model": "gpt-3.5-turbo",
            "max_tokens": -1,
            "temperature": 0.7,
            "prompt_template": "Summarize this for a second-grade student:\n\nText:\n{{text}}\n\nSummary:\n",
        },
        stream=False,
    )
    pprint(complete_response.body)
    pprint(complete_response.body["project_id"])
    pprint(complete_response.body["data"][0])
    pprint(complete_response.body["provider_responses"])
    pprint(complete_response.headers)
    pprint(complete_response.status)
    pprint(complete_response.round_trip_time)
except ApiException as e:
    print("Exception when calling .create: %s\n" % e)
    pprint(e.body)
    if e.status == 422:
        pprint(e.body["detail"])
    pprint(e.headers)
    pprint(e.status)
    pprint(e.reason)
    pprint(e.round_trip_time)

try:
    # Feedback
    feedback_response = humanloop.feedback(
        type="rating",
        value="good",
        data_id="data_[...]",
        user="user@example.com",
    )
    pprint(feedback_response.body)
    pprint(feedback_response.headers)
    pprint(feedback_response.status)
    pprint(feedback_response.round_trip_time)
except ApiException as e:
    print("Exception when calling .submit: %s\n" % e)
    pprint(e.body)
    if e.status == 422:
        pprint(e.body["detail"])
    pprint(e.headers)
    pprint(e.status)
    pprint(e.reason)
    pprint(e.round_trip_time)

try:
    # Log
    log_response = humanloop.log(
        project="sdk-example",
        inputs={
            "text": "Llamas that are well-socialized and trained to halter and lead after weaning and are very friendly and pleasant to be around. They are extremely curious and most will approach people easily. However, llamas that are bottle-fed or over-socialized and over-handled as youth will become extremely difficult to handle when mature, when they will begin to treat humans as they treat each other, which is characterized by bouts of spitting, kicking and neck wrestling.[33]",
        },
        output="Llamas can be friendly and curious if they are trained to be around people, but if they are treated too much like pets when they are young, they can become difficult to handle when they grow up. This means they might spit, kick, and wrestle with their necks.",
        source="sdk",
        model_config={
            "model": "gpt-3.5-turbo",
            "max_tokens": -1,
            "temperature": 0.7,
            "prompt_template": "Summarize this for a second-grade student:\n\nText:\n{{text}}\n\nSummary:\n",
        },
    )
    pprint(log_response.body)
    pprint(log_response.headers)
    pprint(log_response.status)
    pprint(log_response.round_trip_time)
except ApiException as e:
    print("Exception when calling .log: %s\n" % e)
    pprint(e.body)
    if e.status == 422:
        pprint(e.body["detail"])
    pprint(e.headers)
    pprint(e.status)
    pprint(e.reason)
    pprint(e.round_trip_time)
```

## Async

`async` support is available by prepending `a` to any method.

```python
from pprint import pprint
from humanloop import Humanloop, ApiException

humanloop = Humanloop(
    # Defining the host is optional and defaults to https://api.humanloop.com/v4
    # See configuration.py for a list of all supported configuration parameters.
    host="https://api.humanloop.com/v4",
    # Configure API key authorization: APIKeyHeader
    api_key="YOUR_API_KEY",
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    # api_key_prefix = {'APIKeyHeader': 'Bearer'},
)


async def main():
    try:
        # Get App
        get_response = await humanloop.apps.aget(
            id="id_example",  # required
        )
        pprint(get_response.headers)
        pprint(get_response.status)
        pprint(get_response.round_trip_time)
    except ApiException as e:
        print("Exception when calling AppsApi.get: %s\n" % e)
        pprint(e.body)
        if e.status == 422:
            pprint(e.body["detail"])
        pprint(e.headers)
        pprint(e.status)
        pprint(e.reason)
        pprint(e.round_trip_time)


asyncio.run(main())
```


## Streaming

Streaming support is available by suffixing a `chat` or `complete` method with `_stream`.

```python
import asyncio
from humanloop import Humanloop

humanloop = Humanloop(
    api_key="YOUR_API_KEY",
)


async def main():
    response = await humanloop.chat_stream(
        project="sdk-example",
        messages=[
            {
                "role": "user",
                "content": "Explain asynchronous programming.",
            }
        ],
        model_config={
            "model": "gpt-3.5-turbo",
            "max_tokens": -1,
            "temperature": 0.7,
            "chat_template": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant who replies in the style of {{persona}}.",
                },
            ],
        },
        inputs={
            "persona": "the pirate Blackbeard",
        },
    )
    async for token in response.content:
        print(token)


asyncio.run(main())
```



## Author
This Python package is automatically generated by [Konfig](https://konfigthis.com)

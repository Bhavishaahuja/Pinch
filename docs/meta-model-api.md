# Meta Model API — reference notes

Collected from Meta's official docs on 2026-10-26. `https://ai.developer.meta.com/docs/` redirects (302) to `https://dev.meta.ai/docs/`, so every source link below is on `dev.meta.ai`.

Code samples are copied from the docs. The docs use `muse-spark-1.3` in their examples. To use Muse Wonder, change `model` to `muse-wonder-1.0`, which the Models page lists as supporting Chat Completions, image input, and structured output.

---

## Base URL, auth header, env var

Source: https://dev.meta.ai/docs/quickstart · https://dev.meta.ai/docs/authentication

| | |
|---|---|
| Base URL | `https://api.meta.ai/v1` |
| Auth header | `Authorization: Bearer $MODEL_API_KEY` |
| Env var | `MODEL_API_KEY` |
| Key format | Starts with `LLM_`, then a numeric ID and the secret, separated by underscores |

- To get a key: Model API dashboard → **API keys** → **Create API key**. The key is shown only once.
- To rotate a key: create a new one, move your apps to it, then delete the old one.
- **The OpenAI SDK (and the Anthropic SDK, LangChain, LiteLLM) does not read `MODEL_API_KEY` automatically.** Pass it explicitly:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.meta.ai/v1",
    api_key=os.environ["MODEL_API_KEY"],
)
```

---

## Muse Wonder model id

Source: https://dev.meta.ai/docs/models

| Field | Value |
|---|---|
| Model id | `muse-wonder-1.0` |
| Status | **Preview** ("Muse Wonder is in preview.") |
| Context window | 1,048,576 tokens |
| Input / output | Text, image, video, audio, PDF in → text out |
| Endpoints | Responses, Chat Completions, Messages |
| Features | Structured output, tool calling, reasoning (effort `minimal` to `max`), search grounding, computer use |
| Availability | Model API pay-as-you-go, Standard mode only. Not available in South Korea. |

"Muse Wonder Full" is **not** available on Model API. Setting reasoning effort to `max` does not select it.

---

## Chat Completions: request and response

Source: https://dev.meta.ai/docs/protocols/chat-completions

**Endpoint:** `POST https://api.meta.ai/v1/chat/completions`

### Request

```shell
curl -X POST "https://api.meta.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "muse-spark-1.3",
  "messages": [
    {
      "role": "user",
      "content": "What are three differences between TCP and UDP?"
    }
  ]
}'
```

```python
response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "user",
            "content": "What are three differences between TCP and UDP?",
        },
    ],
)
print(response.model_dump_json(indent=2))
```

Roles: `user`, `assistant`, `developer`, `system`, `tool`. `system` is merged with `developer` at the same precedence.

### Parameters

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `model` | string | required | |
| `messages` | array | required | |
| `temperature` | number | 1.0 | 0–2. Use this or `top_p`, not both. |
| `top_p` | number | 1.0 | 0 < top_p ≤ 1 |
| `frequency_penalty` / `presence_penalty` | number | 0 | -2 to 2 |
| `max_completion_tokens` | integer | model-dependent | `max_tokens` is still accepted as a deprecated alias |
| `stream` | boolean | false | SSE |
| `reasoning_effort` | string | model-set | `minimal`, `low`, `medium`, `high`, `xhigh`. `none` returns HTTP 400. |
| `seed` | integer | null | best-effort |
| `n` | integer | 1 | Only 1 is supported |
| `response_format` | object | | Structured output (see below) |
| `tools`, `tool_choice` | | | Tool calling |
| `prompt_cache_key`, `prompt_cache_retention` (`in_memory` / `24h`) | string | null | Prompt caching |
| `safety_identifier` | string | null | ≤64 chars. Replaces the deprecated `user`. |

**Rejected with HTTP 400 (differences from OpenAI):** `stop`, `n > 1`, `verbosity`, `logit_bias`, `prediction`, `web_search_options`, `modalities`, `audio`, `logprobs: true`, `reasoning_effort: "none"`, `max_output_tokens`, `text.format`. Tool-call replays must pair each assistant `tool_calls` message with its `tool` results.

### Response

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1714502400,
  "model": "muse-spark-1.3",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here are three key differences between TCP and UDP..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 19,
    "total_tokens": 44
  }
}
```

The text is at `response.choices[0].message.content`.

### Streaming

Set `"stream": true` and send `Accept: text/event-stream`. Each SSE line starts with `data: `, each chunk carries `choices[0].delta.content`, and the stream ends with `data: [DONE]`. Streaming requests are exempt from the non-streaming server time limit, which otherwise returns HTTP 504.

---

## Sending an image (Chat Completions)

Source: https://dev.meta.ai/docs/image-understanding

Put a `content` array on a **`user`** message (only user messages are processed for images). Combine a `"text"` part with one or more `"image_url"` parts. `image_url.url` takes a public `http(s)` URL or a base64 data URL.

### Public URL

```python
response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe what you see in this image.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Avocado_Hass_-_single_and_halved.jpg/1280px-Avocado_Hass_-_single_and_halved.jpg",
                    },
                },
            ],
        },
    ],
)
```

### Local file as base64

```python
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

base64_image = image_to_base64("photo.jpg")

response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What does this image contain?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ],
        }
    ],
)
print(response.choices[0].message.content)
```

The response has the same shape as a text-only chat completion.

### Limits

| Constraint | Value |
|---|---|
| Formats | `image/jpeg`, `image/jpg`, `image/png`, `image/gif`, `image/webp`, `image/x-icon` |
| Max size, inline `image_url` | 50 MB (50,000,000 bytes) |
| Max size, Files API `input_file` (Responses API only) | 1 GiB |
| Max images per request | 50 (more returns HTTP 400) |
| PDFs | First 50 page-images kept |
| Undecodable image | HTTP 400 `invalid_request_error` |

The page documents no `detail` parameter. For object locations, the page asks the model for coordinates on a normalized **0–1000** grid with (0,0) at the top-left. Convert to pixels with `x = round(x_norm * width / 1000)`.

---

## Structured JSON output (Chat Completions)

Source: https://dev.meta.ai/docs/structured-output

Set `response_format` to `type: "json_schema"` and put a `name` and a `schema` inside `json_schema`. The page doesn't mention `json_object` mode.

### Request

```python
response = client.chat.completions.create(
    model="muse-spark-1.3",
    messages=[
        {
            "role": "system",
            "content": "Extract the address from the user input into the specified JSON format.",
        },
        {
            "role": "user",
            "content": "Please format this address: 1 Hacker Wy Menlo Park CA 94025",
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "Address",
            "schema": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string", "description": "2-letter state abbreviation"},
                    "zip": {"type": "string", "description": "5-digit zip code"},
                },
                "required": ["street", "city", "state", "zip"],
            },
        },
    },
)
```

### Response

The JSON comes back as a **string** in `choices[0].message.content`. Parse it with `json.loads()`:

```json
{
  "street": "1 Hacker Way",
  "city": "Menlo Park",
  "state": "CA",
  "zip": "94025"
}
```

### Pydantic shortcut (OpenAI SDK)

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str

response = client.beta.chat.completions.parse(
    model="muse-spark-1.3",
    messages=[
        {"role": "system", "content": "Extract the address from the user input."},
        {"role": "user", "content": "Please format this address: 1 Hacker Wy Menlo Park CA 94025"},
    ],
    response_format=Address,
)
address = response.choices[0].message.parsed
```

### `strict` and schema limits

- `response_format.json_schema.strict` defaults to `false`. Output is **always** constrained to the schema either way. `strict: true` only makes the server also validate the schema against the strict subset.
- Strict subset: the root must be a plain object (no top-level `anyOf`/`oneOf`/`allOf`/`enum`/`not`), `allOf` and `oneOf` are not allowed anywhere, every object needs `additionalProperties: false`, and `required` must list every property.
- Limits: 10 nesting levels; 5,000 total properties; 120,000 combined characters across names, definitions, enum values, and `const` values; 1,000 enum values (a string enum with more than 250 values is also capped at 15,000 characters); 200,000 nodes after `$ref` inlining.
- Recursive (`$ref`-cycle) schemas are rejected with HTTP 400.

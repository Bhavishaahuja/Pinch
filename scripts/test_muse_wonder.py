# quick smoke tests for Muse Wonder
# run from the repo root:
#   python scripts/test_muse_wonder.py                  -> text prompt test
#   python scripts/test_muse_wonder.py path/to/img.jpg  -> image test
# everything here comes from docs/meta-model-api.md

import base64
import os
import sys

import httpx
from dotenv import load_dotenv

# endpoint and model id straight from the docs
CHAT_URL = "https://api.meta.ai/v1/chat/completions"
MODEL_ID = "muse-wonder-1.0"
TEXT_PROMPT = "Say hi and tell me what model you are"
IMAGE_PROMPT = "Describe what's in this image in one sentence."

# image formats the docs list as supported, keyed by file extension
IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
}
# docs cap inline images at 50 MB
MAX_IMAGE_BYTES = 50_000_000


def get_api_key():
    load_dotenv()
    api_key = os.getenv("MODEL_API_KEY")
    if not api_key:
        print("ERROR: MODEL_API_KEY isn't set. Copy .env.example to .env and add your key.")
        sys.exit(1)
    return api_key


def send_chat(api_key, messages):
    # sends the messages to Muse Wonder and prints everything useful that comes back
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL_ID,
        "messages": messages,
    }

    print(f"Calling {CHAT_URL} with model {MODEL_ID}...")

    try:
        # Muse Wonder reasons before answering, so give it a generous timeout
        response = httpx.post(CHAT_URL, headers=headers, json=body, timeout=120)
    except httpx.TimeoutException:
        print("ERROR: request timed out after 120s. No response from the API.")
        sys.exit(1)
    except httpx.RequestError as err:
        # DNS, connection refused, SSL problems, that kind of thing
        print(f"ERROR: couldn't reach the API: {err}")
        sys.exit(1)

    print(f"Status code: {response.status_code}")

    if response.status_code != 200:
        # docs don't spell out the error body shape, so just dump whatever came back
        if response.status_code == 401 or response.status_code == 403:
            print("ERROR: auth failed. Double check MODEL_API_KEY in .env.")
        elif response.status_code == 404:
            print("ERROR: got a 404. Endpoint or model id might be wrong.")
        else:
            print("ERROR: the API returned an error.")
        print("Response body:")
        print(response.text)
        sys.exit(1)

    try:
        data = response.json()
    except ValueError:
        print("ERROR: got a 200 but the body isn't JSON:")
        print(response.text)
        sys.exit(1)

    # response text lives at choices[0].message.content
    choices = data.get("choices") or []
    if len(choices) == 0:
        print("ERROR: no choices in the response. Full body:")
        print(response.text)
        sys.exit(1)

    message = choices[0].get("message", {})
    print("\nResponse text:")
    print(message.get("content"))
    print(f"\nFinish reason: {choices[0].get('finish_reason')}")
    print(f"Model (as reported by the API): {data.get('model')}")

    # print every usage field the API sends, not just the three in the docs example
    usage = data.get("usage")
    if usage:
        print("\nUsage:")
        for key, value in usage.items():
            print(f"  {key}: {value}")
    else:
        print("\nNo usage info in the response.")


def test_text(api_key):
    messages = [
        {"role": "user", "content": TEXT_PROMPT},
    ]
    send_chat(api_key, messages)


def test_image(api_key, image_path):
    if not os.path.isfile(image_path):
        print(f"ERROR: can't find an image at {image_path}")
        sys.exit(1)

    extension = os.path.splitext(image_path)[1].lower()
    if extension not in IMAGE_TYPES:
        print(f"ERROR: {extension or 'no extension'} isn't a supported image type.")
        print("Supported: " + ", ".join(IMAGE_TYPES.keys()))
        sys.exit(1)
    mime_type = IMAGE_TYPES[extension]

    file_size = os.path.getsize(image_path)
    if file_size > MAX_IMAGE_BYTES:
        print(f"ERROR: image is {file_size} bytes, the inline limit is {MAX_IMAGE_BYTES}.")
        sys.exit(1)

    # read the file and turn it into a base64 data URL like the docs show
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    data_url = f"data:{mime_type};base64,{base64_image}"

    print(f"Sending {image_path} ({mime_type}, {file_size} bytes)")

    # images only get processed on user messages
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": IMAGE_PROMPT},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        },
    ]
    send_chat(api_key, messages)


if __name__ == "__main__":
    api_key = get_api_key()
    if len(sys.argv) > 1:
        test_image(api_key, sys.argv[1])
    else:
        test_text(api_key)

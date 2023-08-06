#!/usr/bin/env python
import argparse
import os
import queue
import threading

import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def openai_chat_thread(prompt=None):
    def process_gpt(prompt: str, q: queue.Queue):
        dic = {}
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.5,
            stream=True,
            max_tokens=2048
        )
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            if "finish_reason" in chunk["choices"][0] and chunk["choices"][0]["finish_reason"] == "stop":
                break
            if "content" in delta:
                q.put(delta["content"])
        q.put(None)

    q = queue.Queue()
    new_thread = threading.Thread(target=process_gpt, args=(prompt, q))
    new_thread.start()
    return q


def main():
    parser = argparse.ArgumentParser(description="Chat with GPT.")
    parser.add_argument("prompt", type=str, help="The prompt for GPT to respond to")
    args = parser.parse_args()

    q = openai_chat_thread(args.prompt)

    while True:
        response = q.get()
        if response is None:
            break
        print(response, end="", flush=True)


if __name__ == "__main__":
    main()

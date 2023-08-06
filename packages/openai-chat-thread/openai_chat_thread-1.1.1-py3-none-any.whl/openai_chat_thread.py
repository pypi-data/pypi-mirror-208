#!/usr/bin/env python
import argparse
import os
import queue
import threading

import openai
from dotenv import load_dotenv
from opencc import OpenCC

cc = OpenCC('s2t')

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def openai_chat_thread(prompt=None, model="gpt-4", convert_to_taiwan=False):
    def process_gpt(prompt: str, q: queue.Queue, model: str, convert_to_traditional: bool):
        response = openai.ChatCompletion.create(
            model=model,
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
                content = delta["content"]
                if convert_to_traditional:
                    content = cc.convert(content)
                q.put(content)
        q.put(None)

    q = queue.Queue()
    new_thread = threading.Thread(target=process_gpt, args=(prompt, q, model, convert_to_taiwan))
    new_thread.start()
    return q


def openai_chat_thread_taiwan(prompt=None, model="gpt-4"):
    return openai_chat_thread(prompt, model=model, convert_to_taiwan=True)


def main():
    parser = argparse.ArgumentParser(description="Chat with GPT.")
    parser.add_argument("prompt", type=str, help="The prompt for GPT to respond to")
    parser.add_argument("--model", type=str, default="gpt-4", help="The model to use (gpt-4 or gpt-3.5-turbo)")
    args = parser.parse_args()

    q = openai_chat_thread_taiwan(args.prompt, model=args.model)

    while True:
        response = q.get()
        if response is None:
            break
        print(response, end="", flush=True)


if __name__ == "__main__":
    main()

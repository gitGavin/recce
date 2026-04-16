"""Recce CLI. Week 1: hello-world. Week 2: real agent flow."""
import os
import sys
from anthropic import Anthropic

def main():
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    product = sys.argv[1] if len(sys.argv) > 1 else "Linear Agents"

    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"In one sentence, what is {product}?"
        }],
    )
    print(resp.content[0].text)

if __name__ == "__main__":
    main()

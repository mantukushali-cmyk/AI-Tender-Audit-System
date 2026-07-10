# modules/ollama_client.py
import time
from ollama import Client

# Configured client pointing to local Ollama instance with high timeout for large PDFs
client = Client(
    host="http://127.0.0.1:11434",
    timeout=300
)

def ask_gemma(prompt_content: str) -> str:
    print("=" * 80)
    print("🤖 Sending prompt to Gemma")
    print(f"Prompt length : {len(prompt_content):,} characters")
    print(f"Estimated tokens : {len(prompt_content)//4:,}")
    print("=" * 80)

    start = time.time()

    response = client.chat(
        model="gemma3:4b",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt_content
            }
        ]
    )

    print(f"Finished in {time.time()-start:.2f} sec")
    return response["message"]["content"]
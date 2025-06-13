import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")

def estimate_tokens(text: str) -> int:
    return len(encoding.encode(text))

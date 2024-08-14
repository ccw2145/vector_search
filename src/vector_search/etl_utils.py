import tiktoken
import pandas as pd
from typing import List

def chunk_text(text: str, max_chunk_tokens: int, encoding: tiktoken.Encoding) -> List[str]:
    """Split text to smaller chunks"""
    # Encode and then decode within the function
    tokens = encoding.encode(text)
    chunks = []
    while tokens:
        chunk_tokens = tokens[:max_chunk_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        tokens = tokens[max_chunk_tokens:]
    return chunks
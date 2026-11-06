import os
from transformers import AutoTokenizer


class TokenCounter:
    """
    Counts tokens using the actual Hugging Face tokenizer.

    The tokenizer is loaded once and reused.
    """

    DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

    def __init__(self, model_name=None):

        self.model_name = (
            model_name
            or os.getenv("TOKENIZER_MODEL", self.DEFAULT_MODEL)
        )

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=True
            )

        except Exception as error:
            raise RuntimeError(
                f"Could not load tokenizer: {error}"
            ) from error

    def encode(self, text):
        """
        Convert text into token IDs.
        Special tokens are excluded because we count
        the actual text separately from model formatting.
        """

        return self.tokenizer.encode(
            text,
            add_special_tokens=False
        )

    def count(self, text):
        """
        Return the number of tokens in a text string.
        """

        return len(self.encode(text))

    def decode(self, token_ids):
        """
        Convert token IDs back into readable text.
        """

        return self.tokenizer.decode(
            token_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )

    def split_text(self, text, max_tokens):
        """
        Split an exceptionally long text into pieces
        containing no more than max_tokens tokenizer IDs.
        """

        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")

        token_ids = self.encode(text)

        if not token_ids:
            return [text]

        pieces = []

        for start in range(0, len(token_ids), max_tokens):

            token_part = token_ids[start:start + max_tokens]

            pieces.append(self.decode(token_part))

        return pieces
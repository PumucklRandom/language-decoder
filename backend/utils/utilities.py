import re
from typing import Iterator
from backend.config.config import CONFIG


def maxlen(a_list: list) -> int:
    # Get the length of the longest element in a sequence.
    if not a_list:
        return 0
    return max(len(item) for item in a_list)


def yield_batch(string_list: list[str], char_limit: int, offset: int = 1) -> Iterator[list[str]]:
    """
    Yield batches of strings that fit within a character limit.

    Args:
        string_list: List of strings to batch
        char_limit: Maximum characters per batch
        offset: Additional character count per string (e.g., for separators)

    Yields:
        Lists of strings that fit within the character limit
    """

    batch, batch_len = [], 0
    string_data = ((string, len(string) + offset) for string in string_list)
    for string, str_len in string_data:
        batch_len += str_len
        # Check if adding the current string exceeds the character limit
        if batch_len <= char_limit:
            batch.append(string)
        else:
            yield batch
            batch = [string]
            batch_len = str_len
    # Yield the last batch if it is not empty
    if batch:
        yield batch


def yield_batch_eos(string_list: list[str], char_limit: int, offset: int = 1,
                    endofs: str = CONFIG.Regex.endofs, quotes = CONFIG.Regex.quotes) -> Iterator[list[str]]:
    last_valid_index = 0
    batch, batch_len = [], 0
    pattern = re.compile(rf'.*?[{endofs}][{quotes}]?$')
    string_data = ((string, len(string) + offset, bool(pattern.match(string))) for string in string_list)
    for string, str_len, eos in string_data:
        batch_len += str_len
        # Check if adding the current string exceeds the character limit
        if batch_len <= char_limit:
            batch.append(string)
        # If limit exceeded, yield the current batch and start a new one
        else:
            # If a valid end of sentence index exists
            if last_valid_index > 0:
                yield batch[:last_valid_index]
                batch = batch[last_valid_index:] + [string]
                batch_len = sum(len(word) + offset for word in batch)
            else:
                yield batch
                batch = [string]
                batch_len = str_len
            last_valid_index = 0
        # Get last valid end of sentence index
        if eos:
            last_valid_index = len(batch)
    # Yield the last batch if it is not empty
    if batch:
        yield batch

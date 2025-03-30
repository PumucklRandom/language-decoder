def lonlen(a_list: list) -> int:
    # get the length of the longest list element
    if a_list:
        return len(max(a_list, key = len))
    return 0


def yield_batch(string_list: list, char_limit: int, offset: int = 1):
    batch, batch_len = [], 0
    for string in string_list:
        # Check if adding the current word exceeds the character limit
        if batch_len + len(string) + len(batch) * offset <= char_limit:
            batch.append(string)
            batch_len += len(string)
        else:
            # If limit exceeded, yield the current batch and start a new one
            yield batch
            batch = [string]
            batch_len = len(string)
    # Yield the last batch if it's not empty
    if batch:
        yield batch

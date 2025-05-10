def lonlen(a_list: list) -> int:
    # get the length of the longest list element
    if a_list:
        return len(max(a_list, key = len))
    return 0


def yield_batch(string_list: list, char_limit: int, offset: int = 1) -> list:
    batch, batch_len = [], 0
    for string in string_list:
        batch_len += len(string) + offset
        # Check if adding the current string exceeds the character limit
        if batch_len <= char_limit:
            batch.append(string)
        # If limit exceeded, yield the current batch and start a new one
        else:
            yield batch
            batch = [string]
            batch_len = len(string) + offset
    # Yield the last batch if it is not empty
    if batch:
        yield batch


def yield_batch_eos(string_list: list, char_limit: int, offset: int = 1, endofs: str = '.!?\'"') -> list:
    batch, batch_len = [], 0
    last_valid_index = 0
    for string in string_list:
        batch_len += len(string) + offset
        # Check if adding the current string exceeds the character limit
        if batch_len <= char_limit:
            batch.append(string)
            # get last valid end of sentence index
            if string[-1] in endofs:
                last_valid_index = len(batch)
        # If limit exceeded, yield the current batch and start a new one
        else:
            # If a valid end of sentence index exists
            if last_valid_index > 0:
                yield batch[:last_valid_index]
                batch = batch[last_valid_index:] + [string]
            else:
                yield batch
                batch = [string]
            last_valid_index = 0
            batch_len = sum(len(word) + offset for word in batch)
    # Yield the last batch if it is not empty
    if batch:
        yield batch

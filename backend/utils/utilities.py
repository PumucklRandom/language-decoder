def lonlen(a_list: list) -> int:
    # get the length of the longest list element
    return len(max(a_list, key = len))

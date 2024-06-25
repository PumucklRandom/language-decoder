def lonlen(a_list: list) -> int:
    # get the length of the longest list element
    if a_list:
        return len(max(a_list, key = len))
    return 0

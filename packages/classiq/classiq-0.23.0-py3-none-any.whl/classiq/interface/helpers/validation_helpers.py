from typing import Hashable, List


def is_list_unique(lst: List[Hashable]) -> bool:
    return len(set(lst)) == len(lst)

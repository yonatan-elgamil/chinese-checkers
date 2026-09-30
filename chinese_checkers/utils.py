"""Coordinate, path, and input helpers used by the board and game."""

import itertools
from typing import Any, Dict, List, Tuple


def is_valid_coordinate_input(s: str) -> bool:
    """Check 1-based row,column input without allowing zero or negatives."""
    parts = s.split(',')
    return len(parts) == 2 and all(part.isdecimal() and int(part) > 0 for part in parts)


def group_coordinates_by_row(tapele_list: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    """Gets a list of positions and returns a list of lists ordered by the first row and the last
     at the position of the first number in the tuple indicating a row and the second a column"""
    grouped_list = {}
    for tapele in tapele_list:
        key = tapele[0]
        if key in grouped_list:
            grouped_list[key].append(tapele)
        else:
            grouped_list[key] = [tapele]
    return sorted(list(grouped_list.values()), key=lambda x: min(t[0] for t in x))


def group_coordinates_by_row_descending(tapele_list: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    """Gets a list of positions and returns a list of lists ordered by the last row and at the end of the
     first in the position the first number in the tuple indicates a row and the second a column"""
    grouped_list = {}
    for tapele in tapele_list:
        key = tapele[0]
        if key in grouped_list:
            grouped_list[key].append(tapele)
        else:
            grouped_list[key] = [tapele]
    return sorted(list(grouped_list.values()), key=lambda x: min(t[0] for t in x), reverse=True)


def opposite_direction(direction: str) -> List[str]:
    """Gets a position and returns its inverse in a list"""
    if direction == 'N':
        return ['S']
    if direction == 'S':
        return ['N']
    if direction == 'NE':
        return ['SW']
    if direction == 'SW':
        return ['NE']
    if direction == 'NW':
        return ['SE']
    if direction == 'SE':
        return ['NW']


def get_all_subsets(input_dict):
    all_subsets = []
    for r in range(len(input_dict) + 1):
        subsets = itertools.combinations(input_dict.items(), r)
        all_subsets.extend(subsets)
    all_subsets_dicts = [dict(subset) for subset in all_subsets]
    return all_subsets_dicts


def rearrange_list(dicts: List[Dict[str, Any]], name) -> List[Dict[str, Any]]:
    """Gets a dictionary of players and rearranges them. The new name is first and everything else after it"""
    idx = None
    for i, d in enumerate(dicts):
        if d['name'] == name:
            idx = i
            break

    if idx is None:
        return dicts

    rearranged_list = dicts[idx:] + dicts[:idx]
    return rearranged_list


def exclude_coordinates(list1: List[Any], list2: List[Any]) -> List[Any]:
    """Downloads similar values in list 2 from list 1"""
    set2 = set(list2)
    subtracted_list = [tefle for tefle in list1 if tefle not in set2]
    return subtracted_list


def find_smallest_lists(list_of_lists: List[List[Any]]) -> List[List[Any]]:
    """From a list of lists finds the small list"""
    min_length = min(len(sublist) for sublist in list_of_lists)
    smallest_lists = [sublist for sublist in list_of_lists if len(sublist) == min_length]
    return smallest_lists


def unique_path_destinations(list_of_lists: List[List[Any]]) -> List[Any]:
    new_lst = []
    for lst in list_of_lists:
        if lst[len(lst)-1] not in new_lst:
            new_lst.append(lst[len(lst)-1])
    return new_lst


def find_path_for_cell(list_of_lists: List[List[Any]], lst: List[Tuple[int, int]]) -> List[List[Any]]:
    new_lst = []
    for cor in lst:
        for path in list_of_lists:
            if path[-1] == cor:
                new_lst.append(path)
    return new_lst


def group_coordinates(tapele_list):
    grouped_list = {}
    for tapele in tapele_list:
        key = tapele[0]
        if key in grouped_list:
            grouped_list[key].append(tapele)
        else:
            grouped_list[key] = [tapele]
    return list(grouped_list.values())


def serialize_status(started: Any, end: Any) -> Any:
    return {
        'started': started,
        'end': end,
    }

import pytest
from chinese_checkers import utils as util

def test_is_valid_coordinate_input():
    assert util.is_valid_coordinate_input("1,2") == True
    assert util.is_valid_coordinate_input("1,a") == False
    assert util.is_valid_coordinate_input("1") == False
    assert util.is_valid_coordinate_input("SSSS") == False
    assert util.is_valid_coordinate_input("0,0,1") == False

# Test for group_coordinates_by_row
def test_group_coordinates_by_row():
    tapele_list = [(1, 3), (2, 5), (1, 2), (2, 4)]
    result = util.group_coordinates_by_row(tapele_list)
    assert result == [[(1, 3),(1, 2)], [(2, 5),(2, 4)]]
    tapele_list = [(1, 3),(1,3), (2, 5), (1, 2), (2, 4)]
    result = util.group_coordinates_by_row(tapele_list)
    assert result == [[(1, 3),(1,3),(1, 2)], [(2, 5),(2, 4)]]

# Test for group_coordinates_by_row_reverse
def test_group_coordinates_by_row_descending():
    tapele_list = [(1, 3), (2, 5), (1, 2), (2, 4)]
    result = util.group_coordinates_by_row_descending(tapele_list)
    assert result == [[(2, 5),(2, 4)], [(1, 3),(1, 2)]]
    tapele_list = [(1, 3), (2, 5),(2, 5),(1, 2), (2, 4)]
    result = util.group_coordinates_by_row_descending(tapele_list)
    assert result == [[(2, 5),(2, 5),(2, 4)], [(1, 3),(1, 2)]]

def test_opposite_direction():
    assert util.opposite_direction('N') == ['S']
    assert util.opposite_direction('S') == ['N']
    assert util.opposite_direction('SE') == ['NW']
    assert util.opposite_direction('NW') == ['SE']
    assert util.opposite_direction('SW') == ['NE']
    assert util.opposite_direction('NE') == ['SW']

def test_get_all_subsets():
    input_dict = {'a': 1, 'b': 2, 'c': 3}
    result = util.get_all_subsets(input_dict)
    assert len(result) == 2**len(input_dict)

def test_rearrange_list():
    input_dicts = [{'name': 'Alice'}, {'name': 'Bob'}, {'name': 'Charlie'}]
    result = util.rearrange_list(input_dicts, 'Bob')
    assert result == [{'name': 'Bob'}, {'name': 'Charlie'}, {'name': 'Alice'}]

def test_exclude_coordinates():
    list1 = [1, 2, 3, 4, 5]
    list2 = [2, 4]
    result = util.exclude_coordinates(list1, list2)
    assert result == [1, 3, 5]
    list1 = [(1, 2), (3, 4), (5, 3)]
    list2 = [(2, 4)]
    result = util.exclude_coordinates(list1, list2)
    assert result == [(1, 2), (3, 4), (5, 3)]
    list1 = [(1, 2), (3, 4), (5, 3)]
    list2 = [(3, 4),(3, 4)]
    result = util.exclude_coordinates(list1, list2)
    assert result == [(1, 2), (5, 3)]

def test_find_smallest_lists():
    input_lists = [[1, 2, 3], [4, 5], [6, 7, 8], [9]]
    result = util.find_smallest_lists(input_lists)
    assert result == [[9]]
    input_lists = [[1, 2, 3], [4], [6, 7, 8], [9]]
    result = util.find_smallest_lists(input_lists)
    assert result == [[4],[9]]

def test_unique_path_destinations():
    input_lists = [[(1, 2), (1, 3)], [(2, 4), (2, 5)], [(1, 3), (1, 4)], [(2, 6), (2, 7)]]
    result = util.unique_path_destinations(input_lists)
    assert result == [(1, 3), (2, 5), (1, 4), (2, 7)]
    input_lists = [[(1, 2),(1, 2), (1, 3)],[(1, 2),(1, 2), (1, 3)], [(2, 4), (2, 5)], [(1, 3), (1, 4)], [(2, 6), (2, 7)]]
    result = util.unique_path_destinations(input_lists)
    assert result == [(1, 3), (2, 5), (1, 4), (2, 7)]

def test_find_path_for_cell():
    input_lists = [[(1, 2), (1, 3)], [(2, 4), (2, 5)], [(1, 3), (1, 4)], [(2, 6), (2, 7)]]
    target_cells = [(1, 3), (2, 7)]
    result = util.find_path_for_cell(input_lists, target_cells)
    assert result == [[(1, 2), (1, 3)], [(2, 6), (2, 7)]]
    input_lists = [[(1, 2), (1, 3)], [(2, 4), (2, 5)], [(1, 3), (1, 4)], [(2, 6), (2, 7)]]
    target_cells = [(1, 3), (2, 6)]
    result = util.find_path_for_cell(input_lists, target_cells)
    assert result == [[(1, 2), (1, 3)]]

def test_group_coordinates():
    tapele_list = [(1, 3), (2, 5), (1, 2), (2, 4)]
    result = util.group_coordinates(tapele_list)
    assert result == [[(1, 3), (1, 2)], [(2, 5), (2, 4)]]
    tapele_list = [(1, 3), (2, 5),(1, 3), (1, 2), (2, 4)]
    result = util.group_coordinates(tapele_list)
    assert result == [[(1, 3),(1, 3),(1, 2)], [(2, 5), (2, 4)]]


from chinese_checkers.player import Player

def test_get_name():
    player = Player("Alice", 5, 3, ["red", "blue"])
    assert player.get_name() == "Alice"

def test_get_number_wins():
    player = Player("Bob", 7, 2, ["green"])
    assert player.get_number_wins() == 7

def test_get_number_losses():
    player = Player("Charlie", 4, 6, ["yellow"])
    assert player.get_number_losses() == 6

def test_get_color():
    player = Player("David", 2, 8, ["orange", "purple"])
    assert player.get_color() == ["orange", "purple"]

def test_set_number_wins():
    player = Player("Eve", 3, 4, ["cyan"])
    player.set_number_wins(6)
    assert player.get_number_wins() == 6

def test_set_number_losses():
    player = Player("Frank", 1, 2, ["magenta"])
    player.set_number_losses(5)
    assert player.get_number_losses() == 5

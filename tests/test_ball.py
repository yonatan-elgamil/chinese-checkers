from chinese_checkers.ball import Ball  # Replace 'your_module_name' with the name of the module where your Ball class is defined

def test_get_location():
    ball = Ball("red", (0, 0))
    assert ball.get_location() == (0, 0)

def test_get_color():
    ball = Ball("blue", (0, 0))
    assert ball.get_color() == "blue"

def test_is_possible_replaces():
    ball = Ball("blue", (4, 2))
    assert ball.is_possible_replaces((1, 1)) == True
    assert ball.is_possible_replaces((-1, -1)) == False
    assert ball.is_possible_replaces((0, 0)) == True

def test_replaces():
    ball = Ball("red", (0, 0))
    assert ball.replaces((1, 1)) == True
    assert ball.get_location() == (1, 1)
    assert ball.replaces((-1, -1)) == False

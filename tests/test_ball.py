from chinese_checkers.ball import Ball  # Replace 'your_module_name' with the name of the module where your Ball class is defined

def test_get_position():
    ball = Ball("red", (0, 0))
    assert ball.get_position() == (0, 0)

def test_get_color():
    ball = Ball("blue", (0, 0))
    assert ball.get_color() == "blue"

def test_can_move_to():
    ball = Ball("blue", (4, 2))
    assert ball.can_move_to((1, 1)) == True
    assert ball.can_move_to((-1, -1)) == False
    assert ball.can_move_to((0, 0)) == True

def test_move_to():
    ball = Ball("red", (0, 0))
    assert ball.move_to((1, 1)) == True
    assert ball.get_position() == (1, 1)
    assert ball.move_to((-1, -1)) == False

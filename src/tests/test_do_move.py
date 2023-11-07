import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))


from game import find_jumped_pos, choose_move


def test_find_jump_position():
    jloc = find_jumped_pos(2, 11)
    assert jloc == 6
    jloc = find_jumped_pos(6, 15)
    assert jloc == 11
    jloc = find_jumped_pos(1, 10)
    assert jloc == 5
    jloc = find_jumped_pos(5, 14)
    assert jloc == 10
    jloc = find_jumped_pos(10, 19)
    assert jloc == 14
    jloc = find_jumped_pos(0, 9)
    assert jloc == 4
    jloc = find_jumped_pos(4, 13)
    assert jloc == 9
    jloc = find_jumped_pos(9, 18)
    assert jloc == 13
    jloc = find_jumped_pos(13, 22)
    assert jloc == 18
    jloc = find_jumped_pos(18, 27)
    assert jloc == 22
    jloc = find_jumped_pos(22, 31)
    assert jloc == 27
    jloc = find_jumped_pos(8, 17)
    assert jloc == 12
    jloc = find_jumped_pos(12, 21)
    assert jloc == 17
    jloc = find_jumped_pos(17, 26)
    assert jloc == 21
    jloc = find_jumped_pos(21, 30)
    assert jloc == 26
    jloc = find_jumped_pos(16, 25)
    assert jloc == 20
    jloc = find_jumped_pos(20, 29)
    assert jloc == 25


def test_choose_move():
    move = (13, 22)
    chosen_move = choose_move(move)
    assert chosen_move == [(13, 22)]

    move = [31, 22, 15, 6, 13, 4]
    chosen_move = choose_move(move)
    assert chosen_move == [(31, 22), (22, 15), (15, 6), (6, 13), (13, 4)]

    move = [28, 21, 12, 5, 14]
    chosen_move = choose_move(move)
    assert chosen_move == [(28, 21), (21, 12), (12, 5), (5, 14)]

    move = [22, 15, 6]
    chosen_move = choose_move(move)
    assert chosen_move == [(22, 15), (15, 6)]


if __name__ == "__main__":
    pytest.main()

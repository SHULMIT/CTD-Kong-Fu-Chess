import unittest

from model.position import Position


class TestPositionEquality(unittest.TestCase):

    def test_equal_positions(self):
        self.assertEqual(Position(2, 3), Position(2, 3))

    def test_different_row(self):
        self.assertNotEqual(Position(1, 3), Position(2, 3))

    def test_different_column(self):
        self.assertNotEqual(Position(2, 1), Position(2, 3))


class TestPositionImmutability(unittest.TestCase):

    def test_cannot_set_row(self):
        pos = Position(1, 2)
        with self.assertRaises(Exception):
            pos.row = 99

    def test_cannot_set_column(self):
        pos = Position(1, 2)
        with self.assertRaises(Exception):
            pos.column = 99


class TestPositionOffset(unittest.TestCase):

    def test_offset_moves_position(self):
        pos = Position(3, 3)
        self.assertEqual(pos.offset(1, 0), Position(4, 3))
        self.assertEqual(pos.offset(0, -1), Position(3, 2))
        self.assertEqual(pos.offset(-1, 1), Position(2, 4))

    def test_offset_returns_new_object(self):
        pos = Position(0, 0)
        new_pos = pos.offset(1, 1)
        self.assertIsNot(pos, new_pos)


class TestPositionHashable(unittest.TestCase):

    def test_can_be_used_in_set(self):
        positions = {Position(0, 0), Position(0, 1), Position(0, 0)}
        self.assertEqual(len(positions), 2)

    def test_can_be_used_as_dict_key(self):
        mapping = {Position(1, 2): "wR"}
        self.assertEqual(mapping[Position(1, 2)], "wR")


class TestPositionStr(unittest.TestCase):

    def test_str_format(self):
        self.assertEqual(str(Position(1, 4)), "(1, 4)")


if __name__ == "__main__":
    unittest.main()

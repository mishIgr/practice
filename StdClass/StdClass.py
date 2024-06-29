class Point:
    def __init__(self, x: int, y: int, mark: int) -> None:
        self._x = x
        self._y = y
        self._mark = mark

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def mark(self) -> int:
        return self._mark


class Rectangle:
    def __init__(self, left_up_point: Point, right_down_point: Point) -> None:
        self._left_up_point = left_up_point
        self._right_down_point = right_down_point

    @property
    def lup(self):
        return self._left_up_point

    @property
    def rdp(self):
        return self._right_down_point


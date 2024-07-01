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

    def copy(self):
        return Point(self._x, self._y, self._mark)


class Rectangle:
    def __init__(self, left_up_point: Point, right_down_point: Point) -> None:
        if left_up_point.x > right_down_point.x or left_up_point.y < left_up_point.y:
            raise ValueError('PIt is impossible to create a square based on points.')
        self._left_up_point = left_up_point
        self._right_down_point = right_down_point

    @property
    def lup(self):
        return self._left_up_point.copy()

    @property
    def rdp(self):
        return self._right_down_point.copy()


from dataclasses import dataclass


class Point:
    def __init__(self, x: int, y: int, mark: int) -> None:
        if not (isinstance(x, int) and isinstance(y, int) and isinstance(mark, int)):
            raise TypeError('x and y and mark must be integers')
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
        if not (isinstance(left_up_point, Point) and isinstance(right_down_point, Point)):
            raise TypeError('left_up_point and right_down_point and must be Point')
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

    def copy(self):
        return Rectangle(self.lup, self.rdp)


@dataclass
class ParamFitness:
    encore: int
    fine: int

    def __post_init__(self) -> None:
        if self.encore < 1 or self.fine < 1:
            raise ValueError('Positive parameters were expected.')


@dataclass
class ParamMutation:
    probability: float  # добавил просто вероятность мутации, можно убрать, если писать отдельные функции для мутации увеличения и уменьшения
    expansion: float
    narrowing: float

    def __post_init__(self) -> None:
        if 0 > self.expansion > 1 or 0 > self.narrowing > 1 or 0 > self.probability > 1:
            raise ValueError('The parameters cannot represent the probability.')


@dataclass
class ParamProbability:
    crossing: float
    mutation: ParamMutation

    def __post_init__(self) -> None:
        if 0 > self.crossing > 1:
            raise ValueError('The parameter(crossing) cannot represent the probability.')


@dataclass
class ParamGeneticAlgorithm:
    probability: ParamProbability
    fitness: ParamFitness
    num_individuals: int

    def __post_init__(self) -> None:
        if self.num_individuals < 1:
            raise ValueError('Positive parameter(num_individuals) were expected.')


@dataclass
class PairRectangleInt:
    rec: Rectangle
    value: int

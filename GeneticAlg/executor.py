from typing import Callable
from GeneticAlg.StdClass import *
from queue import Queue


class State:
    def __init__(self, solutions: list[RectangleInfo], num_state: int) -> None:
        self._solutions = [info.copy() for info in solutions]
        self._num_state = num_state
        self._counter = 0
        self._rectangles = [info.rectangle.copy() for info in solutions]

    @property
    def step(self):
        return self._num_state

    def get_values(self) -> list[Rectangle]:
        return [info.rectangle.copy() for info in self._solutions]

    def __iter__(self):
        self._counter = 0
        return self

    def __next__(self):
        if self._counter < len(self._rectangles):
            self._counter += 1
            return self._rectangles[self._counter - 1].copy()
        else:
            raise StopIteration

    def __str__(self) -> str:
        return (f'Лучшее решение: {self._solutions[0].one_points_in} точек с меткой 1; '
                f'{self._solutions[0].zero_points_in} точек с меткой 0')


@dataclass
class StoreData:
    points: list[Point]
    value_params: dict[str, float]
    selection_method: Callable[[dict[Func, ...], list[Point], list[RectangleInfo], ParamGeneticAlgorithm], list[Rectangle]]


class Executor:
    def __init__(self,
                 next_generation: Callable[[dict[Func, ...], list[Point], list[RectangleInfo], ParamGeneticAlgorithm], list[Rectangle]],
                 func: dict[Func, ...],
                 points: list[Point],
                 first_generation: list[RectangleInfo],
                 param: ParamGeneticAlgorithm,
                 value_param: dict[str, float]) -> None:
        self._next_generation = next_generation
        self._func = func
        self._points = [p.copy() for p in points]
        self._generations = [None, [info.copy() for info in first_generation]]
        self._param = param.copy()
        self._counter_generation = 0
        self._max_generation = 1
        self._data: StoreData = StoreData(points=points,
                                          value_params=value_param,
                                          selection_method=next_generation)

    def get_data(self) -> StoreData:
        return self._data

    def get_state(self) -> State | None:
        if self._counter_generation == 0:
            return None

        queue = Queue()
        max_fitness = ~0 - 1
        for info in self._generations[self._counter_generation]:
            if queue.qsize() < 3:
                queue.put(info.copy())
                max_fitness = max(info.fitness, max_fitness)
            elif info.fitness > max_fitness:
                queue.put(info.copy())
                queue.get()
                max_fitness = info.fitness
        return State(sorted([queue.get().copy() for _ in range(3)], key=lambda r: r.fitness, reverse=True), self._counter_generation)

    def update_solution(self, num: int = 1) -> None:
        if self._counter_generation + num < 0:
            self._counter_generation = 0
            return

        if self._counter_generation + num < self._max_generation:
            self._counter_generation += num
            return

        num -= self._max_generation - self._counter_generation
        for _ in range(num):
            self._generations.append(self._next_generation(self._func, self._points, self._generations[-1], self._param))

        self._max_generation = self._counter_generation = self._max_generation + num

    def restart(self):
        self._counter_generation = 0


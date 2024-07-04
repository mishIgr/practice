from typing import Callable
from StdClass import *
from queue import Queue


class State:
    def __init__(self, points: list[Point], solutions: list, best_solution: Rectangle):
        self._points = points
        self._solutions = solutions
        self._best_solution = best_solution

    def get_values(self) -> tuple:
        ...

    def __str__(self):
        counter = [0] * 2
        for point in self._points:
            if self._best_solution.lup.x <= point.x <= self._best_solution.rdp.x and self._best_solution.lup.y >= point.y >= self._best_solution.rdp.y:
                counter[point.mark] += 1
        return f'Best solution: points0: {counter[0]}, points1: {counter[1]}'


class Executor:
    def __init__(self,
                 next_generation: Callable[[dict[Func, ...], list[Point], list[RectangleInfo], ParamGeneticAlgorithm], list[Rectangle]],
                 func: dict[Func, ...],
                 points: list[Point],
                 first_generation: list[RectangleInfo],
                 param: ParamGeneticAlgorithm) -> None:
        self._func = func
        self._next_generation = next_generation
        self._points = points
        self._generations = [first_generation]
        self._param = param
        self._counter_generation = 0
        self._max_generation = 0

    def get_state(self) -> State:
        queue = Queue()
        max_fitness = ~0 - 1
        for pair in self._generations[self._counter_generation]:
            if queue.qsize() < 3:
                queue.put(Rectangle(pair.rec.lup, pair.rec.rdp))
                max_fitness = max(pair.value, max_fitness)
            elif pair.value > max_fitness:
                queue.put(pair.rec.copy())
                queue.get()
                max_fitness = pair.value
        tmp_solution = [queue.get() for _ in range(3)]
        return State([point.copy() for point in self._points],
                     [sol.rec.copy() for sol in tmp_solution],
                     max(tmp_solution, key=lambda s: s.value).rec.copy())

    def update_solution(self, num: int = 1) -> None:
        if self._counter_generation + num < 0:
            self._counter_generation = 0
            return

        if self._counter_generation + num < self._max_generation:
            self._counter_generation += num
            return

        num -= self._max_generation - self._counter_generation
        for _ in range(num):
            self._generations.append(self._next_generation(self._points, self._generations[-1], self._param))

        self._max_generation = self._counter_generation = self._max_generation + num

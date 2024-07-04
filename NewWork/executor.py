from typing import Callable
from StdClass import *
from queue import Queue


class State:
    def __init__(self, solutions: list[RectangleInfo]):
        self._solutions = solutions

    def get_values(self) -> list[Rectangle]:
        return [info.rectangle for info in self._solutions]

    def __str__(self):
        return f'Тут будет текст.'


class Executor:
    def __init__(self,
                 next_generation: Callable[[dict[Func, ...], list[Point], list[RectangleInfo], ParamGeneticAlgorithm], list[Rectangle]],
                 func: dict[Func, ...],
                 points: list[Point],
                 first_generation: list[RectangleInfo],
                 param: ParamGeneticAlgorithm) -> None:
        self._next_generation = lambda generation, f=func.copy(), po=points.copy(), pa=param: next_generation(f, po, generation, pa)
        self._generations = [first_generation]
        self._counter_generation = 0
        self._max_generation = 0

    def get_state(self) -> State:
        queue = Queue()
        max_fitness = ~0 - 1
        for pair in self._generations[self._counter_generation]:
            if queue.qsize() < 3:
                queue.put(Rectangle(pair.rectangle.lup, pair.rectangle.rdp))
                max_fitness = max(pair.fitness, max_fitness)
            elif pair.fitness > max_fitness:
                queue.put(pair.rectangle.copy())
                queue.get()
                max_fitness = pair.fitness
        return State([queue.get().copy() for _ in range(3)])

    def update_solution(self, num: int = 1) -> None:
        if self._counter_generation + num < 0:
            self._counter_generation = 0
            return

        if self._counter_generation + num < self._max_generation:
            self._counter_generation += num
            return

        num -= self._max_generation - self._counter_generation
        for _ in range(num):
            self._generations.append(self._next_generation(self._generations[-1]))

        self._max_generation = self._counter_generation = self._max_generation + num

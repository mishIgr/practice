from dataclasses import dataclass
from StdClass.StdClass import *
from random import random


@dataclass
class ParamFitness:
    encore: int
    fine: int

    def __post_init__(self) -> None:
        if self.encore < 1 or self.fine < 1:
            raise ValueError('Positive parameters were expected.')


@dataclass
class ParamMutation:
    expansion: float
    narrowing: float

    def __post_init__(self) -> None:
        if 0 > self.expansion > 1 or 0 > self.expansion > 1:
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


def first_generation(points: list[Point], num_individuals: int) -> list[Rectangle]:
    ...


def mutation(rectangle: Rectangle) -> Rectangle:
    ...


def crossing(rectangle1: Rectangle, rectangle2: Rectangle) -> Rectangle:
    ...


def func_fitness(points: list[Point], rectangle: Rectangle, param_fitness=ParamFitness(1, 1)) -> int:
    ...


def next_generation(points: list[Point], rectangles: list[Rectangle], param: ParamGeneticAlgorithm) -> list[Rectangle]:
    ...

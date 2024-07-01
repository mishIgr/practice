from dataclasses import dataclass
from StdClass.StdClass import *
from random import random


@dataclass
class ParamFitness:
    encore: int
    fine: int


@dataclass
class ParamMutation:
    expansion: float
    narrowing: float


@dataclass
class ParamProbability:
    crossing: float
    mutation: ParamMutation


@dataclass
class ParamGeneticAlgorithm:
    probability: ParamProbability
    fitness: ParamFitness
    num_individuals: int


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

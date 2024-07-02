from StdClass.StdClass import *
from typing import Callable
import random
import matplotlib.pyplot as plt


def first_generation(points: list[Point], num_individuals: int) -> list[PairRectangleInt]:
    points = sorted(points, key=lambda p: (p.x, p.y)) # когда будет класс, переместить сортировку в init
    # (список points должен поступать отсортированным)
    rectangles = []

    for i in range(num_individuals):
        x_min, x_max = sorted((points[random.randint(0, len(points) - 1)].x + random.randint(-5, 5) for k in range(2)))
        # выбираем 2 случайные координаты х из массива точек и задаем значение, сортируем, чтобы узнать, какая из них большая и меньшая
        y_min, y_max = sorted((points[random.randint(0, len(points) - 1)].y + random.randint(-5, 5) for k in range(2)))
        # то же самое, только с координатами y

        left_up_point = Point(x_min, y_max, 1)
        right_bottom_point = Point(x_max, y_min, 1)
        # формируем точки на координатной прямой

        rectangles.append(Rectangle(left_up_point, right_bottom_point))

    for i in rectangles:
        print(f'left up: {i.lup.x} {i.lup.y}, right bottom: {i.rdp.x} {i.rdp.y}') # логи

    return rectangles


def mutation(rectangle: Rectangle) -> Rectangle: # в эту функцию добаить прием параметра мутации
    extension_chance = 0.7
    # шанс на увеличение/уменьшение должен передаваться в функцию

    left_up_point = rectangle.lup
    right_bottom_point = rectangle.rdp

    x_mutation = random.randint(0, right_bottom_point.x - left_up_point.x // 2 + 1)
    y_mutation = random.randint(0, left_up_point.y - right_bottom_point.y // 2 + 1)
    # мутация координат (случайное значение от 1 до высоты/ширины прямоугольника, деленной на 2)

    if random.random() < extension_chance: # увеличение
        new_x, new_y = right_bottom_point.x + x_mutation, left_up_point.y + y_mutation

    else: # уменьшение
        new_x, new_y = right_bottom_point.x - x_mutation, left_up_point.y - y_mutation

    left_up_x, left_up_y, right_bottom_x, right_bottom_y = \
    min(left_up_point.x, new_x), max(right_bottom_point.y, new_y), \
    max(left_up_point.x, new_x), min(right_bottom_point.y, new_y)

    new_rectangle = Rectangle(Point(left_up_x, left_up_y, 1), Point(right_bottom_x, right_bottom_y, 1))

    print(f'mutation - left up: {rectangle.lup.x} {rectangle.lup.y}, right bottom: {rectangle.rdp.x} {rectangle.rdp.y}') # логи

    return new_rectangle


def crossing(rectangle1: Rectangle, rectangle2: Rectangle) -> Rectangle:
    # иммитация двоичного скрещивания

    def calculate_beta(eta):
        u = random.random()
        if u <= 0.5:
            return (2 * u) ** (1 / (eta + 1))
        else:
            return ((1 - u) / 2) ** (1 / (eta + 1))

    beta = calculate_beta(1) # определить, каким будет значение эта!

    rectangle1_left_up_point, rectangle1_right_bottom_point = rectangle1.lup, rectangle1.rdp
    rectangle2_left_up_point, rectangle2_right_bottom_point = rectangle2.lup, rectangle2.rdp

    x_offspring1 = int(round((1 + beta) * rectangle1_right_bottom_point.x + (1 - beta) * rectangle2_right_bottom_point.x) / 2)
    x_offspring2 = int(round((1 - beta) * rectangle1_right_bottom_point.x + (1 + beta) * rectangle2_right_bottom_point.x) / 2)

    y_offspring1 = int(round((1 + beta) * rectangle1_right_bottom_point.y + (1 - beta) * rectangle2_right_bottom_point.y) / 2)
    y_offspring2 = int(round((1 - beta) * rectangle1_right_bottom_point.y + (1 + beta) * rectangle2_right_bottom_point.y) / 2)

    new_left_up_point = Point(min(x_offspring1, x_offspring2), max(y_offspring1, y_offspring2), 1)
    new_right_bottom_point = Point(max(x_offspring1, x_offspring2), min(y_offspring1, y_offspring2), 1)

    new_rectangle = Rectangle(new_left_up_point, new_right_bottom_point)

    print(f'crossing - beta: {beta} left up: {x_offspring1} {y_offspring1}, right bottom: {x_offspring2} {y_offspring2}')  # логи
    return new_rectangle


def fitness(points: list[Point], rectangle: Rectangle, param_fitness=ParamFitness(1, 1)) -> int:
    points = sorted(points, key=lambda p: (p.x, p.y))  # когда будет класс, переместить сортировку в init
    # (список points должен поступать отсортированным)

    left_up_point = rectangle.lup
    right_bottom_point = rectangle.rdp

    fitness_ratio = 0

    for point in points:
        if point.x <= right_bottom_point.x:
            if left_up_point.x <= point.x and right_bottom_point.y <= point.y <= left_up_point.y:
                if point.mark == 1:
                    fitness_ratio += param_fitness.encore
                else:
                    fitness_ratio -= param_fitness.fine
        else:
            break

    return fitness_ratio


def get_func_next_generation(func_mutation: Callable[[Rectangle], Rectangle],
                             func_crossing: Callable[[Rectangle, Rectangle], Rectangle],
                             func_fitness: Callable[[list[Point], Rectangle, ParamFitness], int]) -> (
        Callable)[[list[Point], list[PairRectangleInt], ParamGeneticAlgorithm], list[PairRectangleInt]]:

    def next_generation(points: list[Point], rectangles: list[PairRectangleInt], param: ParamGeneticAlgorithm) -> list[PairRectangleInt]:
        new_generation = []
        total_fitness = sum([pair.value for pair in rectangles])

        def select_parent(): # выбор родителя
            pick = random.uniform(0, total_fitness)
            current = 0
            for pair in rectangles:
                current += pair.fitness
                if current > pick:
                    return pair.rectangle
            return rectangles[-1].rectangle

        while len(new_generation) < param.num_individuals:
            if random.random() < param.probability.crossing:
                parent1 = select_parent()
                parent2 = select_parent()
                descendant = func_crossing(parent1, parent2)
            else:
                parent = select_parent()
                descendant = parent

            if random.random() < param.probability.mutation.probability: #
                descendant = func_mutation(descendant)

            fitness = func_fitness(points, descendant, param)
            new_generation.append(PairRectangleInt(descendant, fitness))

    return next_generation


def visualize_population(points, rectangles): # функции визуализации будут удалены
    plt.figure(figsize=(10, 10))

    for point in points:
        if point.mark == 1:
            plt.plot(point.x, point.y, 'bo')
        else:
            plt.plot(point.x, point.y, 'ro')

    for rect in rectangles:
        lup = rect.lup
        rdp = rect.rdp

        rect_x = [lup.x, lup.x, rdp.x, rdp.x, lup.x]
        rect_y = [lup.y, rdp.y, rdp.y, lup.y, lup.y]

        plt.plot(rect_x, rect_y, 'r-')

    plt.xlim(-15, 15)
    plt.ylim(-15, 15)
    plt.grid(True)
    plt.title("Points and Rectangles Visualization")
    plt.show()


def visualize_mutation(original: Rectangle, mutated: Rectangle):
    fig, ax = plt.subplots()

    original_width = original.rdp.x - original.lup.x
    original_height = original.lup.y - original.rdp.y
    orig_rect = plt.Rectangle((original.lup.x, original.rdp.y), original_width, original_height,
                              fill=None, edgecolor='blue', label='Original')

    mutated_width = mutated.rdp.x - mutated.lup.x
    mutated_height = mutated.lup.y - mutated.rdp.y
    mut_rect = plt.Rectangle((mutated.lup.x, mutated.rdp.y), mutated_width, mutated_height,
                             fill=None, edgecolor='red', label='Mutated')

    ax.add_patch(orig_rect)
    ax.add_patch(mut_rect)

    min_x = min(original.lup.x, mutated.lup.x) - 10
    max_x = max(original.rdp.x, mutated.rdp.x) + 10
    min_y = min(original.rdp.y, mutated.rdp.y) - 10
    max_y = max(original.lup.y, mutated.lup.y) + 10

    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.legend()
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(color='gray', linestyle='--', linewidth=0.5)

    plt.plot(mutated.lup.x, mutated.lup.y, 'ro')
    plt.plot(mutated.rdp.x, mutated.rdp.y, 'bo')
    plt.show()


def visualize_crossing(rect1: Rectangle, rect2: Rectangle, new_rect: Rectangle):
    plt.figure(figsize=(10, 10))

    def draw_rectangle(rect, color):
        lup, rdp = rect.lup, rect.rdp
        rect_x = [lup.x, lup.x, rdp.x, rdp.x, lup.x]
        rect_y = [lup.y, rdp.y, rdp.y, lup.y, lup.y]
        plt.plot(rect_x, rect_y, color)


    draw_rectangle(rect1, 'b-')  # синий
    draw_rectangle(rect2, 'g-')  # зеленый

    # прямоугольник потомок
    draw_rectangle(new_rect, 'r-')  # красный

    plt.xlim(-15, 15)
    plt.ylim(-15, 15)
    plt.grid(True)
    plt.title("Rectangles Crossing Visualization")
    plt.show()


points = [
    Point(1, 2, 1), Point(2, 3, 1), Point(3, 5, 0), Point(4, 1, 1), Point(5, 6, 0),
    Point(6, 4, 1), Point(7, 8, 1), Point(8, 7, 0), Point(9, 9, 1), Point(10, 10, 1)
]

# генерация первой популяции
# rectangles = first_generation(points, 1)
# for i in rectangles:
#     print(fitness(points, i))
# visualize_population(points, rectangles)

# мутация
# rectangle = Rectangle(Point(1,1, 1), Point(1,-2,1))
# mutated_rectangle = mutation(rectangle)
# visualize_mutation(rectangle, mutated_rectangle)

# скрещивание
# rectangle1 = Rectangle(Point(-2,2, 1), Point(10,-9,1))
# rectangle2 = Rectangle(Point(-1,1, 1), Point(1,-1,1))
# new_rectangle = crossing(rectangle1, rectangle2)
# visualize_crossing(rectangle1, rectangle2, new_rectangle)

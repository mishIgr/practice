from StdClass.StdClass import *
import random
import matplotlib.pyplot as plt


def first_generation(func: dict[Func, ...], points: list[Point], num_individuals: int) -> list[RectangleInfo]:
    rectangles = []

    for i in range(num_individuals):
        random_point = points[random.randint(0, len(points) - 1)]
        # случайная точка для генерации случайного смещения
        offset_border_x, offset_border_y = abs(random_point.x) // 2, abs(random_point.y) // 2
        # границы случайного смещения

        x_min, x_max = sorted((points[random.randint(0, len(points) - 1)].x + random.randint(-offset_border_x, offset_border_x) for k in range(2)))
        # выбираем 2 случайные координаты х из массива точек и задаем значение, сортируем, чтобы узнать, какая из них большая и меньшая
        y_min, y_max = sorted((points[random.randint(0, len(points) - 1)].y + random.randint(-offset_border_y, offset_border_y) for k in range(2)))
        # то же самое, только с координатами y

        left_up_point = Point(x_min, y_max, 1)
        right_bottom_point = Point(x_max, y_min, 1)
        # формируем точки на координатной прямой

        current_rectangle = Rectangle(left_up_point, right_bottom_point)
        current_rectangle_info = func[Func.Fitness](points, current_rectangle) # fitness функция возвращает класс rectangle_info

        rectangles.append(current_rectangle_info)

    for i in rectangles:
        print(f'fitness: {i.fitness}, left up: {i.rectangle.lup.x} {i.rectangle.lup.y}, right bottom: {i.rectangle.rdp.x} {i.rectangle.rdp.y}') # логи

    return rectangles


def mutation(points: list[Point], rectangle_info: RectangleInfo, parameters: ParamMutation) -> Rectangle:
    left_up_point = rectangle_info.rectangle.lup
    right_bottom_point = rectangle_info.rectangle.rdp

    x_mutation = random.randint(0, abs(right_bottom_point.x - left_up_point.x) // 2 + 1)
    y_mutation = random.randint(0, abs(left_up_point.y - right_bottom_point.y) // 2 + 1)
    # мутация координат (случайное значение от 1 до высоты/ширины прямоугольника, деленной на 2)

    if random.random() < parameters.expansion: # увеличение
        new_x, new_y = right_bottom_point.x + x_mutation, left_up_point.y + y_mutation

    else: # уменьшение
        new_x, new_y = right_bottom_point.x - x_mutation, left_up_point.y - y_mutation

    left_up_x, left_up_y, right_bottom_x, right_bottom_y = \
    min(left_up_point.x, new_x), max(right_bottom_point.y, new_y), \
    max(left_up_point.x, new_x), min(right_bottom_point.y, new_y)

    new_rectangle = Rectangle(Point(left_up_x, left_up_y, 1), Point(right_bottom_x, right_bottom_y, 1))

    # print(f'mutation - left up: {rectangle_info.rectangle.lup.x} {rectangle_info.rectangle.lup.y}, right bottom: {rectangle_info.rectangle.rdp.x} {rectangle_info.rectangle.rdp.y}') # логи

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

    # print(f'crossing - beta: {beta} left up: {x_offspring1} {y_offspring1}, right bottom: {x_offspring2} {y_offspring2}')  # логи
    return new_rectangle


def fitness(points: list[Point], rectangle: Rectangle, param_fitness=ParamFitness(1, 1)) -> RectangleInfo:
    fitness_ratio = 0
    zero_points_count = 0
    one_points_count = 0

    for point in points:
        if point in rectangle:
            if point.mark == 1:
                fitness_ratio += param_fitness.encore
                one_points_count += 1
            else:
                fitness_ratio -= param_fitness.fine
                zero_points_count += 1

    rectangle_info = RectangleInfo(rectangle, fitness_ratio, zero_points_count, one_points_count)

    return rectangle_info


# def get_func_next_generation(func_mutation: Callable[[Rectangle], Rectangle],
#                              func_crossing: Callable[[Rectangle, Rectangle], Rectangle],
#                              func_fitness: Callable[[list[Point], Rectangle, ParamFitness], int]) -> (
#         Callable)[[list[Point], list[PairRectangleInt], ParamGeneticAlgorithm], list[PairRectangleInt]]:
#
#     def next_generation(points: list[Point], rectangles: list[PairRectangleInt], param: ParamGeneticAlgorithm) -> list[PairRectangleInt]:
#         new_generation = []
#         total_fitness = sum([pair.value for pair in rectangles])
#
#         def select_parent(): # выбор родителя
#             pick = random.uniform(0, total_fitness)
#             current = 0
#             for pair in rectangles:
#                 current += pair.fitness
#                 if current > pick:
#                     return pair.rectangle
#             return rectangles[-1].rectangle
#
#         while len(new_generation) < param.num_individuals:
#             if random.random() < param.probability.crossing:
#                 parent1 = select_parent()
#                 parent2 = select_parent()
#                 descendant = func_crossing(parent1, parent2)
#             else:
#                 parent = select_parent()
#                 descendant = parent
#
#             if random.random() < param.probability.mutation.probability: #
#                 descendant = func_mutation(descendant)
#
#             fitness = func_fitness(points, descendant, param)
#             new_generation.append(PairRectangleInt(descendant, fitness))
#
#     return next_generation


def select_parent(rectangles: list[RectangleInfo]):
    return random.choice(rectangles)  # можно совместить и сделать метод рулетки
                                      # то есть родители с лучшей приспособленностью выбираются с большей вероятностью
                                      # если будем делать разные методы отбора, то нужно эту функцию занести внутрь get_next_generation

def get_next_generation(func: dict[Func, ...], points: list[Point], rectangles: list[RectangleInfo], parameters: ParamGeneticAlgorithm) -> list[RectangleInfo]:
    # отбор усечением

    rectangles.sort(key=lambda recti: recti.fitness, reverse=True) # можно заменить на кучу или очередь с приоритетом
    selected = rectangles[:len(rectangles) // 2] # оставляем половину лучших из популяции
                                                 # можно добавить параметр - усечение популяции

    new_generation = []

    for i in range(parameters.num_individuals):
        if random.random() < parameters.probability.crossing: # скрещищвание
            parent1 = select_parent(selected).rectangle
            # selected.pop(selected.index(parent1))     # трудоемкая операция за O(n)
            parent2 = select_parent(selected).rectangle # без нее особь может скрещиваться сама с собой
                                                        # уточнить по этому поводу
            offspring = func[Func.Crossing](parent1, parent2)
            offspring_info = func[Func.Fitness](points, offspring, parameters.fitness)


        else: # оставляем особь предыдущего поколения
            offspring_info = random.choice(selected)

        if random.random() < parameters.probability.mutation:  # мутация, происходит только при скрещивании
            offspring = func[Func.Mutation](points, offspring_info, parameters.probability.param_mutation)
            offspring_info = func[Func.Fitness](points, offspring, parameters.fitness)

        new_generation.append(offspring_info)

        print(f'fitness: {offspring_info.fitness}, left up: {offspring_info.rectangle.lup.x} {offspring_info.rectangle.lup.y}, right bottom: {offspring_info.rectangle.rdp.x} {offspring_info.rectangle.rdp.y}') # логи

    return new_generation


def visualize_population(points, rectangles): # функции визуализации будут удалены
    plt.figure(figsize=(10, 10))

    for point in points:
        if point.mark == 1:
            plt.plot(point.x, point.y, 'bo')
        else:
            plt.plot(point.x, point.y, 'ro')

    for rect in rectangles:
        lup = rect.rectangle.lup
        rdp = rect.rectangle.rdp

        rect_x = [lup.x, lup.x, rdp.x, rdp.x, lup.x]
        rect_y = [lup.y, rdp.y, rdp.y, lup.y, lup.y]

        plt.plot(rect_x, rect_y, 'r-')

    plt.xlim(-150, 150)
    plt.ylim(-150, 150)
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



point_quantity = 50
points = [Point(random.randint(-120, 120), random.randint(-120, 120), random.randint(0, 1)) for i in range(point_quantity)]

crossing_chance = 0.6
mutation_chance = 0.1
expansion_chance = 0.7
narrowing_chance = 1 - expansion_chance
encore = 100
fine = 1
num_individuals = 10
num_generations = 10

parameters = ParamGeneticAlgorithm(ParamProbability(crossing_chance, mutation_chance, ParamMutation(expansion_chance, narrowing_chance)),\
                                   ParamFitness(encore, fine),\
                                   num_individuals)

# генерация первой популяции
func = {
    Func.Mutation: mutation,
    Func.Crossing: crossing,
    Func.Fitness: fitness
}
print('GENERATION 1')
rectangles = first_generation(func, points, num_individuals)
visualize_population(points, rectangles)

# генерация новых популяций
for i in range(1, num_generations):
    print(f'GENERATION {i + 1}')
    rectangles = get_next_generation(func, points, rectangles, parameters)
    visualize_population(points, rectangles)


# мутация
# rectangle = Rectangle(Point(60,100, 1), Point(120,-111,1))
# rectangle_info = RectangleInfo(rectangle, fitness(points, rectangle), 0, 0)
#
# mutated_rectangle = mutation(points, rectangle_info, parameters.probability.param_mutation)
# visualize_mutation(rectangle, mutated_rectangle)

# скрещивание
# rectangle1 = Rectangle(Point(-2,2, 1), Point(10,-9,1))
# rectangle2 = Rectangle(Point(-1,1, 1), Point(1,-1,1))
# new_rectangle = crossing(rectangle1, rectangle2)
# visualize_crossing(rectangle1, rectangle2, new_rectangle)

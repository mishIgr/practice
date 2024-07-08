from StdClass import *
import random
import matplotlib.pyplot as plt


def first_generation(func: dict[Func, ...], points: list[Point], num_individuals: int) -> list[RectangleInfo]:
    rectangles = []

    for i in range(num_individuals):
        random_point = points[random.randint(0, len(points) - 1)]
        # случайная точка для генерации случайного смещения
        offset_border_x, offset_border_y = abs(random_point.x), abs(random_point.y)
        # границы случайного смещения

        x_min, x_max = sorted(
            (points[random.randint(0, len(points) - 1)].x + random.randint(-offset_border_x, offset_border_x) for k in
             range(2)))
        # выбираем 2 случайные координаты х из массива точек и задаем значение, сортируем, чтобы узнать, какая из них большая и меньшая
        y_min, y_max = sorted(
            (points[random.randint(0, len(points) - 1)].y + random.randint(-offset_border_y, offset_border_y) for k in
             range(2)))
        # то же самое, только с координатами y

        left_up_point = Point(x_min, y_max, 1)
        right_bottom_point = Point(x_max, y_min, 1)
        # формируем точки на координатной прямой

        current_rectangle = Rectangle(left_up_point, right_bottom_point)
        current_rectangle_info = func[Func.Fitness](points,
                                                    current_rectangle)  # fitness функция возвращает класс rectangle_info

        rectangles.append(current_rectangle_info)

    for i in rectangles:
        print(
            f'fitness: {i.fitness}, left up: {i.rectangle.lup.x} {i.rectangle.lup.y}, right bottom: {i.rectangle.rdp.x} {i.rectangle.rdp.y}')  # логи

    return rectangles


def mutation_random_point(points: list[Point], rectangle_info: RectangleInfo, parameters: ParamMutation) -> Rectangle:
    # координаты изменяются в соответствии с случайной выбранной точкой внутри или снаружи прямоугольника
    # гарантия того, что количество точек внутри прямоугольника изменится

    left_up_point = rectangle_info.rectangle.lup
    right_bottom_point = rectangle_info.rectangle.rdp

    size_change_sign = 1 if random.random() < parameters.expansion else -1  # выбираем - увеличение или уменьшение

    # print(size_change_sign)

    if size_change_sign == 1:
        needed_points = [point for point in points if point not in rectangle_info.rectangle]
    else:
        needed_points = [point for point in points if point in rectangle_info.rectangle]

    if len(needed_points) == 0:
        needed_points = points

    random_point = random.choice(needed_points).copy()

    if random.random() < 0.5:
        new_left_up_x, new_left_up_y = (random_point.x + 1, random_point.y - 1) if size_change_sign == -1 else (
        random_point.x, random_point.y)
        new_right_bottom_x, new_right_bottom_y = right_bottom_point.x, right_bottom_point.y
    else:
        new_left_up_x, new_left_up_y = (random_point.x - 1, random_point.y + 1) if size_change_sign == -1 else (
        random_point.x, random_point.y)
        new_right_bottom_x, new_right_bottom_y = random_point.x, random_point.y

    if new_left_up_x > new_right_bottom_x:
        new_left_up_x, new_right_bottom_x = new_right_bottom_x, new_left_up_x
    if new_left_up_y < new_right_bottom_y:
        new_left_up_y, new_right_bottom_y = new_right_bottom_y, new_left_up_y
    # гарантия того, что точки встанут на свои места

    new_rectangle = Rectangle(Point(new_left_up_x, new_left_up_y, 1),
                              Point(new_right_bottom_x, new_right_bottom_y, 1))
    # создаем мутанта

    # print(f'mutation - left up: {rectangle_info.rectangle.lup.x} {rectangle_info.rectangle.lup.y}, right bottom: {rectangle_info.rectangle.rdp.x} {rectangle_info.rectangle.rdp.y}') # логи

    return new_rectangle


def mutation_random_change(points: list[Point], rectangle_info: RectangleInfo, parameters: ParamMutation) -> Rectangle:
    # случайное изменение размера, изменение количества точек внутри не гарантируется

    left_up_point = rectangle_info.rectangle.lup
    right_bottom_point = rectangle_info.rectangle.rdp

    size_change_sign = 1 if random.random() < parameters.expansion else -1  # выбираем - увеличение или уменьшение

    # print(size_change_sign)

    x_mutation_1 = random.randint(0, abs(right_bottom_point.x - left_up_point.x) // 2 + 1) * size_change_sign
    x_mutation_2 = random.randint(0, abs(right_bottom_point.x - left_up_point.x) // 2 + 1) * size_change_sign
    y_mutation_1 = random.randint(0, abs(left_up_point.y - right_bottom_point.y) // 2 + 1) * size_change_sign
    y_mutation_2 = random.randint(0, abs(left_up_point.y - right_bottom_point.y) // 2 + 1) * size_change_sign
    # мутация координат (случайное значение от 1 до высоты/ширины прямоугольника, деленной на 2)

    # print(f'x1: {x_mutation_1} x2: {x_mutation_2} y1: {y_mutation_1} y2: {y_mutation_2}')

    new_left_up_x = left_up_point.x - x_mutation_1
    new_right_bottom_x = right_bottom_point.x + x_mutation_2
    new_left_up_y = left_up_point.y + y_mutation_1
    new_right_bottom_y = right_bottom_point.y - y_mutation_2
    # мутация увеличения и уменьшения может происходить в любом направлении

    if new_left_up_x > new_right_bottom_x:
        new_left_up_x, new_right_bottom_x = new_right_bottom_x, new_left_up_x
    if new_left_up_y < new_right_bottom_y:
        new_left_up_y, new_right_bottom_y = new_right_bottom_y, new_left_up_y
    # гарантия того, что точки встанут на свои места

    new_rectangle = Rectangle(Point(new_left_up_x, new_left_up_y, 1),
                              Point(new_right_bottom_x, new_right_bottom_y, 1))
    # создаем мутанта

    return new_rectangle


def mutation_hybrid(points: list[Point], rectangle_info: RectangleInfo, parameters: ParamMutation) -> Rectangle:
    # смешанная функция

    if random.random() < 0.5:
        return mutation_random_point(points, rectangle_info, parameters)
    else:
        return mutation_random_change(points, rectangle_info, parameters)


def calculate_beta(eta):
    u = random.random()
    if u <= 0.5:
        return (2 * u) ** (1 / (eta + 1))
    else:
        return ((1 - u) / 2) ** (1 / (eta + 1))


def crossing(rectangle1: Rectangle, rectangle2: Rectangle) -> Rectangle:
    # иммитация двоичного скрещивания

    beta = calculate_beta(0)  # определить, каким будет значение эта!

    rectangle1_left_up_point, rectangle1_right_bottom_point = rectangle1.lup, rectangle1.rdp
    rectangle2_left_up_point, rectangle2_right_bottom_point = rectangle2.lup, rectangle2.rdp

    x_offspring1 = int(round((1 + beta) * rectangle1_left_up_point.x + (1 - beta) * rectangle2_left_up_point.x) / 2)
    x_offspring2 = int(
        round((1 - beta) * rectangle1_right_bottom_point.x + (1 + beta) * rectangle2_right_bottom_point.x) / 2)

    y_offspring1 = int(round((1 + beta) * rectangle1_left_up_point.y + (1 - beta) * rectangle2_left_up_point.y) / 2)
    y_offspring2 = int(
        round((1 - beta) * rectangle1_right_bottom_point.y + (1 + beta) * rectangle2_right_bottom_point.y) / 2)

    new_left_up_point = Point(min(x_offspring1, x_offspring2), max(y_offspring1, y_offspring2), 1)
    new_right_bottom_point = Point(max(x_offspring1, x_offspring2), min(y_offspring1, y_offspring2), 1)

    new_rectangle = Rectangle(new_left_up_point, new_right_bottom_point)

    # print(f'crossing - beta: {beta} left up: {x_offspring1} {y_offspring1}, right bottom: {x_offspring2} {y_offspring2}')  # логи
    return new_rectangle


def count_points_in_rectangle(points: list[Point], rectangle: Rectangle) -> (int, int):
    # вспомогательная функция для поиска количества точек в прямоугольнике
    zero_points_in = 0
    one_points_in = 0
    for point in points:
        if point in rectangle:
            if point.mark == 1:
                one_points_in += 1
            else:
                zero_points_in += 1

    return zero_points_in, one_points_in


def fitness(points: list[Point], rectangle: Rectangle, param_fitness=ParamFitness(1, 1)) -> RectangleInfo:
    zero_points_count, one_points_count = count_points_in_rectangle(points, rectangle)
    fitness_ratio = one_points_count * param_fitness.encore - zero_points_count * param_fitness.fine

    rectangle_info = RectangleInfo(rectangle, fitness_ratio, zero_points_count, one_points_count)

    return rectangle_info


def select_parent(rectangles: list[RectangleInfo]):
    return random.choice(rectangles)  # можно совместить и сделать метод рулетки
    # то есть родители с лучшей приспособленностью выбираются с большей вероятностью
    # если будем делать разные методы отбора, то нужно эту функцию занести внутрь get_next_generation


def get_new_generation(func: dict[Func, ...], points: list[Point], selected: list[RectangleInfo],
                       parameters: ParamGeneticAlgorithm) -> list[RectangleInfo]:
    new_generation = []

    for i in range(parameters.num_individuals):
        if random.random() < parameters.probability.crossing:  # скрещищвание
            parent1 = select_parent(selected).rectangle
            parent2 = select_parent(selected).rectangle
            offspring = func[Func.Crossing](parent1, parent2)
            offspring_info = func[Func.Fitness](points, offspring, parameters.fitness)

            if random.random() < parameters.probability.mutation:  # мутация, происходит только при скрещивании
                offspring = func[Func.Mutation](points, offspring_info, parameters.probability.param_mutation)
                offspring_info = func[Func.Fitness](points, offspring, parameters.fitness)

        else:  # оставляем особь предыдущего поколения
            offspring_info = random.choice(selected)

        new_generation.append(offspring_info)

        print(
            f'fitness: {offspring_info.fitness}, left up: {offspring_info.rectangle.lup.x} {offspring_info.rectangle.lup.y}, right bottom: {offspring_info.rectangle.rdp.x} {offspring_info.rectangle.rdp.y}')  # логи

    return new_generation


def truncation_selection(func: dict[Func, ...], points: list[Point], rectangles: list[RectangleInfo],
                         parameters: ParamGeneticAlgorithm) -> list[RectangleInfo]:
    # отбор усечением

    rectangles.sort(key=lambda rectangle: rectangle.fitness, reverse=True)
    selected = rectangles[:len(rectangles) // 2]  # оставляем половину лучших из популяции
    # можно добавить параметр - усечение популяции
    return get_new_generation(func, points, selected, parameters)


def roulette_selection(func: dict[Func, ...], points: list[Point], rectangles: list[RectangleInfo],
                       parameters: ParamGeneticAlgorithm) -> list[RectangleInfo]:
    # правило рулетки

    fitness_values = [rectangle_info.fitness for rectangle_info in rectangles]
    min_fitness = min(fitness_values)

    if min_fitness < 0:
        fitness_values = [i - min_fitness for i in fitness_values]
    else:
        fitness_values = [i + 1 for i in fitness_values]
        # +1, чтобы избежать нулевой вероятности

    selected = random.choices(rectangles, weights=fitness_values, k=num_individuals)
    # выбираем родителей с вероятностью, зависящей от приспособленности

    return get_new_generation(func, points, selected, parameters)


def tournament_selection(func: dict[Func, ...], points: list[Point], rectangles: list[RectangleInfo],
                         parameters: ParamGeneticAlgorithm) -> list[RectangleInfo]:
    # турнирный отбор

    selected = []
    tournament_size = min(parameters.num_individuals // 2 + 1, len(rectangles))

    for i in range(parameters.num_individuals):
        tournament = random.sample(rectangles, tournament_size)  # выбираем особей для турнира
        best_individual = max(tournament, key=lambda rectangle: rectangle.fitness)  # выбираем лучшего из турнира
        selected.append(best_individual)

    return get_new_generation(func, points, selected, parameters)


def elite_selection(func: dict[Func, ...], points: list[Point], rectangles: list[RectangleInfo],
                    parameters: ParamGeneticAlgorithm) -> list[RectangleInfo]:
    # элитарный отбор

    num_elites = parameters.num_individuals // 5 + 1  # 20% лучших особей

    rectangles.sort(key=lambda rectangle: rectangle.fitness, reverse=True)
    elites = rectangles[:num_elites]

    new_parameters = ParamGeneticAlgorithm(parameters.probability, parameters.fitness,
                                           parameters.num_individuals - num_elites)
    # создаем параметры для второй части отбора

    return elites + roulette_selection(func, points, rectangles, new_parameters)  # остальные отбираются методом рулетки


def visualize_population(points, rectangles):  # функции визуализации будут удалены
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


def draw_rectangle(rect, color):
    lup, rdp = rect.lup, rect.rdp
    rect_x = [lup.x, lup.x, rdp.x, rdp.x, lup.x]
    rect_y = [lup.y, rdp.y, rdp.y, lup.y, lup.y]
    plt.plot(rect_x, rect_y, color)


def visualize_crossing(rect1: Rectangle, rect2: Rectangle, new_rect: Rectangle):
    plt.figure(figsize=(10, 10))

    draw_rectangle(rect1, 'b-')  # синий
    draw_rectangle(rect2, 'g-')  # зеленый

    # прямоугольник потомок
    draw_rectangle(new_rect, 'r-')  # красный

    plt.xlim(-15, 15)
    plt.ylim(-15, 15)
    plt.grid(True)
    plt.title("Rectangles Crossing Visualization")
    plt.show()


# if __name__ == '__main__':
#     point_quantity = 100
#     points = [Point(random.randint(-120, 120), random.randint(-120, 120), random.randint(0, 1)) for i in
#               range(point_quantity)]
#     # points = [Point(-120, -120, 1), Point(120, 120, 1)]
#     crossing_chance = 0.6
#     mutation_chance = 0.2
#     expansion_chance = 0.7
#     narrowing_chance = 1 - expansion_chance
#     encore = 1
#     fine = 1
#     num_individuals = 10
#     num_generations = 40
#
#     parameters = ParamGeneticAlgorithm(
#         ParamProbability(crossing_chance, mutation_chance, ParamMutation(expansion_chance, narrowing_chance)), \
#         ParamFitness(encore, fine), \
#         num_individuals)
#
#     # генерация первой популяции
#     func = {
#         Func.Mutation: mutation_hybrid,
#         Func.Crossing: crossing,
#         Func.Fitness: fitness
#     }
#     print('GENERATION 1')
#     rectangles = first_generation(func, points, parameters.num_individuals)
#     visualize_population(points, rectangles)
#
#     # генерация новых популяций
#     for i in range(1, num_generations):
#         print(f'GENERATION {i + 1}')
#         rectangles = get_next_generation(func, points, rectangles, parameters)
#     visualize_population(points, rectangles)

# мутация
# rectangle = Rectangle(Point(1,1, 1), Point(1,-2,1))
# rectangle_info = RectangleInfo(rectangle, fitness(points, rectangle), 0, 0)
#
# mutated_rectangle = mutation(points, rectangle_info, parameters.probability.param_mutation)
# visualize_mutation(rectangle, mutated_rectangle)

# скрещивание
# rectangle1 = Rectangle(Point(-2,2, 1), Point(10,-9,1))
# rectangle2 = Rectangle(Point(-1,1, 1), Point(1,-1,1))
# new_rectangle = crossing(rectangle1, rectangle2)
# visualize_crossing(rectangle1, rectangle2, new_rectangle)

__all__ = ['first_generation', 'mutation_random_point', 'crossing', 'fitness', 'get_next_generation']
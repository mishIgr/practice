import csv
from tkinter import filedialog
from tkinter import messagebox
from GeneticAlg.GA import *
import matplotlib.pyplot as plt
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import random
from PIL import Image, ImageTk
from GeneticAlg.executor import *


class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.x_press = None
        self.y_press = None
        self._cur_xlim: float = None
        self._cur_ylim: float = None

    def get_x_lim(self) -> float:
        return self._cur_xlim

    def get_y_lim(self) -> float:
        return self._cur_ylim

    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = 1 / base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
            self._cur_xlim = [xdata - new_width * (1-relx), xdata + new_width * (relx)]
            self._cur_ylim = [ydata - new_height * (1-rely), ydata + new_height * (rely)]
            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def on_press(event):
            if event.inaxes != ax:
                return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.x_press, self.y_press = self.press

        def on_release(event):
            self.press = None
            ax.figure.canvas.draw()

        def on_motion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.x_press
            dy = event.ydata - self.y_press
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()
        fig = ax.get_figure()
        fig.canvas.mpl_connect('button_press_event', on_press)
        fig.canvas.mpl_connect('button_release_event', on_release)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        return on_motion


class Graphic:
    def __init__(self, master: ctk.CTk, points: list[Point]):
        self._points: list[Point] = points
        self.figure, self.ax = plt.subplots(figsize=(6, 5.6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().pack()
        ZoomPan().pan_factory(self.ax)
        ZoomPan().zoom_factory(self.ax, base_scale=1.1)
        self.x_lim_max, self.x_lim_min, self.y_lim_max, self.y_lim_min = self.__get_size()
        self.ax.set_xlim(self.x_lim_min, self.x_lim_max)
        self.ax.set_ylim(self.y_lim_min, self.y_lim_max)
        self._plot_points: list[Point] = points
        self._rectangles: set[int, int, int, int] = set()
        self.__draw_points()

    def __get_size(self) -> tuple[int, int, int, int]:
        max_x, min_x, max_y, min_y = (next(iter(self._points)).x, next(iter(self._points)).x,
                                      next(iter(self._points)).y, next(iter(self._points)).y)
        for point in self._points:
            max_x = max(point.x, max_x)
            min_x = min(point.x, min_x)
            max_y = max(point.y, max_y)
            min_y = min(point.y, min_y)
        return max_x + 5, min_x - 5, max_y + 5, min_y - 5

    def __draw_points(self):
        for point in self._plot_points:
            if point.mark:
                self.ax.plot(point.x, point.y, 'bo')
            else:
                self.ax.plot(point.x, point.y, 'ro')

        self.ax.set_xlim(self.x_lim_min, self.x_lim_max)
        self.ax.set_ylim(self.y_lim_min, self.y_lim_max)

        self.ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()

    def add_rectangles(self, state: State) -> None:
        colors = ['green', 'yellow', "red"]
        bridge = lambda rec, color: (rec.lup.x, rec.rdp.y, rec.rdp.x - rec.lup.x, rec.lup.y - rec.rdp.y, color)
        for i, rec in enumerate(state):
            self.add_rectangle(*bridge(rec, colors[i]))

    def add_rectangle(self, x: int, y: int, width: int, height: int, color_rectangles: str) -> None:
        rectangle = patches.Rectangle((x, y), width, height, color=color_rectangles, alpha=0.4, linewidth=2)
        self._rectangles.add(rectangle)
        self.ax.add_patch(rectangle)
        self.canvas.draw()

    def clear_rectangles(self) -> None:
        for rectangle in self._rectangles:
            rectangle.remove()
        self._rectangles.clear()
        self.canvas.draw()


class MainWindow(ctk.CTk):
    def __init__(self, points: list[Point], executor: Executor, count_iteration: int) -> None:
        super().__init__(fg_color="white")
        self.geometry('1055x630')
        self.title("Генетический алгоритм")
        self.resizable(False, False)
        self._graphic_frame: ctk.CTkFrame = GraphicFrame(self, points, executor, count_iteration)
        self._info_table_frame: ctk.CTkFrame = InfoTableFrame(self)
        self._return_button_frame: ctk.CTkFrame = ReturnButtonFrame(self)
        self._executor: Executor = executor
        print(executor.get_data())

    def add_event(self, event: str) -> None:
        self._info_table_frame.add_event(event)

    def get_executor(self) -> Executor:
        return self._executor


class ReturnButtonFrame(ctk.CTkFrame):
    def __init__(self, master: MainWindow) -> None:
        super().__init__(master=master, fg_color='white')
        self.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.grid_propagate(False)
        self._return_button: ctk.CTkButton = ReturnButton(self)

    def destroy_master(self) -> None:
        self.master.destroy()

    def get_executor(self) -> Executor:
        return self.master.get_executor()

class ReturnButton(ctk.CTkButton):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, text='Вернуться на стартовое окно', width=300, height=50,
                         command=self.__handler_return_button)
        self.grid_propagate(False)
        self.place(relx=0.5, rely=0.2, anchor='center')

    def __handler_return_button(self) -> None:
        self.master.destroy_master()
        StartWindow().restore_data(data=self.master.get_executor().get_data())


class InfoTableFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master=master, fg_color='white', width=450, height=530)
        self.grid_propagate(False)
        self.grid(row=0, column=1, sticky='nsew')
        self.__create_name_label()
        self._view_info_table: ctk.CTkScrollableFrame = ViewInfoTable(self)

    def __create_name_label(self) -> None:
        information_table_label = ctk.CTkLabel(master=self, text="Панель информации", width=600,
                                               text_color='black', font=("Arial", 20), fg_color="white")
        information_table_label.place(relx=0.5, rely=0.05, anchor='center')

    def add_event(self, event: str) -> None:
        self._view_info_table.add_event(event)


class ViewInfoTable(ctk.CTkScrollableFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, height=455, width=420, border_width=2)
        self.place(relx=0.5, rely=0.505, anchor='center')
        self.bind("<Button-4>", lambda _: self._parent_canvas.yview("scroll", -1, "units"))
        self.bind("<Button-5>", lambda _: self._parent_canvas.yview("scroll", 1, "units"))

    def add_event(self, message: str) -> None:
        count = len(self.winfo_children())
        inform_message = ctk.CTkLabel(master=self, text=message)
        inform_message.grid(row=count, column=0, padx=0, pady=0,
                            sticky="nw", columnspan=2)
        self._parent_canvas.yview("scroll", 1, "units")


class GraphicFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, points: list[Point], executor: Executor, count_iteration: int) -> None:
        super().__init__(master=master, fg_color='white', width=640, height=530)
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_propagate(False)
        self._points: list[Point] = points
        self._graphic: Graphic = Graphic(self, self._points)
        self.__create_buttons_frame()
        self._executor = executor
        self._count_iteration = count_iteration

    def __create_buttons_frame(self) -> None:
        self.graphic_buttons_frame = ctk.CTkFrame(master=self, width=100, height=50, fg_color='white')
        self.graphic_buttons_frame.grid(row=1, column=0, pady=0, sticky='nsew')
        self.__create_buttons()

    def __create_buttons(self) -> None:
        prev_image = ctk.CTkImage(Image.open("GeneticAlg/images/prev.png").resize((30, 30)))
        self.prev_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                         width=40, height=40, image=prev_image, text="",
                                         command=self.__handler_prev)
        self.prev_button.grid(row=0, column=1, padx=(5, 0), pady=(10, 5), sticky="nsew")
        forward_image = ctk.CTkImage(Image.open("GeneticAlg/images/forward.png").resize((30, 30)))
        self.forward_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                            width=40, height=40, image=forward_image,
                                            text="", command=self.__handler_forward)
        self.forward_button.grid(row=0, column=2, padx=(5, 0), pady=(10, 5), sticky="nsew")
        next_next_image = ctk.CTkImage(Image.open("GeneticAlg/images/next_next.png").resize((30, 30)))
        self.next_next_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                              width=40, height=40, image=next_next_image,
                                              text="", command=self.__handler_next_next)
        self.next_next_button.grid(row=0, column=3, padx=(5, 0), pady=(10, 5), sticky="nsew")
        reload_image = ctk.CTkImage(Image.open("GeneticAlg/images/reload.png").resize((30, 30)))
        self.reload_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                           width=40, height=40, image=reload_image,
                                           text="", command=self.__handler_reload)
        self.reload_button.grid(row=0, column=0, padx=(220, 0), pady=(10, 5), sticky="nsew")

    def __handler_prev(self) -> None:
        self._graphic.clear_rectangles()
        self._executor.update_solution(-1)
        state = self._executor.get_state()
        if state:
            self._graphic.add_rectangles(state)
            self.master.add_event(str(state))

    def __handler_next_next(self) -> None:
        self._graphic.clear_rectangles()
        num_step = self._count_iteration - (0 if self._executor.get_state() is None else self._executor.get_state().step)
        self._executor.update_solution(num_step)
        state = self._executor.get_state()
        self._graphic.add_rectangles(state)
        self.master.add_event(str(state))

    def __handler_reload(self) -> None:
        self._graphic.clear_rectangles()
        self._executor.restart()
        self.master.add_event("Очистка")

    def __handler_forward(self):
        if self._executor.get_state() is not None and self._count_iteration == self._executor.get_state().step:
            return
        self._graphic.clear_rectangles()
        self._executor.update_solution(1)
        state = self._executor.get_state()
        self._graphic.add_rectangles(state)
        self.master.add_event(str(state))


class StartWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color="#dbdbdb")
        self.geometry('640x950')
        self.title("Установка начальных параметров")
        self.resizable(False, False)
        self._start_params_frame: ctk.CTkFrame = StartParamsFrame(self)
        self._point_frame: ctk.CTkFrame = PointFrame(self)
        self._selection_method_frame: ctk.CTkFrame = SelectionMethodFrame(self)
        self._values_dict = self._start_params_frame.get_value_start_param()
        self._start_work_button: ctk.CTkButton = StartWorkButton(self, points=self._point_frame.get_points(),
                                                                 value_params=self._values_dict,
                                                                 selection_method=self._selection_method_frame)

    def get_point_frame(self) -> ctk.CTkFrame:
        return self._point_frame

    def get_points(self) -> list[Point]:
        return self._point_frame.get_points()

    def get_value_params(self) -> dict[str, float]:
        return self._values_dict

    def restore_data(self, data: StoreData) -> None:
        self._start_work_button.destroy()
        self._point_frame.view_points(data.points, data.point_flag)
        self._point_frame.set_point_flag(data.point_flag)
        self._selection_method_frame.view_base_value_method(data.selection_method)
        self._start_params_frame.set_view_start_param(data.value_params)
        self._start_work_button: ctk.CTkButton = StartWorkButton(self, points=self._point_frame.get_points(),
                                                                 value_params=self._values_dict,
                                                                 selection_method=self._selection_method_frame)


class StartParamsFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master=master, width=320, height=450)
        self.grid(row=0, column=0)
        self._setter_start_params: ctk.CTkFrame = SetterStartParams(self)

    def get_value_start_param(self) -> dict[str, float]:
        return self._setter_start_params.get_value_start_param()

    def set_view_start_param(self, params: dict[str, float]) -> None:
        self._setter_start_params.set_view_start_param(params)


class ViewStartParams(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, fg_color='#808080', height=110, width=290)
        self.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self._state_view_params: dict[str, ctk.CTkLabel] = dict()
        self.__create_view_start_param_label("Шанс мутации: 20%", 0)
        self.__create_view_start_param_label("Шанс cкрещивания: 70%", 1)
        self.__create_view_start_param_label("Шанс увеличения прям. при мутации: 40%", 2)
        self.__create_view_start_param_label("Максимальное количество эпох: 200", 3)
        self.__create_view_start_param_label("Количество индивидов в эпохе: 50", 4)

    def __create_view_start_param_label(self, text: str, index_row: int) -> None:
        view_param_label = ctk.CTkLabel(master=self, width=100, text=text)
        view_param_label.grid(row=index_row, column=0, padx=5, pady=0, sticky='w')
        self._state_view_params[text.split(':')[0]] = view_param_label

    def set_state_view_params(self, name_param: str, text: str) -> None:
        self._state_view_params[name_param].configure(text=text)


class SetterStartParams(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, fg_color='#808080', width=30)
        self.grid(row=0, column=0, padx=40, pady=5, sticky='nsew')
        self._string_value_params: dict[str, ctk.StringVar] = dict()
        self._value_start_params: dict[str, float] = {
            'Шанс мутации': 0.2,
            'Шанс cкрещивания': 0.7,
            'Шанс увеличения прям. при мутации': 0.4,
            'Максимальное количество эпох': 200,
            'Количество индивидов в эпохе': 50
        }
        self._view_start_params = ViewStartParams(master)
        self.__create_set_start_param_label('Шанс мутации', 0)
        self.__create_set_start_param_label('Шанс cкрещивания', 2)
        self.__create_set_start_param_label('Шанс увеличения прям. при мутации', 4)
        self.__create_set_start_param_label('Максимальное количество эпох', 6)
        self.__create_set_start_param_label('Количество индивидов в эпохе', 8)

    def set_view_start_param(self, params: dict[str, float]) -> None:
        for name_param, value in params.items():
            if name_param in ["Шанс мутации", "Шанс cкрещивания", "Шанс увеличения прям. при мутации"]:
                self._view_start_params.set_state_view_params(name_param, f'{name_param}:  {value * 100} %')
                self._value_start_params[name_param] = value
            else:
                self._view_start_params.set_state_view_params(name_param, f'{name_param}:  {int(value)}')
                self._value_start_params[name_param] = int(value)

    def __create_set_start_param_label(self, name_param: str, index_row: int) -> None:
        self._string_value_params[name_param] = ctk.StringVar()
        param_label = ctk.CTkLabel(master=self, text=name_param)
        param_label.grid(row=index_row, column=0, padx=15, pady=3, sticky="we")
        param_entry = ctk.CTkEntry(master=self, textvariable=self._string_value_params[name_param])
        param_entry.grid(row=index_row+1, column=0, padx=10, pady=5, sticky="we")
        param_entry.bind('<Return>', lambda event: self.__handler_entry_start_params(event, name_param))

    def __handler_entry_start_params(self, event, name_param: str) -> None:
        value_param = self._string_value_params[name_param].get()
        try:
            number = float(value_param)
            if name_param in ["Шанс мутации", "Шанс cкрещивания", "Шанс увеличения прям. при мутации"]:
                if 0 <= number <= 1:
                    self._view_start_params.set_state_view_params(name_param, f'{name_param}:  {number * 100} %')
                    self._value_start_params[name_param] = number
            elif 0 <= number:
                self._view_start_params.set_state_view_params(name_param, f'{name_param}:  {int(number)}')
                self._value_start_params[name_param] = int(number)
        except ValueError:
            pass
        finally:
            self._string_value_params[name_param].set("")

    def get_value_start_param(self) -> dict[str, float]:
        return self._value_start_params


class PointFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master=master, height=420, width=320)
        self.grid(row=0, column=1, padx=0, pady=0, sticky='nsew')
        self.grid_propagate(False)
        self._set_point_frame: ctk.CTkFrame = SetterPoint(self)

    def get_points(self) -> list[Point]:
        return self._set_point_frame.get_points()

    def view_points(self, points: list[Point], flag: bool) -> None:
        self._set_point_frame.view_points(points, flag)

    def get_state_point_flag(self) -> bool:
        return self._set_point_frame.get_state_point_flag()

    def set_point_flag(self, flag: bool) -> None:
        self._set_point_frame.set_point_flag(flag)


class SetterPoint(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, fg_color='#dbdbdb')
        self.place(relx=0.5, rely=0.75, anchor='center')
        self._view_points_flag: bool = True
        self._view_pointers: ctk.CTkScrollableFrame = ViewPointers(master)
        self.__create_choose_add_points()

    def get_points(self) -> list[Point]:
        return self._view_pointers.get_points()

    def view_points(self, points: list[Point]) -> None:
        self._view_pointers.view_points(points)

    def get_state_point_flag(self) -> bool:
        return self._view_pointers.get_state_point_flag()

    def view_points(self, points: list[Point], flag: bool) -> None:
        self._view_pointers.view_points(points, flag)

    def set_point_flag(self, flag: bool) -> None:
        if not flag:
            self.switcher_view_points.toggle(flag)

    def __create_choose_add_points(self) -> None:
        self.__create_input_frame_point()
        button_add_point = ctk.CTkButton(master=self, text='Добавить точку',
                                         width=200, command=self.__handler_add_point)
        button_add_point.grid(row=1, column=0, padx=0, pady=5)

        button_add_point_file = ctk.CTkButton(master=self, text='Считать точки из файла',
                                              width=200, command=self.__read_file_point)
        button_add_point_file.grid(row=2, column=0, padx=0, pady=5)

        button_add_point_random = ctk.CTkButton(master=self, text='Случайная генерация',
                                                width=200, command=self.__open_window_randomly)
        button_add_point_random.grid(row=3, column=0, padx=0, pady=5)

        button_all_clear_points = ctk.CTkButton(master=self, text='Удалить все точки',
                                                width=200, command=self.__clear_all_points)
        button_all_clear_points.grid(row=4, column=0, padx=0, pady=5)
        self.switcher_view_points = ctk.CTkSwitch(master=self, text='Не отображать точки',
                                                  fg_color='red', command=self.__switch_event)
        self.switcher_view_points.grid(row=5, column=0, padx=0, pady=5)

    def __switch_event(self) -> None:
        if self.switcher_view_points.get():
            self._view_pointers.set_view_point_flag(False)
        else:
            self._view_pointers.set_view_point_flag(True)

    def __clear_all_points(self):
        self._view_pointers.get_points().clear()
        for label, button in self._view_pointers.get_points_clear():
            button.destroy()
            label.destroy()

    def __open_window_randomly(self) -> None:
        self.generate_random_window = ctk.CTkToplevel(self)
        self.generate_random_window.title("Введите диапазон")
        self.generate_random_window.geometry("250x300")

        label_random = ctk.CTkLabel(self.generate_random_window, text="Введите диапазон значений генерации")
        label_random.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.range_random_from = ctk.CTkEntry(self.generate_random_window)
        self.range_random_from.grid(row=1, column=0, padx=10, pady=10, sticky='we')

        self.range_random_before = ctk.CTkEntry(self.generate_random_window)
        self.range_random_before.grid(row=2, column=0, padx=10, pady=10, sticky='we')

        label_count = ctk.CTkLabel(self.generate_random_window, text="Введите количество точек")
        label_count.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        self.range_random_count = ctk.CTkEntry(self.generate_random_window)
        self.range_random_count.grid(row=4, column=0, padx=10, pady=10, sticky='we')

        submit_button = ctk.CTkButton(self.generate_random_window, text="Подтвердить",
                                      command=self.__random_generate_points)
        submit_button.grid(row=5, column=0, padx=10, pady=10, sticky='we')

    def __random_generate_points(self):
        random_from = self.range_random_from.get()
        random_before = self.range_random_before.get()
        random_count = self.range_random_count.get()
        try:
            random_from = int(random_from)
            random_before = int(random_before)
            random_count = int(random_count)
            self.generate_random_window.destroy()
            for i in range(random_count):
                x = random.randint(min(random_from, random_before), max(random_from, random_before))
                y = random.randint(min(random_from, random_before), max(random_from, random_before))
                value = random.randint(0, 1)
                point = Point(x, y, value)
                self._view_pointers.create_point(point)
        except ValueError:
            pass

    def __read_file_point(self) -> None:
        file_path = filedialog.askopenfilename(title="Выберите файл",
                                               filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        with open(file_path, newline='', encoding='utf-8') as file:
            file_reader = csv.reader(file, delimiter=',')
            for x, y, value, *empty in file_reader:
                try:
                    point = Point(int(x), int(y), int(value))
                    self._view_pointers.create_point(point)
                except ValueError:
                    pass

    def __handler_add_point(self) -> None:
        x = self.x_string.get()
        y = self.y_string.get()
        value = self.value_string.get()
        try:
            point = Point(int(x), int(y), int(value))
            self._view_pointers.create_point(point)
            if int(value) in [0, 1]:
                self.x_string.set('')
                self.y_string.set('')
                self.value_string.set('')
        except ValueError:
            pass

    def __create_input_frame_point(self) -> None:
        input_frame = ctk.CTkFrame(master=self)
        input_frame.grid(row=0, column=0, padx=0, pady=0)
        self.x_string = ctk.StringVar()
        self.y_string = ctk.StringVar()
        self.value_string = ctk.StringVar()
        x_label = ctk.CTkLabel(master=input_frame, text="X")
        x_label.grid(row=0, column=0, padx=5, pady=0, sticky='nw')
        x_enter = ctk.CTkEntry(master=input_frame, width=50, textvariable=self.x_string)
        x_enter.grid(row=0, column=1, padx=0, pady=0, sticky='nw')
        y_label = ctk.CTkLabel(master=input_frame, text="Y")
        y_label.grid(row=0, column=2, padx=5, pady=0, sticky='nw')
        y_enter = ctk.CTkEntry(master=input_frame, width=50, textvariable=self.y_string)
        y_enter.grid(row=0, column=3, padx=0, pady=0, sticky='nw')
        value_label = ctk.CTkLabel(master=input_frame, text="Значение")
        value_label.grid(row=0, column=4, padx=5, pady=0, sticky='nw')
        value_enter = ctk.CTkEntry(master=input_frame, width=50, textvariable=self.value_string)
        value_enter.grid(row=0, column=5, padx=0, pady=0, sticky='nw')


class ViewPointers(ctk.CTkScrollableFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, width=250, height=200)
        self.place(relx=0.5, rely=0.25, anchor='center')
        self._points: list[Point] = list()
        self._view_point_flag: bool = True
        self._set_points_clear: [ctk.CTkLabel, ctk.CTkButton] = list()
        self.bind("<Button-4>", lambda _: self._parent_canvas.yview("scroll", -1, "units"))
        self.bind("<Button-5>", lambda _: self._parent_canvas.yview("scroll", 1, "units"))

    def set_view_point_flag(self, value: bool) -> None:
        self._view_point_flag = value

    def get_state_point_flag(self) -> bool:
        return self._view_point_flag

    def create_point(self, point: Point) -> None:
        if point.mark in [0, 1]:
            row_index = len(self._points)
            self._points.append(point)
            if self._view_point_flag:
                text_label = ctk.CTkLabel(master=self, text=f'X: {point.x}, Y: {point.y}, VALUE: {point.mark}')
                text_label.grid(row=row_index, column=0, padx=5, pady=3)
                trash_image = ctk.CTkImage(Image.open("GeneticAlg/images/trash.png").resize((25, 25)))
                point_button_delete = ctk.CTkButton(master=self, width=45, text="", image=trash_image,
                                                    command=lambda: self.__delete_point(point,
                                                                                        text_label,
                                                                                        point_button_delete))
                point_button_delete.grid(row=row_index, column=1, padx=(40, 0), pady=5, sticky='e')
                self._set_points_clear.append((text_label, point_button_delete))

    def view_points(self, points: list[Point], flag: bool) -> None:
        self._points = points
        counter = 0
        for point in points:
            if flag:
                text_label = ctk.CTkLabel(master=self, text=f'X: {point.x}, Y: {point.y}, VALUE: {point.mark}')
                text_label.grid(row=counter, column=0, padx=5, pady=3)
                trash_image = ctk.CTkImage(Image.open("GeneticAlg/images/trash.png").resize((25, 25)))
                point_button_delete = ctk.CTkButton(master=self, width=45, text="", image=trash_image,
                                                    command=lambda: self.__delete_point(point,
                                                                                        text_label,
                                                                                        point_button_delete))
                point_button_delete.grid(row=counter, column=1, padx=(40, 0), pady=5, sticky='e')
                self._set_points_clear.append((text_label, point_button_delete))
                counter += 1

    def __delete_point(self, point: Point, label: ctk.CTkLabel, button: ctk.CTkButton) -> None:
        self._points.remove(point)
        label.destroy()
        button.destroy()

    def get_points(self) -> list[Point]:
        return self._points

    def get_points_clear(self) -> list[Point]:
        return self._set_points_clear


class SelectionMethodFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master=master, width=640, height=280)
        self.grid(row=1, column=0, rowspan=2, columnspan=2, padx=0, pady=0)
        self.grid_propagate(False)
        self._selection_values: list[str] = [
            'Отсечение',
            'Рулетка',
            'Турнир',
            'Элита'
        ]
        self._selection_method: ctk.CTkFrame = ChooseMethodFrame(self, row=0, column=0,
                                                                 name_method='Выберите метод отбора',
                                                                 values=self._selection_values,
                                                                 base_value='Отсечение')

    def get_value_method(self) -> dict[Func, ...]:
        return self._selection_method.get_value_method()

    def view_base_value_method(self, method: str) -> None:
        self._selection_method.view_base_value_method(method)


class ChooseMethodFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame, row: int, column: int, name_method: str,
                 values: list[str], base_value: str) -> None:
        super().__init__(master=master, height=140, width=320, fg_color='#dbdbdb')
        self.grid(row=row, column=column, padx=0, pady=0)
        self.grid_propagate(False)
        self._name_method: str = name_method
        self._values: list[str] = values
        self._value_method: str = base_value
        self.__create_name_label()
        self.__create_choose_frame()

    def view_base_value_method(self, method: str) -> None:
        self._value_method = method
        help_dict = {
            truncation_selection: "Отсечение",
            roulette_selection: 'Рулетка',
            tournament_selection: 'Турнир',
            elite_selection: 'Элита'
        }
        self.choose_method_selection.set(help_dict[method])

    def __create_name_label(self) -> ctk.CTkLabel:
        border_frame = ctk.CTkFrame(master=self, border_width=4, border_color='black', width=300, height=100)
        border_frame.place(relx=0.5, rely=0.25, anchor='center')
        name_label = ctk.CTkLabel(master=border_frame, text=self._name_method, font=("Arial", 20))
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    def __create_choose_frame(self):
        self.choose_method_selection = ctk.CTkOptionMenu(master=self, width=250, height=50, values=self._values,
                                                    command=self.__handler_method_selection)
        self.choose_method_selection.place(relx=0.5, rely=0.75, anchor='center')
        self.choose_method_selection.grid_propagate(False)

    def __handler_method_selection(self, choice):
        self._value_method = choice

    def get_value_method(self) -> str:
        help_dict = {
            "Отсечение": truncation_selection,
            'Рулетка': roulette_selection,
            'Турнир': tournament_selection,
            'Элита': elite_selection
        }
        if isinstance(self._value_method, str):
            return help_dict[self._value_method]
        return self._value_method

class ErrorMessage:
    def __init__(self, message: str) -> None:
        messagebox.showerror("Ошибка", message)


class StartWorkButton(ctk.CTkButton):
    def __init__(self, master: ctk.CTk, points: list[Point],
                 value_params: dict[str, float], selection_method: ...) -> None:
        super().__init__(master=master, text="Начать работу", width=400, height=70,
                         fg_color='#228B22',
                         hover_color='#008000',
                         command=self.__handler_start_work)
        self._points: list[Point] = points
        self.master = master
        self._value_params: dict[str, float] = value_params
        self._selection_method: ... = selection_method
        self.grid(row=3, column=0, rowspan=2, columnspan=2, padx=0, pady=30)

        self._value_methods: dict[Func, ...] = {
            Func.Fitness: fitness,
            Func.Crossing: crossing,
            Func.Mutation: mutation_random_point
        }
        self._param_mutation = ParamMutation(value_params['Шанс увеличения прям. при мутации'],
                                             1 - value_params['Шанс увеличения прям. при мутации'])
        self._param_probability = ParamProbability(crossing=value_params['Шанс cкрещивания'],
                                                   mutation=value_params['Шанс мутации'],
                                                   param_mutation=self._param_mutation)
        self._param_fitness = ParamFitness(4, 5)
        self._param_genetic_algorithm = ParamGeneticAlgorithm(probability=self._param_probability,
                                                              fitness=self._param_fitness,
                                                              num_individuals=int(value_params['Количество индивидов в эпохе']))

    def __handler_start_work(self):
        if len(self._points) == 0:
            ErrorMessage("Создайте хотя бы одну точку!")
        else:
            self.master.destroy()
            self._first_generation: list[RectangleInfo] = first_generation(self._value_methods, self._points,
                                                                           int(self._value_params['Количество индивидов в эпохе']))

            self._executor = Executor(next_generation=self._selection_method.get_value_method(), func=self._value_methods, points=self._points,
                                  first_generation=self._first_generation,
                                  param=self._param_genetic_algorithm, value_param=self._value_params,
                                      point_flag=self.master.get_point_frame().get_state_point_flag())
            MainWindow(points=self._points, executor=self._executor,
                       count_iteration=self._value_params['Максимальное количество эпох']).mainloop()


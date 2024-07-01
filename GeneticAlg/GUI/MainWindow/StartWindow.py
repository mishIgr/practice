from StdClass.StdClass import Point
import csv
from tkinter import filedialog
import random
import customtkinter as ctk
from PIL import Image
from MainWindow import *


class StartWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color="#dbdbdb")
        self.geometry('640x850')
        self.title("Установка начальных параметров")
        self.resizable(False, False)
        self._start_params_frame: ctk.CTkFrame = StartParamsFrame(self)
        self._point_frame: ctk.CTkFrame = PointFrame(self)
        self._methods_alg_frame: ctk.CTkFrame = MethodsAlgFrame(self)
        self._values_dict = self._start_params_frame.get_value_start_param()
        self._start_work_button: ctk.CTkButton = StartWorkButton(self, points=self._point_frame.get_points(),
                                                                 value_params=self._values_dict)

    def get_points(self) -> set[Point]:
        return self._point_frame.get_points()

    def get_value_params(self) -> dict[str, float]:
        return self._values_dict

    def get_method_selection(self) -> str:
        return self._methods_alg_frame.get_value_selection()

    def get_method_crossing(self) -> str:
        return self._methods_alg_frame.get_value_crossing()

    def get_method_mutation(self) -> str:
        return self._methods_alg_frame.get_value_mutation()


class StartParamsFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master=master, width=320, height=450)
        self.grid(row=0, column=0)
        self.grid_propagate(False)
        self._setter_start_params: ctk.CTkFrame = SetterStartParams(self)

    def get_value_start_param(self) -> dict[str, float]:
        return self._setter_start_params.get_value_start_param()


class ViewStartParams(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, fg_color='#808080', height=110, width=290)
        self.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_propagate(False)
        self._state_view_params: dict[str, ctk.CTkLabel] = dict()
        self.__create_view_start_param_label("Шанс мутации: error", 0)
        self.__create_view_start_param_label("Шанс cкрещивания: error", 1)
        self.__create_view_start_param_label("Шанс увеличения прям. при мутации: error", 2)
        self.__create_view_start_param_label("Максимальное количество эпох: error", 3)

    def __create_view_start_param_label(self, text, index_row) -> None:
        view_param_label = ctk.CTkLabel(master=self, width=100, text=text)
        view_param_label.grid(row=index_row, column=0, padx=5, pady=0, sticky='w')
        self._state_view_params[text[:-7]] = view_param_label

    def set_state_view_params(self, name_param: str, text: str) -> None:
        self._state_view_params[name_param].configure(text=text)


class SetterStartParams(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, fg_color='#808080', width=30)
        self.grid(row=0, column=0, padx=40, pady=5, sticky='nsew')
        self._string_value_params: dict[str, ctk.StringVar] = dict()
        self._value_start_params: dict[str, float] = dict()
        self._view_start_params = ViewStartParams(master)
        self.__create_set_start_param_label('Шанс мутации', 0)
        self.__create_set_start_param_label('Шанс cкрещивания', 2)
        self.__create_set_start_param_label('Шанс увеличения прям. при мутации', 4)
        self.__create_set_start_param_label('Максимальное количество эпох', 6)

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
                self._view_start_params.set_state_view_params(name_param, f'{name_param}:  {number}')
                self._value_start_params[name_param] = number
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

    def get_points(self) -> set[Point]:
        return self._set_point_frame.get_points()


class SetterPoint(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master=master, fg_color='#dbdbdb')
        self.place(relx=0.5, rely=0.75, anchor='center')
        self._view_points_flag: bool = True
        self._view_pointers: ctk.CTkScrollableFrame = ViewPointers(master)
        self.__create_choose_add_points()

    def get_points(self) -> set[Point]:
        return self._view_pointers.get_points()

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
                                                  fg_color='red', command=self._switch_event)
        self.switcher_view_points.grid(row=5, column=0, padx=0, pady=5)

    def _switch_event(self) -> None:
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
        self._points: set[Point] = set()
        self._view_point_flag: bool = True
        self._set_points_clear: [ctk.CTkLabel, ctk.CTkButton] = set()
        self.bind("<Button-4>", lambda _: self._parent_canvas.yview("scroll", -1, "units"))
        self.bind("<Button-5>", lambda _: self._parent_canvas.yview("scroll", 1, "units"))

    def set_view_point_flag(self, value: bool) -> None:
        self._view_point_flag = value

    def create_point(self, point: Point) -> None:
        if point not in self._points and point.mark in [0, 1]:
            row_index = len(self._points)
            self._points.add(point)
            if self._view_point_flag:
                text_label = ctk.CTkLabel(master=self, text=f'X: {point.x}, Y: {point.y}, VALUE: {point.mark}')
                text_label.grid(row=row_index, column=0, padx=5, pady=3)
                trash_image = ctk.CTkImage(Image.open("../images/trash.png").resize((25, 25)))
                point_button_delete = ctk.CTkButton(master=self, width=45, text="", image=trash_image,
                                                    command=lambda: self.__delete_point(point,
                                                                                        text_label,
                                                                                        point_button_delete))
                point_button_delete.grid(row=row_index, column=1, padx=(40, 0), pady=5, sticky='e')
                self._set_points_clear.add((text_label, point_button_delete))

    def __delete_point(self, point: Point, label: ctk.CTkLabel, button: ctk.CTkButton) -> None:
        self._points.remove(point)
        label.destroy()
        button.destroy()

    def get_points(self) -> set[Point]:
        return self._points

    def get_points_clear(self) -> set[Point]:
        return self._set_points_clear


class MethodsAlgFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master=master, width=640, height=280)
        self.grid(row=1, column=0, rowspan=2, columnspan=2, padx=0, pady=0)
        self.grid_propagate(False)
        self._selection_values: list[str] = [
            'Правило рулетки',
            'Стохастическая универсальная выборка',
            'Ранжированный отбор',
            'Масштабирование приспособленности',
            'Турнирный отбор']
        self._crossing_values: list[str] = [
            'Одноточечное скрещивание',
            'Двухточечное скрещивание',
            'Равномерное скрещивание',
            'Упорядоченное скрещивание',
            'Скрещивание смешением',
            'Имитация двоичного скрещивания'
        ]
        self._mutation_values: list[str] = [
            'Инвертирование бита',
            'Мутация обменом',
            'Мутация обращением',
            'Мутация перетасовкой',
            'Вещественная мутация'
        ]
        self._selection_method: ctk.CTkFrame = ChooseMethodFrame(self, row=0, column=0,
                                                                 name_method='Выберите метод отбора',
                                                                 values=self._selection_values,
                                                                 base_value=self._selection_values[0])
        self._crossing_method: ctk.CTkFrame = ChooseMethodFrame(self, row=0, column=1,
                                                                name_method='Выберите метод скрещивания',
                                                                values=self._crossing_values,
                                                                base_value=self._crossing_values[0])
        self._mutation_method: ctk.CTkFrame = ChooseMethodFrame(self, row=1, column=0,
                                                                name_method='Выберите метод мутации',
                                                                values=self._mutation_values,
                                                                base_value=self._mutation_values[0])

    def get_value_selection(self) -> str:
        return self._selection_method.get_value_method()

    def get_value_crossing(self) -> str:
        return self._crossing_method.get_value_method()

    def get_value_mutation(self) -> str:
        return self._mutation_method.get_value_method()


class ChooseMethodFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame, row, column, name_method, values, base_value) -> None:
        super().__init__(master=master, height=140, width=320, fg_color='#dbdbdb')
        self.grid(row=row, column=column, padx=0, pady=0)
        self.grid_propagate(False)
        self._name_method: str = name_method
        self._values: list[str] = values
        self._value_method: str = base_value
        self.__create_name_label()
        self.__create_choose_frame()

    def __create_name_label(self) -> ctk.CTkLabel:
        border_frame = ctk.CTkFrame(master=self, border_width=4, border_color='black', width=300, height=100)
        border_frame.place(relx=0.5, rely=0.25, anchor='center')
        name_label = ctk.CTkLabel(master=border_frame, text=self._name_method, font=("Arial", 20))
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    def __create_choose_frame(self):
        choose_method_selection = ctk.CTkOptionMenu(master=self, width=250, height=50, values=self._values,
                                                    command=self.__handler_method_selection)
        choose_method_selection.place(relx=0.5, rely=0.75, anchor='center')
        choose_method_selection.grid_propagate(False)

    def __handler_method_selection(self, choice):
        self._value_method = choice

    def get_value_method(self) -> str:
        return self._value_method


class ErrorMessage(ctk.CTk):
    def __init__(self, text: str):
        super().__init__(fg_color='red')
        self._window_width = 470
        self._window_height = 100
        self.resizable(False, False)
        self.__setup_window()
        self.__add_widgets(text)
        self.after(1000, self.__fade_out)

    def __fade_out(self) -> None:
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.05
            self.attributes("-alpha", alpha)
            self.after(50, self.__fade_out)
        else:
            self.destroy()

    def __setup_window(self):
        position_x = self.winfo_screenwidth() - self._window_width
        position_y = self.winfo_screenheight() - self._window_height - 100
        self.geometry(f"{self._window_width}x{self._window_height}+{position_x}+{position_y}")
        self.title("Error")

    def __add_widgets(self, text: str):
        text_label = ctk.CTkLabel(self, text=text, font=("Arial", 20), bg_color="transparent")
        text_label.place(relx=0.5, rely=0.5, anchor='center')


class StartWorkButton(ctk.CTkButton):
    def __init__(self, master: ctk.CTk, points: list[Point], value_params: dict[str, float]) -> None:
        super().__init__(master=master, text="Начать работу", width=400, height=70,
                         fg_color='#228B22',
                         hover_color='#008000',
                         command=self.__handler_start_work)
        self._points: set[Point] = points
        self._value_params: dict[str, float] = value_params
        self.grid(row=3, column=0, rowspan=2, columnspan=2, padx=0, pady=30)

    def __handler_start_work(self):
        # print(a.get_value_params())
        print(a.get_points())
        # print(f'Метод отбора: {a.get_method_selection()}')
        # print(f'Метод скрещивания: {a.get_method_crossing()}')
        # print(f'Метод мутации: {a.get_method_mutation()}')
        if len(self._points) == 0:
            ErrorMessage("Создайте хотя бы одну точку!").mainloop()
        elif 'Шанс мутации' not in self._value_params:
            ErrorMessage("Установите вероятность мутации!").mainloop()
        elif 'Шанс cкрещивания' not in self._value_params:
            ErrorMessage("Установите вероятность cкрещивания!").mainloop()
        elif 'Шанс увеличения прям. при мутации' not in self._value_params:
            ErrorMessage("Установите шанс увеличения прям. при мутации!").mainloop()
        elif 'Максимальное количество эпох' not in self._value_params:
            ErrorMessage("Установите максимальное количество эпох!").mainloop()

        window = MainWindow()
        window.mainloop()


a = StartWindow()
a.mainloop()


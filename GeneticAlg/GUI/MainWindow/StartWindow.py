from StdClass.StdClass import Point
import csv
from tkinter import filedialog
import random
import matplotlib.pyplot as plt
import customtkinter as ctk
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class StartWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry('640x1000')
        self.title("Установка начальных параметров")
        self.grid_propagate(False)
        self.resizable(False, False)
        self._start_params_frame: ctk.CTkFrame = StartParamsFrame(self)


class StartParamsFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master=master, width=330, height=450, fg_color='green')
        self.grid(row=0, column=0)
        self.grid_propagate(False)
        self._setter_start_params: ctk.CTkFrame = SetterStartParams(self)


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
            else:
                if 0 <= number:
                    self._view_start_params.set_state_view_params(name_param, f'{name_param}:  {number}')
                    self._value_start_params[name_param] = number
        except ValueError:
            pass
        finally:
            self._string_value_params[name_param].set("")


a = StartWindow()
a.mainloop()
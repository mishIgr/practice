import matplotlib.pyplot as plt
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import random
from PIL import Image, ImageTk
from executor import *

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
    def __init__(self, master: ctk.CTk, points: set[Point]):
        self._points: set[Point] = points
        self.figure, self.ax = plt.subplots(figsize=(6, 5.6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().pack()
        ZoomPan().pan_factory(self.ax)
        ZoomPan().zoom_factory(self.ax, base_scale=1.1)
        self.x_lim_max, self.x_lim_min, self.y_lim_max, self.y_lim_min = self.__get_size()
        self.ax.set_xlim(self.x_lim_min, self.x_lim_max)
        self.ax.set_ylim(self.y_lim_min, self.y_lim_max)
        self._plot_points: set[Point] = points
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
    def __init__(self, points: set[Point], executor: Executor) -> None:
        super().__init__(fg_color="white")
        self.geometry('1055x530')
        self.title("Генетический алгоритм")
        self.resizable(False, False)
        self._graphic_frame: ctk.CTkFrame = GraphicFrame(self, points, executor)
        self._info_table_frame: ctk.CTkFrame = InfoTableFrame(self)

    def add_event(self, event: str) -> None:
        self._info_table_frame.add_event(event)


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
        inform_message = ctk.CTkLabel(master=self, text="#log " + str(count + 1) + ": " + message)
        inform_message.grid(row=count, column=0, padx=0, pady=0,
                            sticky="nw", columnspan=2)
        self._parent_canvas.yview("scroll", 1, "units")


class GraphicFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, points: set[Point], executor: Executor) -> None:
        super().__init__(master=master, fg_color='white', width=640, height=530)
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_propagate(False)
        self._points: set[Point] = points
        self._graphic: Graphic = Graphic(self, self._points)
        self.__create_buttons_frame()

    def __create_buttons_frame(self) -> None:
        self.graphic_buttons_frame = ctk.CTkFrame(master=self, width=100, height=50, fg_color='white')
        self.graphic_buttons_frame.grid(row=1, column=0, pady=0, sticky='nsew')
        self.__create_buttons()

    def __create_buttons(self) -> None:
        prev_image = ctk.CTkImage(Image.open("images/prev.png").resize((30, 30)))
        self.prev_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                         width=40, height=40, image=prev_image, text="")
        self.prev_button.grid(row=0, column=1, padx=(5, 0), pady=(10, 5), sticky="nsew")
        forward_image = ctk.CTkImage(Image.open("images/forward.png").resize((30, 30)))
        self.forward_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                            width=40, height=40, image=forward_image,
                                            text="", command=self.__handler_forward)
        self.forward_button.grid(row=0, column=2, padx=(5, 0), pady=(10, 5), sticky="nsew")
        next_next_image = ctk.CTkImage(Image.open("images/next_next.png").resize((30, 30)))
        self.next_next_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                              width=40, height=40, image=next_next_image,
                                              text="")
        self.next_next_button.grid(row=0, column=3, padx=(5, 0), pady=(10, 5), sticky="nsew")
        reload_image = ctk.CTkImage(Image.open("images/reload.png").resize((30, 30)))
        self.reload_button = ctk.CTkButton(master=self.graphic_buttons_frame,
                                           width=40, height=40, image=reload_image,
                                           text="", command=self.__handler_reload)
        self.reload_button.grid(row=0, column=0, padx=(220, 0), pady=(10, 5), sticky="nsew")

    def __handler_reload(self) -> None:
        self._graphic.clear_rectangles()
        self.master.add_event("Очистка")

    def __handler_forward(self):
        self._graphic.clear_rectangles()
        self._graphic.add_rectangle(random.randint(0, 50), random.randint(0, 50),
                                    random.randint(1, 50), random.randint(1, 50), 'green')
        self._graphic.add_rectangle(random.randint(0, 50), random.randint(0, 50),
                                    random.randint(1, 50), random.randint(1, 50), 'yellow')
        self._graphic.add_rectangle(random.randint(0, 50), random.randint(0, 50),
                                    random.randint(1, 50), random.randint(1, 50), 'blue')
        self.master.add_event("Следующий шаг алгоритма")
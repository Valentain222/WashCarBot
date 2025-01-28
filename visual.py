import matplotlib.pyplot as plt

from data_management import FillingContainer

import os

import random
import math


class VisualMethods:

    def __spawn_colours(self, quantity: int, mode: str) -> list:

        """
        :param quantity: quantity return colours
        :param mode: shade return colours
        :return: colours in RGB/255
        """

        color_base = {
            'middle': [(180, 0, 0), (0, 204, 204), (204, 132, 0), (255, 204, 0), 2],
            'cold': [(255, 0, 0), (0, 150, 0), (0, 0, 255), (0, 255, 255), (200, 200, 0), 1],
            'warm': [(205, 3, 3), (3, 150, 28), (205, 125, 3),(205, 205, 3), (3, 120, 205),
                    (120, 94, 188), (204, 153, 255), 0],
            'standard': [(255, 0, 0), (0, 255, 0), 2]
        }

        colours = color_base.get(mode, False)
        if colours is False:
            raise ValueError("Wrong mode. Choose from 'middle', 'cold', 'warm', or 'dark'.")

        colours_set = set(colours[:-1])

        if quantity > len(colours_set)-1:
            while quantity > len(colours_set):

                random_color_original = random.choice(colours[:-1])
                random_color = random_color_original[:]

                random_color[colours[-1]] += random.choice(range(0, 240))

                colours_set.add(tuple(random_color))

        colours = list(colours_set)[0:quantity]
        random.shuffle(colours)

        colours = [[c/255 for c in color] for color in colours]

        return colours

    def __spawn_title(self, plot: plt.axes, graph_name, min_size=13.5):

        bbox = plot.get_window_extent()
        sq = bbox.width * bbox.height / 120

        bbox = dict(facecolor='black', edgecolor='blue', boxstyle='round,pad=0.3', linewidth=0.6)
        plot.set_title(graph_name, color='white', bbox=bbox, fontsize=min(17, max(sq * 0.009, min_size)))

    def __revers_colour_graph(self, plot: plt.axes, graph_name, x_name=None, y_name=None):
        self.__spawn_title(plot, graph_name)
        if x_name is not None:
            plot.set_xlabel(x_name, color='white')
        if y_name is not None:
            plot.set_ylabel(y_name, color='white')

        plot.tick_params(axis='both', which='both', colors='white')

        plot.spines['bottom'].set_color('#D3D3D3')
        plot.spines['left'].set_color('#D3D3D3')

    def __spawn_spines(self, names_spin: list, plot: plt.axes, c, lw, points: list, position: list):

        for index, name in enumerate(names_spin):
            plot.spines[name].set_visible(True)
            plot.spines[name].set_linewidth(lw)
            plot.spines[name].set_color(c)

            plot.spines[name].set_bounds(points[index][0], points[index][1])
            plot.spines[name].set_position(('axes', position[index]))

    def __string2list(self, max_len, strings):

        strings_text = []
        str_split = strings.split()

        string = ''
        for element in str_split:
            if len(string) + len(element) - 1 >= max_len:
                strings_text.append(string.strip())
                string = f'{element} '
            else:
                string += f'{element} '

        strings_text.append(string.strip())

        return strings_text

    def __len_text(self, plot, txt):

        renderer = plot.figure.canvas.get_renderer()

        text_extent = txt.get_window_extent(renderer)
        text_width_px = text_extent.width
        text_height_px = text_extent.height

        ax_extent = plot.get_window_extent()
        ax_width_px = ax_extent.width
        ax_height_px = ax_extent.height

        text_width = text_width_px / ax_width_px
        text_height = text_height_px / ax_height_px

        return [text_width, text_height]

    def __sort_with_label(self, data: tuple, label: tuple):

        paired = list(zip(data, label))
        sorted_pairs = sorted(paired, key=lambda x: x[0])

        return zip(*sorted_pairs)

    def __legend(self, plot: plt.axes, labels: tuple):

        legend = plot.legend(labels=labels, bbox_to_anchor=(1, 1.1), framealpha=0.3)

        plot.grid(axis='both', linestyle='--', alpha=0.7, color='gray')
        plt.setp(legend.get_texts(), color='white')

    def _get_subplots_adjust(self, layout):

        parameters = {
            '2': (0.952, 0.039, 0.032, 0.992, 0.211, 0.119),
            '3': (0.923, 0.059, 0.048, 0.932, 0.261, 0.193),
            '4': (0.922, 0.059, 0.028, 0.962, 0.183, 0.119),
            '5': (0.927, 0.059, 0.032, 0.986, 0.376, 0.21),
            '6': (0.961, 0.059, 0.035, 0.953, 0.339, 0.073),
            '7': (0.927, 0.059, 0.032, 0.929, 0.574, 0.225)
        }

        return parameters.get(str(layout), False)

    def spawn_axs(self, num_gr: int, capacity: int) -> list:

        """
        :param num_gr: number of required graphs
        :param capacity: capacity of graphs on one figure
        :return: axes in list
        """

        axes = []
        for i in range(0, num_gr, capacity):

            graph_on_figure = min(num_gr, capacity)
            half = math.ceil(graph_on_figure * 0.5)

            row = 1 if half < 2 else 2
            col = 2 if half == 1 else half

            fig = plt.figure(figsize=(19.2, 9.83), facecolor='black')  # row*16 col*10

            for j in range(graph_on_figure):

                index = j + 1
                if j == graph_on_figure-1:
                    index = (index, graph_on_figure + 1)

                ax = fig.add_subplot(col, row, index)
                ax.set_facecolor('black')

                axes.append(ax)

            num_gr -= capacity
        return axes

    def spawn_table(self, plot: plt.axes, bbox: tuple, table_data: tuple, table_size: tuple, colours: list = None):

        """
        :param plot: ax
        :param bbox: coordinates of table
        :param table_data: data in table
        :param colours: colours
        :param table_size: width coloumn in table
        :return: None
        """

        table = plot.table(cellText=table_data, bbox=bbox, cellLoc='center', colWidths=table_size)

        for key, cell in table.get_celld().items():

            cell.set_fontsize(50)
            cell.set_text_props(fontweight='semibold')

            cell.set_linewidth(1.7)
            cell.set_edgecolor('#D3D3D3')

            if key[1] == 0:
                if colours is not None:
                    cell.set_facecolor(colours[key[0]])
                    continue

            cell.set_facecolor('black')
            cell.set_text_props(color='white')

    def line_graph(self, plot: plt.axes, data: tuple, settings: tuple, legends: tuple):

        """
        :param plot: ax
        :param data: data for graph (((x,y)),)
        :param settings: name_graph, x_name, y_name, lindewith_graph
        :param legends: labels for plot ()
        :return: None
        """

        colours = self.__spawn_colours(len(data), 'cold')

        for d, c in zip(data, colours):
            plot.plot(d[0], d[1], color=c, marker='.', linewidth=settings[3])

        self.__revers_colour_graph(plot, settings[0], settings[1], settings[2])

        self.__legend(plot, legends)

    def pie_graph(self, plot: plt.axes, data: tuple, settings: tuple):

        """
        :param plot: ax
        :param data: data pie []
        :param settings: (name_graph, (labels), annotate_table)
        :return: None
        """

        colours = self.__spawn_colours(len(data), 'warm')

        sort_data, sort_labels = self.__sort_with_label(data, settings[1])

        table_data = [[' ', f'{l}', f'{round(sort_data[i] / sum(sort_data) * 100, 1)}%', f'{sort_data[i]}{settings[2]}']
                      for i, l in enumerate(sort_labels)]

        plot.pie(sort_data, colors=colours,
                 wedgeprops={'linewidth': 2, 'edgecolor': 'black', 'center': (1.922, -0.1)}, startangle=90, radius=1.28,
                 hatch='/')
        self.spawn_table(plot, (-0.71, -0.09, 1.45, 1.07), tuple(table_data), table_size=(0.05, 0.5, 0.2, 0.2),
                         colours=colours)

        self.__spawn_title(plot, settings[0])

    def bar_graph(self, plot: plt.axes, data: tuple, setting: tuple):

        """
        :param plot: ax
        :param data: data bar
        :param setting: ((labels), (name_graph, y_name))
        :return: None
        """

        data, label = self.__sort_with_label(data, setting[0])

        len_group, _ = min((2, math.modf(len(data) / 2)[0]), (3, math.modf(len(data) / 3)[0]), key=lambda x: x[1])

        colours = self.__spawn_colours(len_group, 'middle')

        data = [data[i:i + len_group] for i in range(0, len(data), len_group)]

        width = 0.15
        distant = 0.2
        position = [x * width for x in range(len_group)]
        positions = []

        for i, data_chunk in enumerate(data):

            bars = plot.bar(position[:len(data_chunk)], data_chunk, color=colours, width=0.15, zorder=2, hatch='/')

            for j, x in enumerate(position[:len(data_chunk)]):
                positions.append(x)
                position[j] = x + distant + len_group * width

            for bar in bars:
                bar_center = bar.get_x() + width / 2
                bar_height = bar.get_height()

                plot.text(bar_center, bar_height, str(bar.get_height()),
                          ha='center', va='bottom', color='white')

        plot.set_xticks(positions, label)
        plot.grid(axis='y', linestyle='--', alpha=0.7, color='gray')
        self.__revers_colour_graph(plot, setting[1][0], y_name=setting[1][1])

    def text(self, plot: plt.axes, data: str, x: float = 0, y: float = 0.97, spines=True):

        """
        :param plot: ax
        :param data: data in str 'aoaoaoaoaoaoa...'
        :param x: up right symbol in float
        :param y: up right symbol in float
        :param spines: spawn or not spines
        :return: y
        """

        standard_sq = 328872.6259653244

        bbox = plot.get_window_extent()
        sq = bbox.width * bbox.height

        letter_size = max(min(17, 16 * sq / standard_sq), 14)
        y = min(y, 0.97)

        max_len_string = bbox.width / letter_size + 22

        c = 'white'
        step = 0.08
        paragraph = 0.01

        strings_text = self.__string2list(max_len_string, data)

        first_letter = strings_text[0][0]
        strings_text[0] = strings_text[0][1:]

        txt = plot.text(x + paragraph, y, first_letter, fontsize=letter_size + 5, color=c, fontweight='bold',
                        fontfamily='Comic Sans MS')
        first_letter_width, first_letter_height = self.__len_text(plot, txt)

        if strings_text[0][1] == ' ':
            paragraph += 0.015
        plot.text(x + paragraph + first_letter_width, y, strings_text[0], fontsize=letter_size, color=c,
                  fontfamily='Georgia')

        if spines:
            indent_x = x - 0.6 * first_letter_width
            indent_y = y + first_letter_height * 0.95

            len_top = len(sorted(strings_text, key=len, reverse=True)[0]) * first_letter_width * 0.63

            self.__spawn_spines(['left', 'top'], plot, '#D3D3D3', 2, [[0, indent_y], [indent_x, len_top]],
                                [indent_x, indent_y])

        for s in strings_text[1:]:
            plot.text(x, y := y - step, s, fontsize=letter_size, color=c, fontfamily='Georgia')

        return y

    def hist_graph(self, plot: plt.axes, data: tuple, settings: tuple, label: tuple):

        """
        :param plot: ax
        :param data: data in ()
        :param settings: name_graph, x_name, y_name
        :param label: data for legend ()
        :return: None
        """

        color = self.__spawn_colours(1, 'middle')

        plot.hist(data, bins='auto', color=color, alpha=0.9, edgecolor='black', hatch='x')

        self.__revers_colour_graph(plot, settings[0], settings[1], settings[2])
        self.__legend(plot, label)

    def point_graph(self, plot: plt.axes, data: tuple, settings: tuple, legend: tuple):

        """
        :param plot: ax
        :param data: data in (((x),(y)),)
        :param settings: name_graph, x_name, y_name
        :param legend: legends_data (labels)
        :return: None
        """

        colours = self.__spawn_colours(len(data), 'standard')
        for d, c in zip(data, colours):
            plot.scatter(d[0], d[1], s=9, color=c, marker='s', zorder=6)

        self.__legend(plot, legend)
        self.__revers_colour_graph(plot, settings[0], settings[1], settings[2])


class Visual(VisualMethods):

    def set_settings(self, settings: FillingContainer):
        pass

    def __open_graphs(self) -> tuple[str, ...]:
        return tuple(os.path.join('plots/', name) for name in os.listdir('plots/'))

    def generate_plots(self, func_name='', time_range='', name_car_wash='', capacity=1) -> tuple[str, ...]:
        return self.__open_graphs()
        # name_graphs = ''
        #
        # axes = self.spawn_axs(int(func_name.split('.')[-1]), capacity)
        #
        # top, bottom, left, right, hspace, wspace = self._get_subplots_adjust(4)
        # plt.subplots_adjust(top=top,
        #                     bottom=bottom,
        #                     left=left,
        #                     right=right,
        #                     hspace=hspace,
        #                     wspace=wspace)
        #
        # if func_name.split('.')[0] == 'services':
        #     self.services(None, axes)

    def services(self, datas, axes: list[plt.axes]):
        pass


visual = Visual()
visual.generate_plots('services.6', 0, 5, 6)

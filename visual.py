import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class InteractiveGraph:
    def __init__(self, G, pos=None):
        self.G = G
        self.pos = pos if pos is not None else nx.spring_layout(G, k=1, iterations=50)
        self.selected_node = None
        self.dragging = False
        self.fig, self.ax = plt.subplots(figsize=(18, 14))  # Увеличил размер для полных названий

        # Создаем список узлов для быстрого доступа
        self.nodes_list = list(self.G.nodes())

        self.setup_graph()
        self.connect_events()

    def format_node_name(self, name):
        """Форматирует название узла: сокращает 'Главный станционный путь' до 'ГСП'"""
        if not name:
            return ""

        # Заменяем "Главный станционный путь" на "ГСП"
        formatted_name = name.replace("Главный станционный путь", "ГСП")

        return formatted_name

    def get_node_color(self, node):
        """Возвращает цвет узла в зависимости от его типа"""
        node_type = self.G.nodes[node].get('type', '')
        if node == self.selected_node:
            return 'red'  # Выделенный узел
        elif 'MAIN_STATION' in node_type:
            return 'lightblue'
        elif 'PARKING' in node_type:
            return 'lightgreen'
        elif 'EXIT' in node_type:
            return 'lightcoral'
        else:
            return 'gray'

    def get_node_size(self, node):
        """Возвращает размер узла в зависимости от его типа"""
        node_type = self.G.nodes[node].get('type', '')
        if node == self.selected_node:
            return 600  # Увеличенный размер для выделенного узла
        elif 'MAIN_STATION' in node_type:
            return 450
        elif 'PARKING' in node_type:
            return 300
        elif 'EXIT' in node_type:
            return 350
        else:
            return 250

    def setup_graph(self):
        self.ax.clear()

        # Подготавливаем данные для отрисовки
        node_colors = [self.get_node_color(node) for node in self.nodes_list]
        node_sizes = [self.get_node_size(node) for node in self.nodes_list]

        # Создаем полные подписи с форматированием
        labels = {}
        for node in self.G.nodes():
            name = self.G.nodes[node].get('name', '')
            formatted_name = self.format_node_name(name)
            labels[node] = formatted_name if formatted_name else node[:8]

        # Рисуем граф
        nx.draw_networkx_edges(self.G, self.pos, ax=self.ax,
                               edge_color='gray', arrows=True,
                               arrowsize=20, alpha=0.7, width=1.5)

        nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax,
                               node_color=node_colors,
                               node_size=node_sizes, alpha=0.9,
                               edgecolors='black', linewidths=1.5)

        # Рисуем подписи с увеличенным шрифтом для лучшей читаемости
        nx.draw_networkx_labels(self.G, self.pos, ax=self.ax,
                                labels=labels, font_size=9,
                                font_weight='bold',
                                font_family='DejaVu Sans')  # Используем шрифт с поддержкой кириллицы

        # Информация о выбранном узле
        if self.selected_node:
            node_info = self.G.nodes[self.selected_node]
            full_name = node_info.get('name', 'Unknown')
            formatted_name = self.format_node_name(full_name)
            info_text = f"Выбран: {formatted_name}\nТип: {node_info.get('type', 'Unknown')}\nID: {self.selected_node[:8]}..."
            self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                         fontsize=11, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

        self.ax.set_title(
            "🚂 Интерактивная железнодорожная сеть\n🖱️ Перетаскивайте узлы | R - сброс позиций | ESC - отмена выделения",
            size=14, pad=20)
        self.ax.axis('off')

        # Легенда
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue',
                       markersize=12, label='Станции (ГСП)', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen',
                       markersize=10, label='Указатели парковки', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral',
                       markersize=11, label='Выходы/Тупики', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
                       markersize=14, label='Выбранный узел', markeredgecolor='black')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right',
                       framealpha=0.9, fontsize=11)

    def connect_events(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_press(self, event):
        if event.inaxes != self.ax:
            return

        # Ищем узел под курсором
        closest_node = None
        min_distance = float('inf')

        for node in self.G.nodes():
            x, y = self.pos[node]
            distance = ((x - event.xdata) ** 2 + (y - event.ydata) ** 2) ** 0.5
            if distance < 0.05 and distance < min_distance:  # увеличенный радиус захвата
                min_distance = distance
                closest_node = node

        if closest_node:
            self.selected_node = closest_node
            self.dragging = True
            self.redraw()

    def on_motion(self, event):
        if self.dragging and self.selected_node and event.inaxes == self.ax:
            # Обновляем позицию узла
            self.pos[self.selected_node] = [event.xdata, event.ydata]
            self.redraw()

    def on_release(self, event):
        self.dragging = False
        # Узел остается выделенным после отпускания
        self.redraw()

    def on_key(self, event):
        # Сброс позиций по нажатию 'r'
        if event.key == 'r':
            self.pos = nx.spring_layout(self.G, k=1.2, iterations=100)  # Увеличил k для большего расстояния
            self.selected_node = None  # Сбрасываем выделение
            self.redraw()
        # Отмена выделения по нажатию ESC
        elif event.key == 'escape':
            self.selected_node = None
            self.redraw()

    def redraw(self):
        self.setup_graph()
        self.fig.canvas.draw()

    def show(self):
        plt.tight_layout()
        plt.show()


# Загрузка данных и создание графа
print("Загрузка данных...")
nodes_df = pd.read_csv('nodes_202510210940.csv')
links_df = pd.read_csv('links.csv')

print(f"Узлов: {len(nodes_df)}")
print(f"Связей: {len(links_df)}")

# Создаем граф
G = nx.DiGraph()

# Добавляем узлы с атрибутами
for _, node in nodes_df.iterrows():
    G.add_node(node['id'], name=node['name'], type=node['type'])

# Добавляем связи
added_edges = 0
for _, link in links_df.iterrows():
    if link['start_node'] in G.nodes and link['finish_node'] in G.nodes:
        G.add_edge(link['start_node'], link['finish_node'])
        added_edges += 1

print(f"Добавлено связей в граф: {added_edges}")

# Анализ графа
print(f"\nХарактеристики графа:")
print(f"- Узлов: {G.number_of_nodes()}")
print(f"- Связей: {G.number_of_edges()}")
print(f"- Типы узлов:")
node_types = {}
for node in G.nodes():
    node_type = G.nodes[node].get('type', 'Unknown')
    node_types[node_type] = node_types.get(node_type, 0) + 1

for typ, count in node_types.items():
    print(f"  {typ}: {count}")

# Показываем примеры форматированных названий
print(f"\nПримеры форматированных названий:")
sample_nodes = list(G.nodes())[:5]
for node in sample_nodes:
    original_name = G.nodes[node].get('name', '')
    formatted_name = InteractiveGraph(G).format_node_name(original_name)
    print(f"  '{original_name}' -> '{formatted_name}'")

# Запуск интерактивного графа
print("\nЗапуск интерактивного графа...")
print("Инструкции:")
print("🖱️  ЛКМ - выбрать и перетащить узел")
print("⌨️  R - сбросить позиции всех узлов")
print("⌨️  ESC - отменить выделение узла")
print("\nВсе названия узлов отображаются полностью с заменой 'Главный станционный путь' на 'ГСП'")

interactive_graph = InteractiveGraph(G)
interactive_graph.show()
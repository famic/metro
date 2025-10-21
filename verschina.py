import pandas as pd
import networkx as nx
from tabulate import tabulate

# Загрузка данных
nodes_df = pd.read_csv('nodes_202510210940.csv')
links_df = pd.read_csv('links.csv')

# Создаем граф
G = nx.DiGraph()

# Добавляем узлы с атрибутами
for _, node in nodes_df.iterrows():
    G.add_node(node['id'], name=node['name'], type=node['type'])

# Добавляем связи
for _, link in links_df.iterrows():
    if link['start_node'] in G.nodes and link['finish_node'] in G.nodes:
        G.add_edge(link['start_node'], link['finish_node'],
                   link_type=link.get('type', 'UNKNOWN'),
                   link_id=link['id'])


# Функция для форматирования названия узла
def format_node_name(name):
    return name.replace("Главный станционный путь", "ГСП")


print("=" * 120)
print("ТАБЛИЦА ВЕРШИН ГРАФА И ИХ РЕБЕР")
print("=" * 120)

# Создаем основную таблицу вершин
vertices_data = []
for node in G.nodes():
    node_name = G.nodes[node].get('name', 'Unknown')
    node_type = G.nodes[node].get('type', 'Unknown')
    formatted_name = format_node_name(node_name)

    # Считаем степени
    in_degree = G.in_degree(node)
    out_degree = G.out_degree(node)
    total_degree = in_degree + out_degree

    vertices_data.append({
        'Вершина': formatted_name,
        'Тип': node_type,
        'ID': node[:12] + '...',
        'Входящие': in_degree,
        'Исходящие': out_degree,
        'Всего связей': total_degree
    })

# Создаем DataFrame для вершин
vertices_df = pd.DataFrame(vertices_data)

# Выводим таблицу вершин
print("\n📊 ТАБЛИЦА ВЕРШИН ГРАФА:")
print(tabulate(vertices_df, headers='keys', tablefmt='grid', showindex=True))
print(f"\nВсего вершин: {len(vertices_df)}")

# Создаем детальную таблицу связей
print("\n" + "=" * 120)
print("ДЕТАЛЬНАЯ ТАБЛИЦА СВЯЗЕЙ")
print("=" * 120)

connections_data = []
for node in G.nodes():
    node_name = G.nodes[node].get('name', 'Unknown')
    formatted_name = format_node_name(node_name)

    # Исходящие связи
    for _, target, data in G.out_edges(node, data=True):
        target_name = format_node_name(G.nodes[target].get('name', 'Unknown'))
        link_type = data.get('link_type', 'UNKNOWN')

        connections_data.append({
            'Тип связи': 'Исходящая →',
            'От вершины': formatted_name,
            'К вершине': target_name,
            'Тип связи': link_type,
            'ID начала': node[:8] + '...',
            'ID конца': target[:8] + '...'
        })

    # Входящие связи
    for source, _, data in G.in_edges(node, data=True):
        source_name = format_node_name(G.nodes[source].get('name', 'Unknown'))
        link_type = data.get('link_type', 'UNKNOWN')

        connections_data.append({
            'Тип связи': 'Входящая ←',
            'От вершины': source_name,
            'К вершине': formatted_name,
            'Тип связи': link_type,
            'ID начала': source[:8] + '...',
            'ID конца': node[:8] + '...'
        })

# Создаем DataFrame для связей
if connections_data:
    connections_df = pd.DataFrame(connections_data)
    print("\n🔗 ТАБЛИЦА ВСЕХ СВЯЗЕЙ:")
    print(tabulate(connections_df, headers='keys', tablefmt='grid', showindex=False))
    print(f"\nВсего связей: {len(connections_df)}")
else:
    print("Нет связей в графе")

# Группировка по типам вершин
print("\n" + "=" * 120)
print("СТАТИСТИКА ПО ТИПАМ ВЕРШИН")
print("=" * 120)

type_stats = vertices_df.groupby('Тип').agg({
    'Вершина': 'count',
    'Входящие': 'sum',
    'Исходящие': 'sum',
    'Всего связей': 'sum'
}).rename(columns={'Вершина': 'Количество вершин'}).reset_index()

type_stats['Средняя степень'] = (type_stats['Всего связей'] / type_stats['Количество вершин']).round(2)

print(tabulate(type_stats, headers='keys', tablefmt='grid', showindex=False))

# Таблица самых связанных вершин
print("\n" + "=" * 120)
print("ТОП-10 САМЫХ СВЯЗАННЫХ ВЕРШИН")
print("=" * 120)

top_vertices = vertices_df.nlargest(10, 'Всего связей')[['Вершина', 'Тип', 'Входящие', 'Исходящие', 'Всего связей']]
print(tabulate(top_vertices, headers='keys', tablefmt='grid', showindex=True))

# Таблица вершин без связей
print("\n" + "=" * 120)
print("ВЕРШИНЫ БЕЗ СВЯЗЕЙ")
print("=" * 120)

isolated_vertices = vertices_df[vertices_df['Всего связей'] == 0][['Вершина', 'Тип']]
if not isolated_vertices.empty:
    print(tabulate(isolated_vertices, headers='keys', tablefmt='grid', showindex=True))
    print(f"\nВершин без связей: {len(isolated_vertices)}")
else:
    print("Нет вершин без связей")

# Детальная таблица для конкретных вершин (пример)
print("\n" + "=" * 120)
print("ПРИМЕР ДЕТАЛЬНОЙ ТАБЛИЦЫ ДЛЯ ВЕРШИН СВЯЗЕЙ")
print("=" * 120)

# Берем первые 5 вершин для примера детального отображения
sample_nodes = list(G.nodes())
detailed_data = []

for node in sample_nodes:
    node_name = format_node_name(G.nodes[node].get('name', 'Unknown'))
    node_type = G.nodes[node].get('type', 'Unknown')

    # Исходящие связи
    out_edges = list(G.out_edges(node, data=True))
    for _, target, data in out_edges:
        target_name = format_node_name(G.nodes[target].get('name', 'Unknown'))
        detailed_data.append({
            'Вершина': node_name,
            'Тип вершины': node_type,
            'Направление': '→ ИСХОДЯЩАЯ',
            'Связана с': target_name,
            'Тип связи': data.get('link_type', 'UNKNOWN')
        })

    # Входящие связи
    in_edges = list(G.in_edges(node, data=True))
    for source, _, data in in_edges:
        source_name = format_node_name(G.nodes[source].get('name', 'Unknown'))
        detailed_data.append({
            'Вершина': node_name,
            'Тип вершины': node_type,
            'Направление': '← ВХОДЯЩАЯ',
            'Связана с': source_name,
            'Тип связи': data.get('link_type', 'UNKNOWN')
        })

if detailed_data:
    detailed_df = pd.DataFrame(detailed_data)
    print(f"\nДетальные связи для первых {len(sample_nodes)} вершин:")
    print(tabulate(detailed_df, headers='keys', tablefmt='grid', showindex=False))
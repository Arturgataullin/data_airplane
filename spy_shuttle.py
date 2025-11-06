import pandas as pd
import networkx as nx
from tqdm import tqdm

df = pd.read_csv('mrgd.csv', sep=';', low_memory=False)
df = df.dropna(subset=['From', 'Dest'])
def build_personal_graph(personal_df):
    G = nx.DiGraph()
    for _, row in personal_df.iterrows():
        from_city = row['From']  # или row['from']
        to_city = row['Dest']
        if(from_city != to_city):
            if not G.has_node(from_city):
                G.add_node(from_city)
            if not G.has_node(to_city):
                G.add_node(to_city)
            if G.has_edge(from_city, to_city):
                G[from_city][to_city]['weight'] += 1
            else:
                G.add_edge(from_city, to_city, weight=1)
    return G

def analyze_structural_patterns(G):
    for city_a, city_b in G.edges():
        if G.has_edge(city_b, city_a):
            weight_ab = G[city_a][city_b]['weight']
            weight_ba = G[city_b][city_a]['weight']

            # Челночный маршрут: много рейсов в обе стороны
            shuttle_count = weight_ab + weight_ba
            if shuttle_count >= 6:  # хотя бы 2 челночных поездки
                shuttle_routes.append({
                    'FirstName': first,
                    'LastName': last,
                    'city_a': city_a,
                    'city_b': city_b,
                    'shuttle_count': shuttle_count,
                })
    if shuttle_routes: return True

shuttle_routes = []
for(first, last), person_df in tqdm(df.groupby(['FirstName', 'LastName'])):
    if len(person_df) < 3:
        continue
    personal_graph = build_personal_graph(person_df)
    analyze_structural_patterns(personal_graph)
results_df = pd.DataFrame(shuttle_routes)
results_df.to_csv('shuttle_people.csv', sep=';', index=False)

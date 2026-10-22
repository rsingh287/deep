try:
    import networkx as nx
except ImportError:
    nx = None

class DEEPPropertyGraph:
    def __init__(self):
        print("[Property Graph] Initializing Hyper-Relational OS Graph...")
        if nx:
            self.graph = nx.DiGraph()
            self.active = True
        else:
            self.active = False
            print("[Property Graph] networkx not installed. Operating in disabled mode.")

    def map_workspace(self):
        if not self.active: return
        print("[Property Graph] Mapping causal links across the D.E.E.P. workspace...")
        # Conceptual mapping of the local digital life
        self.graph.add_edge("app.py", "db_engine.py", relation="IMPORTS")
        self.graph.add_edge("db_engine.py", "PostgreSQL", relation="WRITES_TO")
        self.graph.add_edge("swarm_orchestrator.py", "app.py", relation="IMPORTED_BY")

    def query_impact(self, target_node):
        if not self.active: return []
        print(f"[Property Graph] Traversing causal graph for impact of deleting: {target_node}")
        if target_node in self.graph:
            return list(nx.dfs_successors(self.graph, target_node))
        return []

property_graph = None

def get_property_graph():
    global property_graph
    if property_graph is None:
        property_graph = DEEPPropertyGraph()
    return property_graph

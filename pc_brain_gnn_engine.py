import os
import ast
import networkx as nx

def generate_dynamic_pc_brain_gnn():
    """Dynamically scans the workspace to build an interconnected Property Graph."""
    G = nx.DiGraph()
    workspace_dir = os.path.abspath(os.path.dirname(__file__))
    
    # 1. Scan files
    files_scanned = 0
    for root, dirs, files in os.walk(workspace_dir):
        if '__pycache__' in root or '.git' in root or 'venv' in root:
            continue
        for file in files:
            if file.endswith('.py') or file.endswith('.c') or file.endswith('.html') or file.endswith('.h'):
                files_scanned += 1
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, workspace_dir)
                G.add_node(rel_path, type='file')
                
                # If python, parse AST to find dependencies
                if file.endswith('.py'):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for n in node.names:
                                    G.add_edge(rel_path, n.name, relation='imports')
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    G.add_edge(rel_path, node.module, relation='imports')
                    except Exception:
                        pass

    # 2. Add fixed nodes (DB, Kasa, etc.)
    G.add_node("PostgreSQL", type='database')
    G.add_node("Kasa Smart Plug", type='hardware')
    G.add_node("Webcam", type='hardware')
    G.add_node("Microcontroller", type='hardware')

    # Convert to Mermaid
    mermaid_lines = ["```mermaid", "graph TD"]
    
    # Limit to 50 nodes for mermaid to not crash
    top_nodes = [n for n, d in sorted(G.degree(), key=lambda x: x[1], reverse=True)[:50]]
    sub_G = G.subgraph(top_nodes)
    
    for u, d in sub_G.nodes(data=True):
        clean_u = str(u).replace('.py', '').replace('\\\\', '_').replace('/', '_').replace('.', '_')
        label = str(u).split('\\\\')[-1].split('/')[-1]
        mermaid_lines.append(f'    {clean_u}["{label}"]')
        
    for u, v, d in sub_G.edges(data=True):
        clean_u = str(u).replace('.py', '').replace('\\\\', '_').replace('/', '_').replace('.', '_')
        clean_v = str(v).replace('.py', '').replace('\\\\', '_').replace('/', '_').replace('.', '_')
        mermaid_lines.append(f'    {clean_u} -->|{d.get("relation", "connects")}| {clean_v}')
        
    mermaid_lines.append("```")
    mermaid_graph = "\\n".join(mermaid_lines)

    report = f"""🕸️ **Dynamic Graph RAG — PC Workstation Graph**

# 🧠 Graph Topology: `PC AI Brain Network`

### 📊 Graph Neural Network Metrics:
- **Total Files Scanned:** `{files_scanned}`
- **Total Graph Nodes ($N$):** `{G.number_of_nodes()}`
- **Total Graph Edges ($E$):** `{G.number_of_edges()}`
- **Primary Hubs:** `{', '.join([str(n) for n, d in sorted(G.degree(), key=lambda x: x[1], reverse=True)[:3]])}`

---

### 🕸️ Interactive Visual Knowledge Graph (Top 50 Nodes):

{mermaid_graph}

---
✅ **Dynamic Graph Updated!** Ask any systemic impact question to traverse relations.
"""
    return report

if __name__ == "__main__":
    print(generate_dynamic_pc_brain_gnn())

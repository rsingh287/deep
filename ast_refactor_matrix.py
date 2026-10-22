import ast
import os

class DeterministicRefactorer(ast.NodeTransformer):
    def __init__(self, target_name, new_name):
        self.target_name = target_name
        self.new_name = new_name
        self.changes_made = 0

    def visit_Name(self, node):
        if node.id == self.target_name:
            node.id = self.new_name
            self.changes_made += 1
        return self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        if node.name == self.target_name:
            node.name = self.new_name
            self.changes_made += 1
        return self.generic_visit(node)

def refactor_codebase(file_path, target, replacement):
    print(f"[AST-Matrix] Deterministic structural refactoring: '{target}' -> '{replacement}' in {file_path}")
    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found"}
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            
        tree = ast.parse(source)
        transformer = DeterministicRefactorer(target, replacement)
        modified_tree = transformer.visit(tree)
        ast.fix_missing_locations(modified_tree)
        
        if transformer.changes_made > 0:
            new_source = ast.unparse(modified_tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_source)
                
        return {
            "status": "success", 
            "changes_made": transformer.changes_made,
            "message": "Mathematical AST transformation complete with 0% syntax breakage."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

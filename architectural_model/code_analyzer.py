import ast
import libcst as cst
import networkx as nx
from typing import List, Dict, Any, Optional
import graphviz

class CodeAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.ast_tree = ast.parse(code)
        self.cst_tree = cst.parse_module(code)
        self.components = []
        self.relationships = []

    def analyze(self) -> Dict[str, Any]:
        """Basic code analysis to extract components and relationships"""
        self._extract_classes()
        self._extract_functions()
        self._extract_imports()
        return {
            "components": self.components,
            "relationships": self.relationships
        }

    def _extract_classes(self):
        """Extract class definitions from the code"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "type": "class",
                    "name": node.name,
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    "bases": [base.id for base in node.bases if isinstance(base, ast.Name)]
                }
                self.components.append(class_info)

    def _extract_functions(self):
        """Extract function definitions from the code"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                function_info = {
                    "type": "function",
                    "name": node.name,
                    "parameters": [arg.arg for arg in node.args.args]
                }
                self.components.append(function_info)

    def _extract_imports(self):
        """Extract import statements and create relationships"""
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.relationships.append({
                        "type": "import",
                        "source": name.name,
                        "target": "external"
                    })

class UMLGenerator:
    def __init__(self, analysis_result: Dict[str, Any]):
        self.analysis = analysis_result
        self.graph = nx.DiGraph()

    def generate_class_diagram(self) -> str:
        """Generate UML class diagram in DOT format"""
        dot = graphviz.Digraph('UML Class Diagram')
        dot.attr(rankdir='TB')

        # Add classes
        for component in self.analysis["components"]:
            if component["type"] == "class":
                class_label = f"{component['name']}"
                if component["methods"]:
                    class_label += "|" + "\\n".join(component["methods"])
                dot.node(component["name"], label=class_label, shape='record')

        # Add inheritance relationships
        for component in self.analysis["components"]:
            if component["type"] == "class" and component["bases"]:
                for base in component["bases"]:
                    dot.edge(base, component["name"], arrowhead='empty')

        return dot.source

class FourPlusOneViewGenerator:
    def __init__(self, analysis_result: Dict[str, Any]):
        self.analysis = analysis_result

    def generate_views(self) -> Dict[str, Any]:
        """Generate 4+1 view model"""
        return {
            "logical_view": self._generate_logical_view(),
            "process_view": self._generate_process_view(),
            "development_view": self._generate_development_view(),
            "physical_view": self._generate_physical_view(),
            "scenarios": self._generate_scenarios()
        }

    def _generate_logical_view(self) -> Dict[str, Any]:
        """Generate logical view showing key abstractions"""
        return {
            "components": [c for c in self.analysis["components"] if c["type"] == "class"],
            "relationships": [r for r in self.analysis["relationships"] if r["type"] == "inheritance"]
        }

    def _generate_process_view(self) -> Dict[str, Any]:
        """Generate process view showing runtime behavior"""
        return {
            "processes": [c for c in self.analysis["components"] if c["type"] == "function"],
            "interactions": self.analysis["relationships"]
        }

    def _generate_development_view(self) -> Dict[str, Any]:
        """Generate development view showing static organization"""
        return {
            "modules": self.analysis["components"],
            "dependencies": self.analysis["relationships"]
        }

    def _generate_physical_view(self) -> Dict[str, Any]:
        """Generate physical view showing system topology"""
        return {
            "nodes": ["Server", "Client"],
            "connections": self.analysis["relationships"]
        }

    def _generate_scenarios(self) -> List[Dict[str, Any]]:
        """Generate use case scenarios"""
        return [
            {
                "name": "System Operation",
                "description": "Basic system operation flow",
                "components": self.analysis["components"]
            }
        ]

class ADLGenerator:
    def __init__(self, analysis_result: Dict[str, Any]):
        self.analysis = analysis_result

    def generate_adl(self) -> str:
        """Generate Architecture Description Language representation"""
        adl = "architecture SoftwareSystem {\n"
        
        # Add components
        adl += "  components {\n"
        for component in self.analysis["components"]:
            if component["type"] == "class":
                adl += f"    component {component['name']} {{\n"
                adl += f"      type: {component['type']}\n"
                adl += f"      methods: {', '.join(component['methods'])}\n"
                adl += "    }\n"
        adl += "  }\n"

        # Add connectors
        adl += "  connectors {\n"
        for relationship in self.analysis["relationships"]:
            adl += f"    connector {relationship['source']}_to_{relationship['target']} {{\n"
            adl += f"      type: {relationship['type']}\n"
            adl += f"      source: {relationship['source']}\n"
            adl += f"      target: {relationship['target']}\n"
            adl += "    }\n"
        adl += "  }\n"

        adl += "}\n"
        return adl 
"""
Code Scanner Tool
Analyzes Python files to extract functions, classes, and testable components
"""

from claude_agent_sdk import tool
import ast
import json
import os
from pathlib import Path
from typing import List, Dict, Any


class CodeAnalyzer:
    """Analyze Python code to extract testable components"""

    def __init__(self):
        self.results = {
            "functions": [],
            "classes": [],
            "imports": [],
            "constants": [],
            "errors": []
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            return self._extract_components(tree, file_path)

        except SyntaxError as e:
            return {
                "file": file_path,
                "error": f"Syntax error: {str(e)}"
            }
        except Exception as e:
            return {
                "file": file_path,
                "error": f"Error analyzing file: {str(e)}"
            }

    def _extract_components(self, tree: ast.AST, file_path: str) -> Dict[str, Any]:
        """Extract all testable components from AST"""
        result = {
            "file": file_path,
            "module_docstring": ast.get_docstring(tree),
            "functions": [],
            "classes": [],
            "imports": [],
            "constants": []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions (unless testing them is useful)
                func_info = self._analyze_function(node)
                result["functions"].append(func_info)

            elif isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node)
                result["classes"].append(class_info)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append({
                        "name": alias.name,
                        "alias": alias.asname
                    })

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result["imports"].append({
                        "from": module,
                        "name": alias.name,
                        "alias": alias.asname
                    })

            elif isinstance(node, ast.Assign):
                # Module-level constants (UPPERCASE names)
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        result["constants"].append({
                            "name": target.id,
                            "line": node.lineno
                        })

        return result

    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze a function node"""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "docstring": ast.get_docstring(node),
            "parameters": [],
            "returns": None,
            "decorators": [],
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "is_private": node.name.startswith('_'),
            "complexity": self._estimate_complexity(node)
        }

        # Extract parameters
        for arg in node.args.args:
            param = {
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation)
            }
            func_info["parameters"].append(param)

        # Extract return type
        if node.returns:
            func_info["returns"] = self._get_annotation(node.returns)

        # Extract decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                func_info["decorators"].append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                func_info["decorators"].append(decorator.func.id)

        return func_info

    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class node"""
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "docstring": ast.get_docstring(node),
            "methods": [],
            "properties": [],
            "base_classes": [],
            "is_private": node.name.startswith('_')
        }

        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info["base_classes"].append(base.id)

        # Extract methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._analyze_function(item)
                method_info["is_staticmethod"] = any(d == "staticmethod" for d in method_info["decorators"])
                method_info["is_classmethod"] = any(d == "classmethod" for d in method_info["decorators"])
                method_info["is_property"] = any(d == "property" for d in method_info["decorators"])

                if method_info["is_property"]:
                    class_info["properties"].append(method_info)
                else:
                    class_info["methods"].append(method_info)

        return class_info

    def _get_annotation(self, annotation) -> str:
        """Extract type annotation as string"""
        if annotation is None:
            return None

        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            # Handle List[str], Dict[str, int], etc.
            return ast.unparse(annotation)
        else:
            return ast.unparse(annotation)

    def _estimate_complexity(self, node: ast.FunctionDef) -> int:
        """Estimate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


@tool(
    "scan_codebase",
    "Scan Python files to extract testable components (functions, classes, methods)",
    {
        "path": str,  # File path or directory path
        "recursive": bool,  # Scan subdirectories (default True)
        "exclude_patterns": list  # Patterns to exclude (e.g., ["test_*", "__pycache__"])
    }
)
async def scan_codebase(args):
    """
    Scan Python codebase and extract all testable components
    """
    path = args["path"]
    recursive = args.get("recursive", True)
    exclude_patterns = args.get("exclude_patterns", ["test_*", "__pycache__", "*.pyc", ".git"])

    analyzer = CodeAnalyzer()
    results = []

    # Determine if path is file or directory
    path_obj = Path(path)

    if not path_obj.exists():
        return {
            "content": [{
                "type": "text",
                "text": f"Error: Path does not exist: {path}"
            }]
        }

    # Collect Python files
    python_files = []

    if path_obj.is_file():
        if path_obj.suffix == '.py':
            python_files.append(path_obj)
    else:
        # Directory
        if recursive:
            python_files = list(path_obj.rglob("*.py"))
        else:
            python_files = list(path_obj.glob("*.py"))

    # Filter out excluded patterns
    python_files = [
        f for f in python_files
        if not any(f.match(pattern) for pattern in exclude_patterns)
    ]

    # Analyze each file
    for file_path in python_files:
        result = analyzer.analyze_file(str(file_path))
        results.append(result)

    # Generate summary
    total_functions = sum(len(r.get("functions", [])) for r in results if "error" not in r)
    total_classes = sum(len(r.get("classes", [])) for r in results if "error" not in r)
    total_methods = sum(
        len(c.get("methods", []))
        for r in results if "error" not in r
        for c in r.get("classes", [])
    )

    summary = {
        "scanned_files": len(python_files),
        "total_functions": total_functions,
        "total_classes": total_classes,
        "total_methods": total_methods,
        "files": results,
        "recommendations": _generate_test_recommendations(results)
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(summary, indent=2)
        }]
    }


@tool(
    "analyze_function",
    "Deep analysis of a specific function for test generation",
    {
        "file_path": str,
        "function_name": str
    }
)
async def analyze_function(args):
    """
    Perform deep analysis of a specific function
    """
    file_path = args["file_path"]
    function_name = args["function_name"]

    analyzer = CodeAnalyzer()
    file_result = analyzer.analyze_file(file_path)

    if "error" in file_result:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(file_result, indent=2)
            }]
        }

    # Find the function
    target_function = None
    for func in file_result.get("functions", []):
        if func["name"] == function_name:
            target_function = func
            break

    # Check in classes
    if not target_function:
        for cls in file_result.get("classes", []):
            for method in cls.get("methods", []):
                if method["name"] == function_name:
                    target_function = method
                    target_function["class_name"] = cls["name"]
                    break
            if target_function:
                break

    if not target_function:
        return {
            "content": [{
                "type": "text",
                "text": f"Function '{function_name}' not found in {file_path}"
            }]
        }

    # Enhanced analysis
    analysis = {
        "function": target_function,
        "test_strategy": _generate_function_test_strategy(target_function),
        "edge_cases": _identify_edge_cases(target_function),
        "mocking_needs": _identify_mocking_needs(file_result, target_function)
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(analysis, indent=2)
        }]
    }


def _generate_test_recommendations(results: List[Dict]) -> List[str]:
    """Generate testing recommendations based on scan results"""
    recommendations = []

    total_functions = sum(len(r.get("functions", [])) for r in results if "error" not in r)
    total_classes = sum(len(r.get("classes", [])) for r in results if "error" not in r)

    if total_functions > 0:
        recommendations.append(f"Generate unit tests for {total_functions} functions")

    if total_classes > 0:
        recommendations.append(f"Generate class tests for {total_classes} classes")

    # Check for high complexity functions
    complex_functions = []
    for result in results:
        if "error" in result:
            continue
        for func in result.get("functions", []):
            if func.get("complexity", 0) > 5:
                complex_functions.append((result["file"], func["name"], func["complexity"]))

    if complex_functions:
        recommendations.append(
            f"Prioritize testing {len(complex_functions)} high-complexity functions (complexity > 5)"
        )

    return recommendations


def _generate_function_test_strategy(func_info: Dict) -> Dict:
    """Generate test strategy for a function"""
    strategy = {
        "test_count_estimate": 3,  # Base: happy path, edge case, error case
        "priority": "medium",
        "test_types": []
    }

    # Adjust based on complexity
    complexity = func_info.get("complexity", 1)
    if complexity > 5:
        strategy["priority"] = "high"
        strategy["test_count_estimate"] += complexity - 5

    # Determine test types needed
    if func_info.get("parameters"):
        strategy["test_types"].append("parametrized_tests")

    if func_info.get("is_async"):
        strategy["test_types"].append("async_tests")

    if "fixture" in func_info.get("decorators", []):
        strategy["test_types"].append("fixture_tests")

    return strategy


def _identify_edge_cases(func_info: Dict) -> List[str]:
    """Identify potential edge cases for a function"""
    edge_cases = []

    # Check parameters
    for param in func_info.get("parameters", []):
        param_type = param.get("annotation")

        if param_type in ["str", "Optional[str]"]:
            edge_cases.extend(["empty string", "None value", "very long string", "unicode characters"])
        elif param_type in ["int", "float"]:
            edge_cases.extend(["zero", "negative", "very large number"])
        elif param_type in ["list", "List"]:
            edge_cases.extend(["empty list", "single element", "None"])
        elif param_type in ["dict", "Dict"]:
            edge_cases.extend(["empty dict", "missing keys", "None"])

    # Generic edge cases
    if func_info.get("parameters"):
        edge_cases.append("all parameters None")

    return list(set(edge_cases))  # Remove duplicates


def _identify_mocking_needs(file_result: Dict, func_info: Dict) -> List[str]:
    """Identify what needs to be mocked for testing"""
    mocking_needs = []

    # Check imports for external dependencies
    imports = file_result.get("imports", [])

    for imp in imports:
        module_name = imp.get("from") or imp.get("name")

        if any(keyword in module_name for keyword in ["requests", "http", "api"]):
            mocking_needs.append(f"Mock API calls ({module_name})")

        elif any(keyword in module_name for keyword in ["sqlite", "postgres", "mysql", "database"]):
            mocking_needs.append(f"Mock database ({module_name})")

        elif "open" in func_info.get("name", "").lower():
            mocking_needs.append("Mock file operations")

        elif any(keyword in module_name for keyword in ["datetime", "time"]):
            mocking_needs.append(f"Mock time/date ({module_name})")

    return mocking_needs

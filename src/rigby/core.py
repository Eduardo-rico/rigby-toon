import ast
import sys
import os
from typing import Optional

# --- Rigby Personality Logging ---
# Uses stderr so stdout stays clean for piping (e.g., > context.toon)

def log_start(path: str):
    sys.stderr.write(f"Ugh, fine. Scanning {path}... Don't make me work too hard.\n")

def log_success(count: int):
    sys.stderr.write(
        f"Ooooooh! Done! Found {count} items. Here is your TOON context. In your face!\n"
    )

def log_error(error: str):
    sys.stderr.write(f"Dude, stop! This file is trash. I can't parse it. {error}\n")

# --- AST Visitor Logic ---

class ToonVisitor(ast.NodeVisitor):
    """
    Visits AST nodes to extract structure in TOON format.
    - Classes -> CLS
    - Functions -> FUNC / ASYNC_FUNC
    - Methods -> MTHD / ASYNC_MTHD
    - Typed Globals -> VAR
    """
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.items_found = 0

    def _get_indent(self):
        return "  " * self.indent_level

    def _format_docstring(self, node) -> str:
        """Extracts, flattens, and truncates docstrings."""
        doc = ast.get_docstring(node)
        if not doc:
            return ""
        # Flatten to single line
        flat = " ".join([line.strip() for line in doc.splitlines() if line.strip()])
        # Truncate if too long
        if len(flat) > 100:
            flat = flat[:97] + "..."
        return f' "{flat}"'

    def _format_arg(self, arg: ast.arg, default: Optional[ast.AST] = None) -> str:
        """Formats a single argument with type hint and default value."""
        annotation = "?"
        if arg.annotation:
            try:
                # ast.unparse handles complex types like List[int] automatically
                annotation = ast.unparse(arg.annotation)
            except Exception:
                annotation = "Any"

        arg_str = f"{arg.arg}:{annotation}"

        if default:
            try:
                default_val = ast.unparse(default)
                arg_str += f"={default_val}"
            except Exception:
                pass
        return arg_str

    def _get_args_str(self, args: ast.arguments) -> str:
        """Reconstructs the argument list string from AST."""
        arg_list = []

        # Handle positional-only args (Python 3.8+)
        # defaults list corresponds to [posonlyargs...] + [args...]
        # The logic for mapping defaults is complex because defaults can cover both 
        # posonly and regular args.
        # However, ast.arguments stores defaults for both in 'defaults'.
        # It's easier to iterate backwards or calculate indices carefully.

        # Total positional args = posonlyargs + args
        all_pos_args = args.posonlyargs + args.args
        num_defaults = len(args.defaults)
        offset = len(all_pos_args) - num_defaults

        for i, arg in enumerate(all_pos_args):
            default = None
            if i >= offset:
                default = args.defaults[i - offset]

            formatted = self._format_arg(arg, default)
            arg_list.append(formatted)

            # Add the '/' marker if this was the last positional-only argument
            if i == len(args.posonlyargs) - 1:
                arg_list.append("/")

        # Handle varargs (*args)
        if args.vararg:
            annotation = ""
            if args.vararg.annotation:
                annotation = f":{ast.unparse(args.vararg.annotation)}"
            arg_list.append(f"*{args.vararg.arg}{annotation}")

        # Handle kwonlyargs (args after *)
        # kw_defaults can contain None if no default is provided
        for i, arg in enumerate(args.kwonlyargs):
            default = args.kw_defaults[i]
            arg_list.append(self._format_arg(arg, default))

        # Handle kwargs (**kwargs)
        if args.kwarg:
             annotation = ""
             if args.kwarg.annotation:
                annotation = f":{ast.unparse(args.kwarg.annotation)}"
             arg_list.append(f"**{args.kwarg.arg}{annotation}")

        return ",".join(arg_list)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.items_found += 1
        bases = ""
        if node.bases:
            bases_list = [ast.unparse(b) for b in node.bases]
            bases = f"({', '.join(bases_list)})"

        self.output.append(f"{self._get_indent()}CLS {node.name}{bases}:")

        self.indent_level += 1
        # We iterate manually to avoid visiting nodes we don't care about
        # or to control the order/indentation precisely if needed.
        # But generic self.generic_visit(node) would also work if we filtered carefully.
        # Explicit loop is safer for 'TOON' output control.
        for child in node.body:
             if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                 self.visit(child)
             elif isinstance(child, ast.AnnAssign):
                 # Could handle class attributes here if needed
                 pass

        self.indent_level -= 1

    def _process_function(self, node, is_async: bool, is_method: bool):
        self.items_found += 1
        prefix = "ASYNC_" if is_async else ""
        kind = "MTHD" if is_method else "FUNC"
        tag = f"{prefix}{kind}"

        args_str = self._get_args_str(node.args)

        ret_type = ""
        if node.returns:
            try:
                ret_type = f" -> {ast.unparse(node.returns)}"
            except Exception:
                ret_type = " -> Any"

        doc_str = self._format_docstring(node)

        self.output.append(f"{self._get_indent()}{tag} {node.name}({args_str}){ret_type}:{doc_str}")

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Heuristic: if indent > 0, we are likely inside a class
        is_method = self.indent_level > 0
        self._process_function(node, is_async=False, is_method=is_method)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        is_method = self.indent_level > 0
        self._process_function(node, is_async=True, is_method=is_method)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        # Only capture top-level global variables with type hints
        if self.indent_level == 0 and isinstance(node.target, ast.Name):
             self.items_found += 1
             try:
                 type_str = ast.unparse(node.annotation)
                 name = node.target.id
                 self.output.append(f"VAR {name}: {type_str}")
             except Exception:
                 pass # Skip if complex to parse

# --- Main Execution Logic ---

def parse_file(filepath: str) -> tuple[str, int]:
    """Parses a single file and returns its TOON string representation."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    visitor = ToonVisitor()
    visitor.visit(tree)
    return "\n".join(visitor.output), visitor.items_found

IGNORED_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", ".idea", ".vscode", "build", "dist", "env",
    ".venv", "site-packages", ".mypy_cache", ".ruff_cache"
}

def process_path(path: str):
    """Recursively processes files in the path."""
    log_start(path)

    total_items = 0
    results = []

    if os.path.isfile(path):
        files_to_process = [path]
    else:
        files_to_process = []
        for root, dirs, files in os.walk(path):
            # Modify dirs in-place to prevent os.walk from traversing them
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file in files:
                if file.endswith(".py"):
                    files_to_process.append(os.path.join(root, file))

    for fp in files_to_process:
        try:
            output, count = parse_file(fp)
            if output:
                results.append(output)
                total_items += count
        except SyntaxError as e:
            # Fault tolerance: Log error but keep going
            log_error(f"{fp}: {e}")
        except Exception as e:
            log_error(f"{fp}: {e}")

    if results:
        print("\n\n".join(results))
        log_success(total_items)
    else:
        log_success(0)


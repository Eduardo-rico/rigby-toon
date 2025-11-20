import ast
import textwrap

from rigby.core import ToonVisitor


def test_visitor_simple_function():
    code = textwrap.dedent("""
        def hello(name: str) -> str:
            '''Greets the user.'''
            return f"Hello {name}"
    """)
    tree = ast.parse(code)
    visitor = ToonVisitor()
    visitor.visit(tree)
    
    expected = 'FUNC hello(name:str) -> str: "Greets the user."'
    assert visitor.output[0].strip() == expected

def test_visitor_class_structure():
    code = textwrap.dedent("""
        class Dog(Animal):
            def bark(self):
                pass
    """)
    tree = ast.parse(code)
    visitor = ToonVisitor()
    visitor.visit(tree)
    
    assert "CLS Dog(Animal):" in visitor.output[0]
    # Check indentation and method
    # Arguments without annotations get assigned '?' by default
    assert "  MTHD bark(self:?):" in visitor.output[1]

def test_async_definitions():
    code = textwrap.dedent("""
        async def fetch_data():
            pass
            
        class API:
            async def get(self):
                pass
    """)
    tree = ast.parse(code)
    visitor = ToonVisitor()
    visitor.visit(tree)
    
    assert "ASYNC_FUNC fetch_data():" in visitor.output
    assert "  ASYNC_MTHD get(self:?):" in visitor.output

def test_typed_globals():
    code = textwrap.dedent("""
        MAX_RETRIES: int = 5
        name: str
    """)
    tree = ast.parse(code)
    visitor = ToonVisitor()
    visitor.visit(tree)
    
    assert "VAR MAX_RETRIES: int" in visitor.output
    assert "VAR name: str" in visitor.output

def test_docstring_truncation():
    long_doc = "A" * 200
    code = f"def foo():\n    '''{long_doc}'''\n    pass"
    tree = ast.parse(code)
    visitor = ToonVisitor()
    visitor.visit(tree)
    
    # Should be truncated
    assert "..." in visitor.output[0]
    assert len(visitor.output[0]) < 200

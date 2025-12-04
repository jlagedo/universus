"""
Architecture validation tests.

These tests ensure the codebase follows the documented layer segregation:

┌─────────────────────────────────────────┐
│  CLI (universus.py) + GUI (gui/)        │  ← User interfaces
├─────────────────────────────────────────┤
│  Presentation (ui.py)                   │  ← Terminal formatting
├─────────────────────────────────────────┤
│  Business Logic (service.py)            │  ← Market operations
├─────────────────────────────────────────┤
│  API Client (api_client.py)             │  ← HTTP + rate limiting
│  Database (database.py)                 │  ← SQLite persistence
└─────────────────────────────────────────┘

Rules:
- GUI views should NEVER import or use database/api_client directly
- GUI views should ONLY use the service layer
- CLI should use service layer, not database directly (except for initialization)
"""

import ast
import os
import pytest
from pathlib import Path


def get_imports_from_file(filepath: str) -> set:
    """Extract all import statements from a Python file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports


def get_attribute_access(filepath: str) -> list:
    """Find all attribute access patterns like 'db.method()' or 'api.method()'."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    violations = []
    # Simple pattern matching for db. and api. usage
    import re
    
    # Look for patterns like db.something or api.something (not self.db or self.api)
    # This catches function parameters being used directly
    for line_num, line in enumerate(content.split('\n'), 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue
        # Look for standalone db. or api. usage (parameter access)
        if re.search(r'(?<!\.)(?<!self\.)\bdb\.', line):
            violations.append((line_num, 'db', line.strip()))
        if re.search(r'(?<!\.)(?<!self\.)\bapi\.', line):
            violations.append((line_num, 'api', line.strip()))
    
    return violations


class TestLayerSegregation:
    """Test that GUI views don't bypass the service layer."""
    
    @pytest.fixture
    def gui_views_path(self):
        return Path('gui/views')
    
    @pytest.fixture
    def gui_components_path(self):
        return Path('gui/components')
    
    def test_views_do_not_import_database(self, gui_views_path):
        """GUI views should not import database module."""
        if not gui_views_path.exists():
            pytest.skip("gui/views not found")
        
        violations = []
        for py_file in gui_views_path.glob('*.py'):
            imports = get_imports_from_file(str(py_file))
            if 'database' in imports:
                violations.append(f"{py_file.name} imports 'database'")
        
        assert not violations, f"Layer violation - views importing database:\n" + "\n".join(violations)
    
    def test_views_do_not_import_api_client(self, gui_views_path):
        """GUI views should not import api_client module."""
        if not gui_views_path.exists():
            pytest.skip("gui/views not found")
        
        violations = []
        for py_file in gui_views_path.glob('*.py'):
            imports = get_imports_from_file(str(py_file))
            if 'api_client' in imports:
                violations.append(f"{py_file.name} imports 'api_client'")
        
        assert not violations, f"Layer violation - views importing api_client:\n" + "\n".join(violations)
    
    def test_views_do_not_use_db_directly(self, gui_views_path):
        """GUI views should not access db parameter directly."""
        if not gui_views_path.exists():
            pytest.skip("gui/views not found")
        
        violations = []
        for py_file in gui_views_path.glob('*.py'):
            file_violations = get_attribute_access(str(py_file))
            for line_num, obj, line in file_violations:
                if obj == 'db':
                    violations.append(f"{py_file.name}:{line_num} - {line}")
        
        assert not violations, f"Layer violation - views using db directly:\n" + "\n".join(violations)
    
    def test_views_do_not_use_api_directly(self, gui_views_path):
        """GUI views should not access api parameter directly."""
        if not gui_views_path.exists():
            pytest.skip("gui/views not found")
        
        violations = []
        for py_file in gui_views_path.glob('*.py'):
            file_violations = get_attribute_access(str(py_file))
            for line_num, obj, line in file_violations:
                if obj == 'api':
                    violations.append(f"{py_file.name}:{line_num} - {line}")
        
        assert not violations, f"Layer violation - views using api directly:\n" + "\n".join(violations)
    
    def test_components_do_not_import_database(self, gui_components_path):
        """GUI components should not import database module."""
        if not gui_components_path.exists():
            pytest.skip("gui/components not found")
        
        violations = []
        for py_file in gui_components_path.glob('*.py'):
            imports = get_imports_from_file(str(py_file))
            if 'database' in imports:
                violations.append(f"{py_file.name} imports 'database'")
        
        assert not violations, f"Layer violation - components importing database:\n" + "\n".join(violations)
    
    def test_components_do_not_import_api_client(self, gui_components_path):
        """GUI components should not import api_client module."""
        if not gui_components_path.exists():
            pytest.skip("gui/components not found")
        
        violations = []
        for py_file in gui_components_path.glob('*.py'):
            imports = get_imports_from_file(str(py_file))
            if 'api_client' in imports:
                violations.append(f"{py_file.name} imports 'api_client'")
        
        assert not violations, f"Layer violation - components importing api_client:\n" + "\n".join(violations)


class TestServiceLayerIntegrity:
    """Test that service layer properly encapsulates data access."""
    
    def test_service_imports_database(self):
        """Service layer should import database."""
        imports = get_imports_from_file('service.py')
        assert 'database' in imports, "Service should import database module"
    
    def test_service_imports_api_client(self):
        """Service layer should import api_client."""
        imports = get_imports_from_file('service.py')
        assert 'api_client' in imports, "Service should import api_client module"


class TestUILayerIntegrity:
    """Test that UI (presentation) layer doesn't access data layers."""
    
    def test_ui_does_not_import_database(self):
        """UI layer should not import database."""
        imports = get_imports_from_file('ui.py')
        assert 'database' not in imports, "UI layer should not import database"
    
    def test_ui_does_not_import_api_client(self):
        """UI layer should not import api_client."""
        imports = get_imports_from_file('ui.py')
        assert 'api_client' not in imports, "UI layer should not import api_client"
    
    def test_ui_does_not_import_service(self):
        """UI layer should not import service (it's purely presentation)."""
        imports = get_imports_from_file('ui.py')
        assert 'service' not in imports, "UI layer should not import service"

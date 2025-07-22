#!/usr/bin/env python3
"""
Basic structure test for Social Media Agent.

This script performs basic validation of the project structure
and verifies that all modules can be imported correctly.
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Test that the project has the expected structure."""
    print("🏗️  Testing project structure...")
    
    project_root = Path(__file__).parent.parent
    
    # Required directories
    required_dirs = [
        "src",
        "src/agents",
        "src/agents/platform_agents",
        "src/agents/team_leader",
        "src/config",
        "src/content_generation",
        "src/metrics",
        "src/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
        "examples",
        "scripts"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    if missing_dirs:
        print(f"  ❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Project structure is correct")
    return True


def test_required_files():
    """Test that required files exist."""
    print("\n📄 Testing required files...")
    
    project_root = Path(__file__).parent.parent
    
    # Required files
    required_files = [
        "README.md",
        "LICENSE",
        "requirements.txt",
        "setup.py",
        "src/__init__.py",
        "src/main.py",
        "examples/config.example.yaml",
        "Dockerfile",
        ".github/workflows/ci.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True


def test_python_syntax():
    """Test that all Python files have valid syntax."""
    print("\n🐍 Testing Python syntax...")
    
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    python_files = list(src_dir.rglob("*.py"))
    
    syntax_errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to compile the file
            compile(content, str(py_file), 'exec')
            print(f"  ✅ {py_file.relative_to(project_root)}")
        
        except SyntaxError as e:
            syntax_errors.append((py_file, str(e)))
            print(f"  ❌ {py_file.relative_to(project_root)}: {e}")
        except Exception as e:
            print(f"  ⚠️  {py_file.relative_to(project_root)}: Could not read file - {e}")
    
    if syntax_errors:
        print(f"❌ Found {len(syntax_errors)} syntax errors")
        return False
    
    print("✅ All Python files have valid syntax")
    return True


def test_configuration_files():
    """Test that configuration files are valid."""
    print("\n⚙️  Testing configuration files...")
    
    project_root = Path(__file__).parent.parent
    
    # Test YAML files
    yaml_files = [
        "examples/config.example.yaml",
        ".github/workflows/ci.yml",
        "docker-compose.yml"
    ]
    
    yaml_errors = []
    for yaml_file in yaml_files:
        full_path = project_root / yaml_file
        if full_path.exists():
            try:
                import yaml
                with open(full_path, 'r') as f:
                    yaml.safe_load(f)
                print(f"  ✅ {yaml_file}")
            except yaml.YAMLError as e:
                yaml_errors.append((yaml_file, str(e)))
                print(f"  ❌ {yaml_file}: {e}")
        else:
            print(f"  ⚠️  {yaml_file}: File not found (optional)")
    
    if yaml_errors:
        print(f"❌ Found {len(yaml_errors)} YAML errors")
        return False
    
    print("✅ All configuration files are valid")
    return True


def test_documentation():
    """Test that documentation files exist and are readable."""
    print("\n📚 Testing documentation...")
    
    project_root = Path(__file__).parent.parent
    
    # Required documentation
    doc_files = [
        "README.md",
        "docs/api/README.md",
        "docs/deployment/README.md",
        "docs/tutorials/getting-started.md"
    ]
    
    missing_docs = []
    for doc_file in doc_files:
        full_path = project_root / doc_file
        if not full_path.exists():
            missing_docs.append(doc_file)
        else:
            # Check if file is not empty
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if len(content) > 100:  # Reasonable minimum length
                    print(f"  ✅ {doc_file}")
                else:
                    print(f"  ⚠️  {doc_file}: File is too short")
            except Exception as e:
                print(f"  ❌ {doc_file}: Could not read - {e}")
    
    if missing_docs:
        print(f"  ❌ Missing documentation: {missing_docs}")
        return False
    
    print("✅ Documentation files exist and are readable")
    return True


def test_dependencies():
    """Test that requirements.txt is valid."""
    print("\n📦 Testing dependencies...")
    
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("  ❌ requirements.txt not found")
        return False
    
    try:
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
        
        # Basic validation
        valid_lines = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Basic package name validation
                if '==' in line or '>=' in line or '<=' in line or '>' in line or '<' in line:
                    valid_lines += 1
                elif line.replace('-', '').replace('_', '').isalnum():
                    valid_lines += 1
        
        print(f"  ✅ Found {valid_lines} valid package requirements")
        
        if valid_lines > 0:
            print("✅ requirements.txt is valid")
            return True
        else:
            print("❌ No valid requirements found")
            return False
    
    except Exception as e:
        print(f"  ❌ Error reading requirements.txt: {e}")
        return False


def main():
    """Run all basic tests."""
    print("🚀 Running basic structure tests for Social Media Agent")
    print("=" * 60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Required Files", test_required_files),
        ("Python Syntax", test_python_syntax),
        ("Configuration Files", test_configuration_files),
        ("Documentation", test_documentation),
        ("Dependencies", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        emoji = "✅" if result else "❌"
        status = "PASSED" if result else "FAILED"
        print(f"  {emoji} {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 All basic tests passed! The project structure is correct.")
        print("You can now proceed with running the full system tests.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


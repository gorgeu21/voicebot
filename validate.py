#!/usr/bin/env python3
"""
Validation script for Telegram Voice Bot project
Checks code quality, project structure, and deployment readiness
"""
import ast
import os
import re
import sys
from pathlib import Path

def check_python_syntax():
    """Check Python file syntax"""
    print("🐍 Checking Python syntax...")
    app_files = [
        "app/config.py",
        "app/main.py", 
        "app/telegram_bot.py",
        "app/transcriber.py",
        "app/summarizer.py"
    ]
    
    all_good = True
    for file_path in app_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source)
            print(f"  ✓ {file_path}")
        except SyntaxError as e:
            print(f"  ✗ {file_path}: {e}")
            all_good = False
        except Exception as e:
            print(f"  ! {file_path}: {e}")
            all_good = False
    
    return all_good

def check_dependencies():
    """Check requirements.txt format"""
    print("\n📦 Checking dependencies...")
    try:
        with open('requirements.txt', 'r') as f:
            deps = [line.strip() for line in f.readlines() if line.strip()]
        
        valid_count = 0
        for dep in deps:
            # Allow package names with version specifiers and extras
            if re.match(r'^[a-zA-Z0-9_-]+(\[[a-zA-Z,]+\])?(>=|<=|==|!=|>|<)[0-9.]+(\[[a-zA-Z,]+\])?$', dep) or \
               re.match(r'^[a-zA-Z0-9_-]+$', dep):
                print(f"  ✓ {dep}")
                valid_count += 1
            else:
                print(f"  ! {dep} - Check format")
        
        print(f"  📊 {valid_count}/{len(deps)} dependencies validated")
        return valid_count == len(deps)
        
    except FileNotFoundError:
        print("  ✗ requirements.txt not found")
        return False

def check_project_structure():
    """Check required files and directories"""
    print("\n📁 Checking project structure...")
    required_items = {
        'files': [
            'requirements.txt',
            '.env.example', 
            '.gitignore',
            'README.md',
            'Dockerfile',
            'railway.json',
            'app/config.py',
            'app/main.py',
            'app/telegram_bot.py', 
            'app/transcriber.py',
            'app/summarizer.py'
        ],
        'directories': [
            'app/'
        ]
    }
    
    all_present = True
    
    for directory in required_items['directories']:
        if os.path.isdir(directory):
            print(f"  ✓ {directory}")
        else:
            print(f"  ✗ {directory} (missing directory)")
            all_present = False
    
    for file_path in required_items['files']:
        if os.path.isfile(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing file)")
            all_present = False
    
    return all_present

def check_environment_config():
    """Check environment configuration"""
    print("\n⚙️ Checking environment configuration...")
    required_env_vars = [
        'BOT_TOKEN',
        'WEBHOOK_URL', 
        'OPENAI_API_KEY'
    ]
    
    try:
        with open('.env.example', 'r') as f:
            env_content = f.read()
        
        all_vars_present = True
        for var in required_env_vars:
            if f"{var}=" in env_content:
                print(f"  ✓ {var}")
            else:
                print(f"  ✗ {var} (missing from .env.example)")
                all_vars_present = False
        
        return all_vars_present
        
    except FileNotFoundError:
        print("  ✗ .env.example not found")
        return False

def check_deployment_readiness():
    """Check deployment configuration"""
    print("\n🚀 Checking deployment readiness...")
    deployment_files = {
        'Dockerfile': 'Docker deployment',
        'railway.json': 'Railway platform',
        'requirements.txt': 'Python dependencies'
    }
    
    all_ready = True
    for file_path, description in deployment_files.items():
        if os.path.isfile(file_path):
            print(f"  ✓ {file_path} ({description})")
        else:
            print(f"  ✗ {file_path} ({description}) - missing")
            all_ready = False
    
    return all_ready

def main():
    """Run all validation checks"""
    print("🔍 Telegram Voice Bot - Project Validation")
    print("=" * 50)
    
    checks = [
        ("Python Syntax", check_python_syntax),
        ("Dependencies", check_dependencies), 
        ("Project Structure", check_project_structure),
        ("Environment Config", check_environment_config),
        ("Deployment Readiness", check_deployment_readiness)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("🎉 Project is ready for deployment!")
        return 0
    else:
        print("⚠️ Please fix the issues above before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
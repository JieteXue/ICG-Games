import os
import sys

def check_structure():
    """检查项目结构"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    
    print("🔍 Checking project structure...")
    print(f"Base directory: {base_dir}")
    print(f"Source directory: {src_dir}")
    print(f"Exists: {os.path.exists(src_dir)}")
    
    if not os.path.exists(src_dir):
        print("❌ src directory not found!")
        return False
    
    print("\n📁 Contents of src directory:")
    required_dirs = ['core', 'games', 'utils', 'ui']
    all_good = True
    
    for item in sorted(os.listdir(src_dir)):
        item_path = os.path.join(src_dir, item)
        status = "✅" if os.path.exists(item_path) else "❌"
        print(f"  {status} {item}/")
        
        if os.path.isdir(item_path):
            # 检查 __init__.py
            init_file = os.path.join(item_path, '__init__.py')
            init_status = "✅" if os.path.exists(init_file) else "❌"
            print(f"    {init_status} __init__.py")
            
            # 列出子文件和目录
            try:
                subitems = os.listdir(item_path)
                for subitem in sorted(subitems):
                    if subitem != '__init__.py':
                        subitem_path = os.path.join(item_path, subitem)
                        sub_status = "✅" if os.path.exists(subitem_path) else "❌"
                        if os.path.isdir(subitem_path):
                            print(f"    📁 {subitem}/")
                            # 检查子目录的 __init__.py
                            sub_init = os.path.join(subitem_path, '__init__.py')
                            sub_init_status = "✅" if os.path.exists(sub_init) else "❌"
                            print(f"      {sub_init_status} __init__.py")
                        else:
                            print(f"    📄 {subitem}")
            except OSError as e:
                print(f"    ❌ Error reading: {e}")
                all_good = False
    
    return all_good

def check_python_path():
    """检查Python路径"""
    print("\n🐍 Checking Python path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

def check_imports():
    """测试导入"""
    print("\n📦 Testing imports...")
    
    # 添加src到路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    sys.path.insert(0, src_dir)
    
    imports_to_test = [
        'core.game_registry',
        'utils.constants', 
        'utils.helpers',
        'ui.buttons',
        'ui.menus',
        'games.card_nim.game'
    ]
    
    for import_path in imports_to_test:
        try:
            __import__(import_path)
            print(f"  ✅ {import_path}")
        except ImportError as e:
            print(f"  ❌ {import_path}: {e}")

def main():
    print("🚀 ICG Games Project Diagnostic")
    print("=" * 50)
    
    # 检查结构
    structure_ok = check_structure()
    
    # 检查Python路径
    check_python_path()
    
    # 测试导入
    check_imports()
    
    print("\n" + "=" * 50)
    if structure_ok:
        print("✅ Project structure looks good!")
        print("💡 If imports are failing, check the file contents.")
    else:
        print("❌ Project structure has issues!")
        print("💡 Make sure all directories and __init__.py files exist.")

if __name__ == "__main__":
    main()
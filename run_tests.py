import subprocess
import sys

def run_tests():
    print("运行单元测试...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_models/", 
        "tests/test_services/", 
        "tests/test_controllers/",
        "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    
    print("\n运行集成测试...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/integration/",
        "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
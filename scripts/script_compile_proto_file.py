
from pathlib import Path
import subprocess


workspace_dir = Path(__file__).parent.parent.absolute()

def compile_proto(python_path=".venv/bin/python3") -> bool:
    # Build the public proto file
    ret = subprocess.run([f"{python_path}", '-m', 'grpc_tools.protoc', '-I', 'proto/', '--python_betterproto_out=src/grow_api_python_example/', 'ps_common.proto', 'ps_controller_service.proto',], stdout=subprocess.PIPE, stderr=subprocess.PIPE , text=True)
    if ret.returncode != 0 or (ret.stderr and "No module" in ret.stderr):
        print(f"Unable to generate proto, Err msg: {ret.stderr}")
        return False
    print(ret.stdout)
    print(ret.stderr)
    return True





if __name__ == "__main__":
    windows_python_path = workspace_dir / ".venv/Scripts/python.exe"
    linux_python_path = workspace_dir / ".venv/bin/python3"
    if windows_python_path.exists():
        ret = compile_proto(python_path=windows_python_path)   
    elif linux_python_path.exists():
        ret = compile_proto(python_path=linux_python_path)
    else:
        raise Exception("Python path not found")

    if not ret:
        print("compiling protofile failed")
    else:
        print("Success")

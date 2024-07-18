import subprocess
import os
import sys
import time

def compile_proto():
    # Comando para compilar o arquivo .proto
    proto_command = [
        sys.executable, 
        "-m", "grpc_tools.protoc", 
        "-I.", 
        "--python_out=.", 
        "--grpc_python_out=.", 
        "bookstore.proto"
    ]
    subprocess.run(proto_command, check=True)

def run_server():
    # Comando para iniciar o servidor gRPC
    server_command = [sys.executable, "bookstore_server.py"]
    return subprocess.Popen(server_command)

def run_streamlit():
    # Comando para iniciar o aplicativo Streamlit
    streamlit_command = [sys.executable, "-m", "streamlit", "run", "bookstore_app.py"]
    return subprocess.Popen(streamlit_command)

if __name__ == "__main__":
    # Compila o arquivo .proto
    compile_proto()
    
    # Inicia o servidor gRPC
    server_process = run_server()
    time.sleep(5)  # Aguarda alguns segundos para garantir que o servidor está em execução

    # Inicia o aplicativo Streamlit
    streamlit_process = run_streamlit()

    try:
        # Mantém o script principal em execução enquanto os subprocessos estão em execução
        server_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        # Finaliza os subprocessos em caso de interrupção (Ctrl+C)
        server_process.terminate()
        streamlit_process.terminate()
        server_process.wait()
        streamlit_process.wait()

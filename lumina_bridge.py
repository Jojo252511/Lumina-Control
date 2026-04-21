import socket
import json
import sys

def send_command(cmd_dict):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect("/tmp/lumina.sock")
        client.send(json.dumps(cmd_dict).encode())
        if cmd_dict["type"] in ["get_stats", "test", "start_openrgb", "set_gpu"]:
            response = client.recv(1024).decode()
            print(response) # Goes back to QML
    except Exception as e:
        print(f"Lumina Bridge Error: {e}", file=sys.stderr)
    finally:
        client.close()

if __name__ == "__main__":
    if sys.argv[1] == "set_gpu":
        send_command({"type": "set_gpu", "value": int(sys.argv[2])})
    elif sys.argv[1] == "get_stats":
        send_command({"type": "get_stats"})
    elif sys.argv[1] == "openrgb":
        send_command({"type": "start_openrgb"})
    elif sys.argv[1] == "test":
        send_command({"type": "test"})
    
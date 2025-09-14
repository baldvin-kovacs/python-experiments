import requests
import sys
from wscat.server import simple_math_pb2

def main():
    add_req = simple_math_pb2.AddRequest(a=100, b=50)
    payload = add_req.SerializeToString()
    headers = {'Content-Type': 'application/protobuf'}

    try:
        response = requests.post("http://127.0.0.1:8000/add", data=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        add_resp = simple_math_pb2.AddResponse()
        add_resp.ParseFromString(response.content)
        print(f"Success! Result from server: {add_resp.result}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

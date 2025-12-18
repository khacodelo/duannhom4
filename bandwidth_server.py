import socket
import struct
import time

HOST = "0.0.0.0"
PORT = 50000

def recv_exact(conn, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Client disconnected while receiving.")
        data += chunk
    return data

def main():
    print(f"[Server] Listening on {HOST}:{PORT} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[Server] Connected: {addr}")

                # Client gửi 8 byte: tổng số byte sẽ gửi (unsigned long long)
                total_bytes = struct.unpack("!Q", recv_exact(conn, 8))[0]
                print(f"[Server] Expecting {total_bytes} bytes")

                received = 0
                t0 = time.perf_counter()

                while received < total_bytes:
                    chunk = conn.recv(min(65536, total_bytes - received))
                    if not chunk:
                        break
                    received += len(chunk)

                t1 = time.perf_counter()
                elapsed = max(t1 - t0, 1e-9)

                # Trả kết quả cho client: received (8 byte) + elapsed_ms (8 byte)
                elapsed_ms = int(elapsed * 1000)
                conn.sendall(struct.pack("!QQ", received, elapsed_ms))

                print(f"[Server] Done. Received={received} bytes, time={elapsed:.6f}s")

if __name__ == "__main__":
    main()

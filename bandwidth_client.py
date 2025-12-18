import socket
import struct
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

CHUNK = 64 * 1024  # 64KB

class BandwidthApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Công cụ Đo Băng thông TCP (Client)")

        self.running = False

        frm = ttk.Frame(root, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Server IP:").grid(row=0, column=0, sticky="w")
        self.ip_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(frm, textvariable=self.ip_var, width=25).grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(frm, text="Port:").grid(row=1, column=0, sticky="w")
        self.port_var = tk.StringVar(value="50000")
        ttk.Entry(frm, textvariable=self.port_var, width=10).grid(row=1, column=1, sticky="w", padx=6)

        ttk.Label(frm, text="Dung lượng gửi (MB):").grid(row=2, column=0, sticky="w")
        self.mb_var = tk.StringVar(value="100")
        ttk.Entry(frm, textvariable=self.mb_var, width=10).grid(row=2, column=1, sticky="w", padx=6)

        self.pb = ttk.Progressbar(frm, orient="horizontal", mode="determinate")
        self.pb.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 4))

        self.status = tk.StringVar(value="Sẵn sàng.")
        ttk.Label(frm, textvariable=self.status).grid(row=4, column=0, columnspan=2, sticky="w")

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)

        self.btn_start = ttk.Button(btns, text="Bắt đầu đo", command=self.start)
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_stop = ttk.Button(btns, text="Dừng", command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Khu vực kết quả
        sep = ttk.Separator(frm)
        sep.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        self.result = tk.StringVar(value="Kết quả: -")
        ttk.Label(frm, textvariable=self.result, font=("Segoe UI", 10, "bold")).grid(
            row=7, column=0, columnspan=2, sticky="w"
        )

    def set_ui_running(self, is_running: bool):
        self.btn_start.configure(state="disabled" if is_running else "normal")
        self.btn_stop.configure(state="normal" if is_running else "disabled")

    def stop(self):
        self.running = False
        self.status.set("Đang yêu cầu dừng...")

    def start(self):
        if self.running:
            return
        try:
            ip = self.ip_var.get().strip()
            port = int(self.port_var.get().strip())
            mb = float(self.mb_var.get().strip())
            if mb <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Lỗi", "Vui lòng nhập IP/Port/MB hợp lệ.")
            return

        self.running = True
        self.set_ui_running(True)
        self.pb["value"] = 0
        self.result.set("Kết quả: -")
        self.status.set("Đang kết nối server...")

        th = threading.Thread(target=self.worker, args=(ip, port, mb), daemon=True)
        th.start()

    def worker(self, ip: str, port: int, mb: float):
        total_bytes = int(mb * 1024 * 1024)
        payload = b"\x55" * CHUNK  # dữ liệu mẫu

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((ip, port))
                s.settimeout(None)

                # gửi header: total_bytes
                s.sendall(struct.pack("!Q", total_bytes))

                sent = 0
                self._ui(lambda: self.status.set(f"Đang gửi {mb:.2f} MB..."))

                t0 = time.perf_counter()

                while sent < total_bytes and self.running:
                    to_send = min(CHUNK, total_bytes - sent)
                    s.sendall(payload[:to_send])
                    sent += to_send

                    pct = (sent / total_bytes) * 100
                    self._ui(lambda p=pct: self.pb.configure(value=p))
                    self._ui(lambda: self.status.set(f"Đã gửi: {sent/1024/1024:.2f}/{mb:.2f} MB"))

                if not self.running:
                    self._ui(lambda: self.status.set("Đã dừng."))
                    self._ui(lambda: self.set_ui_running(False))
                    return

                # nhận kết quả server: received + elapsed_ms
                data = self.recv_exact(s, 16)
                received, elapsed_ms = struct.unpack("!QQ", data)

                t1 = time.perf_counter()
                client_elapsed = max(t1 - t0, 1e-9)  # tham khảo

                elapsed_s = max(elapsed_ms / 1000.0, 1e-9)
                mbps = (received * 8) / (elapsed_s * 1_000_000)

                self._ui(lambda: self.pb.configure(value=100))
                self._ui(lambda: self.status.set("Hoàn tất."))
                self._ui(lambda: self.result.set(
                    f"Kết quả: Nhận {received/1024/1024:.2f} MB | "
                    f"Server time {elapsed_s:.4f}s | "
                    f"Tốc độ ~ {mbps:.2f} Mbps | "
                    f"(Client time {client_elapsed:.4f}s)"
                ))

        except Exception as e:
            self._ui(lambda: messagebox.showerror("Lỗi", f"Không đo được: {e}"))
            self._ui(lambda: self.status.set("Lỗi khi đo."))
        finally:
            self.running = False
            self._ui(lambda: self.set_ui_running(False))

    def recv_exact(self, sock: socket.socket, n: int) -> bytes:
        data = b""
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Server closed connection.")
            data += chunk
        return data

    def _ui(self, fn):
        self.root.after(0, fn)

def main():
    root = tk.Tk()
    app = BandwidthApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

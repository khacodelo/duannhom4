 HEAD
TCP Network Bandwidth Measurement Tool

1. Giới thiệu dự án
TCP Network Bandwidth Measurement Tool là một công cụ đo băng thông mạng được xây dựng theo mô hình Client – Server, sử dụng giao thức TCP.

Trong hệ thống này, client gửi một lượng dữ liệu lớn (ví dụ: 100MB) tới server. Server đo thời gian nhận dữ liệu và gửi lại kết quả cho client để tính toán và hiển thị tốc độ truyền dữ liệu (Mbps).  
Dự án giúp người học hiểu rõ hơn về lập trình mạng, đo lường hiệu năng và xử lý dữ liệu dung lượng lớn.

2. Thành viên nhóm
Nhóm 4:
- 1.Nguyễn Hữu Kha
- 2.Huỳnh Duy Hưng
- 3.Võ Duy Khải
- 4.Vũ Xuân Tuấn

4. Công nghệ sử dụng
- Ngôn ngữ lập trình: Python 3.13
- Giao thức mạng: TCP
- Thư viện chính:
  - socket – Lập trình mạng TCP
  - time – Đo thời gian thực thi
  - struct – Đóng gói và giải mã dữ liệu nhị phân
  - tkinter – Xây dựng giao diện người dùng (Client)
  - threading – Xử lý đa luồng, tránh treo giao diện

4. Cấu trúc dự án

testspeed
├─ bandwidth_server.py
├─ bandwidth_client_gui.py
├─ common.py                    
├─ README.md
└─ requirements.txt

5. Nguyên lý hoạt động
1. Server khởi động và lắng nghe kết nối TCP tại một cổng xác định
2. Client kết nối đến server
3. Client gửi trước tổng dung lượng dữ liệu cần truyền
4. Client gửi dữ liệu đến server theo từng khối (chunk)
5. Server nhận dữ liệu và đo thời gian nhận
6. Server gửi kết quả (tổng byte, thời gian) về cho client
7. Client tính toán và hiển thị tốc độ truyền (Mbps)



6. Hướng dẫn cài đặt

6.1. Yêu cầu hệ thống
- Hệ điều hành: Windows / Linux / macOS
- Python phiên bản 3.10 trở lên (khuyến nghị Python 3.13)
- Không cần cài thêm thư viện ngoài

6.2. Kiểm tra Python
bash
python --version
7. Hướng dẫn thực thi chương trình
Mở terminal tại thư mục dự án:
-python bandwidth_server.py để khởi động server
-python bandwidth_client.py để khởi động client
Nhập ip server và port tương ứng

=======
# duannhom4
>>>>>>> cd733fedc98437ad541f42ad024d92bce1342a9d

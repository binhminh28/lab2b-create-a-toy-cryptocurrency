# Lab 2: Create a (Toy) Cryptocurrency (Python) (~2-3 giờ)
**Course:** Blockchain Tech, UIT, VNUHCM  
**Lecturer:** Dr. Tran Hung Nghiep, 2025  

> Mục tiêu: hiểu **mô hình tài khoản**, giao dịch, kiểm tra chữ ký (giả lập học thuật), sổ cái & số dư.
> **Lưu ý**: Chữ ký trong lab này là **giả lập**, không dùng cho sản xuất. Chỉ dùng cho mục đích học thuật.

## Kết quả mong đợi
- Sinh "khóa" đơn giản (toy): `secret_key` (32 bytes) -> `address = sha256(secret_key)[:40]`.
- Tạo giao dịch `{from, to, amount, nonce, signature}`; "ký" = `sha256(secret_key + tx_json)`.
- Validate giao dịch: kiểm tra `address == sha256(secret_key)[:40]` và `signature` khớp.
- Áp dụng giao dịch vào sổ cái nếu hợp lệ và số dư đủ.

## Yêu cầu
- Python 3.10+ (không phụ thuộc thư viện bên ngoài).

## Hướng dẫn nhanh
```bash
python coin.py genkey                # sinh toy keypair
python coin.py faucet <address> 100  # nạp thử ví
python coin.py send <sk> <to> 5      # tạo & áp dụng giao dịch
python coin.py balance <address>     # xem số dư
python -m unittest -v                # chạy test
```

## Nhiệm vụ bắt buộc
1. Đọc và hiểu lớp `Ledger` và hàm `build_tx`.
2. Gửi thành công 2 giao dịch nối tiếp (cùng địa chỉ nguồn) với `nonce` tăng dần.
3. Đọc và hiểu các test cases trong file `test_blockchain.py`.

## Mở rộng (tuỳ chọn nếu có thời gian)
- Lưu sổ cái ra file JSON.
- Chống double-spend trong cùng block bằng hàng đợi tạm.

# P3 - Memo kết quả và quyết định

Ngày lập: 24/11/2026. Run `eed008040d6c6d18`. Đây là nghiên cứu hồi cứu năm 2025, không phải lợi nhuận giao dịch thật.

## Kết quả cần nhớ

Mỗi tài sản/chính sách có sleeve riêng 100.000 USDT. Holdout là 01/10-31/12/2025, reset vốn đầu kỳ và đóng vị thế cuối kỳ.

| Chính sách | BTC net P&L | ETH net P&L |
|---|---:|---:|
| Giữ carry liên tục | 374.27 | 311.46 |
| Bật/tắt theo funding gần nhất | -8,137.40 | -10,252.43 |
| Dự báo bằng mean 9 kỳ | -1,255.39 | -1,147.12 |
| Ridge AR(1) | -4,334.24 | -3,858.67 |

Threshold đổi vị thế quá nhiều nên phí lớn hơn funding thu được. Dự báo mượt hơn giảm đổi vị thế, nhưng vẫn lỗ và chưa vượt carry liên tục. Sai số dự báo thấp hơn không tự động tạo lợi nhuận tốt hơn. Không chỉnh threshold sau khi nhìn holdout; nếu thử hysteresis/cost-aware entry thì phải lập study mới.

## Bằng chứng đã có

- BTC/ETH: đủ 1.095 funding events và 1.095 bars cho từng stream spot/perp/mark trong 2025; không thiếu/trùng kỳ.
- 93 funding events BTC tháng 1 khớp archive/API về cả timestamp và rate.
- 18 tests; 13.140 dòng ledger cho 6 policy variants × 3 partitions × 2 assets. Sai số đối soát tối đa dưới 1e-9 USDT.
- Freeze hash trước khi xem kết quả; ba partition; paired block bootstrap; cost ×1/×2/×3 và delay 1/2/3 events.
- Workbook có công thức và golden case độc lập; dashboard giữ các kết quả âm.

## Giới hạn và bước tiếp

Giá tham chiếu là open bar 8 giờ, funding có timestamp thực; độ lệch tối đa 16 ms. Fill, fee tier và flat maintenance là giả định. Bar-high margin chỉ là proxy, không chứng minh không bị thanh lý. Đơn vị P&L là USDT, không phải USD bảo đảm. Chưa có bằng chứng depth/capacity, tier margin lịch sử hay forward track record.

Paper collector chỉ đọc dữ liệu công khai, ghi vị thế giả lập, không gửi lệnh và không cần API key. Không thể tạo trước một chuỗi kết quả tương lai. Trạng thái triển khai/runner thực tế được ghi riêng trong `docs/STATUS_VI.md`.

Kết luận: giữ carry liên tục làm benchmark; bác bỏ threshold đơn giản ở bộ giả định chi phí hiện tại. Giá trị portfolio của P3 là một quy trình nghiên cứu kiểm chứng được, bao gồm kết quả âm và giới hạn thực thi.

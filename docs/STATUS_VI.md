# Trạng thái P3 - 24/11/2026

Release 0.2.0 đã có dữ liệu thật, nghiên cứu hồi cứu và kết quả âm được giữ nguyên. Không còn là gói synthetic-only.

| Hạng mục | Trạng thái |
|---|---|
| BTC/ETH spot, perp, mark, funding 2025 | Đủ 1.095 event/stream/asset; audit không thiếu/trùng |
| Archive/API đối chiếu | 93/93 BTC tháng 1 khớp timestamp/rate |
| Hai ví và ledger | Đối soát từng event; 13.140 dòng, sai số <1e-9 USDT |
| Study | Protocol và freeze trước khi xem return; dev/validation/holdout |
| Forecast | Last/mean/ridge; train-only, MAE/RMSE và matched net economics |
| Sensitivities | Cost ×1/×2/×3; delay 1/2/3; paired 7-day block intervals |
| Notebook | 4 notebook đã thực thi |
| Excel | Golden case bằng công thức, thay input có recalc, audit 4 chênh lệch bằng 0; market snapshot thật |
| Report | PDF 10 trang, Markdown, memo VI |
| Dashboard | Snapshot holdout có controls, CSV và calculator; đang triển khai và kiểm tra trình duyệt |
| Paper | Code read-only và tests hoàn tất; snapshot/runner thực tế đang kiểm tra |
| Kiểm thử | 18 tests pass |

Chưa thể khẳng định: fill thực, depth/capacity, historical margin tiers, venue-exact liquidation, lợi nhuận tương lai hoặc forward track record. Không đặt lệnh, không lấy API key.

Mọi thay đổi engine/model sau khi xem holdout cần study mới. Không gọi lại holdout đã dùng là untouched. Public export không chứa raw/normalized market snapshots hay price-level ledger. Private package giữ nguồn cho việc tái lập.

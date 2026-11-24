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
| Report | PDF 10 trang, Markdown, memo tiếng Anh |
| Dashboard | Đã live: https://thvh2006.github.io/crypto-carry-execution-lab/ ; controls, calculator và CSV 276 dòng đã kiểm tra |
| Paper | Code và tests hoàn tất; runner GitHub bị HTTP 451 tại Binance futures; cron đã bỏ, chỉ còn manual trigger |
| Kiểm thử | 18 tests pass local và GitHub CI |

Chưa thể khẳng định: fill thực, depth/capacity, historical margin tiers, venue-exact liquidation, lợi nhuận tương lai hoặc forward track record. Không đặt lệnh, không lấy API key.

Mọi thay đổi engine/model sau khi xem holdout cần study mới. Không gọi lại holdout đã dùng là untouched. Public export không chứa raw/normalized market snapshots hay price-level ledger. Private package giữ nguồn cho việc tái lập.

## Bằng chứng vận hành

- Source: https://github.com/thvh2006/crypto-carry-execution-lab
- CI thành công: https://github.com/thvh2006/crypto-carry-execution-lab/actions/runs/45386486848
- Paper run thất bại, không có state/artifact thành công: https://github.com/thvh2006/crypto-carry-execution-lab/actions/runs/45386689077 ; log HTTP 451 ở futures bookTicker. Không né giới hạn truy cập.
- Dashboard hiển thị đúng ETH continuous net 311,46 USDT; calculator đổi rate 0,02% cho net -154 USDT; CSV tải được 276 dòng. Không có console error trong lần kiểm tra.

Đây là bản nghiên cứu hồi cứu hoàn chỉnh; forward paper tự động và track record tương lai chưa hoàn thành do chặn truy cập máy chủ. Không ghi giả một chuỗi lợi nhuận paper.

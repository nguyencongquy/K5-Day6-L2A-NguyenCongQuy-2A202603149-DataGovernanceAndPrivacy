# T02 — đối chiếu yêu cầu cuối

Một challenge T02, không làm cả 14. Đối chiếu README gốc và docs/tracks/T02.md.

| Yêu cầu | Kết quả/bằng chứng | Phạm vi chính xác |
|---|---|---|
| 5 bước tự động + 1 lệnh | PASS: make reproduce; fresh_checkout_check.json | load/process/rank/review/decide, offline |
| Đúng input và output | PASS: 96 score, 40 eval, top-20; giữ split và manifest | Không đọc GT ẩn |
| Baseline một Laplacian toàn ảnh | PASS: score=max(0,1-L/80); cutoff 0.5 tương đương L≤40 | Không dùng random thay baseline T02 |
| Cùng pool/budget/seed, metric chuẩn | PASS trên benchmark nội bộ 60 mẫu; evaluator không sửa | Recall hòa ở trần budget; không giả cải thiện |
| Policy không tune theo eval | PASS: AST features/score_features trùng commit đóng băng | Sửa stage review không thay scoring |
| Ba failure mode bắt buộc | PASS: required_failure_cases.md, CSV và ảnh dev | Tách lỗi quan sát được, counterfactual và stress; không giả GT |
| Nhánh +24h: camera threshold hoặc ROI | PASS: glare dùng ROI tile 16x16 | Giới hạn small glare đã minh họa |
| Kiểm 10 ảnh out-of-domain | PASS: pack đóng băng trước đo; ood_results.csv | Synthetic shifted-domain stress; không gọi ảnh thật |
| Human review + audit | PASS: owner đã xác nhận 20 quyết định; owner_review.json | 10 RECAPTURE, 2 KEEP, 8 ESCALATE |
| Owner/reason + gate | PASS: HOLD / REVIEW_ESCALATED | Không đổi 8 ca chưa rõ sang KEEP để đóng bài |
| Raw, final, override, diff | PASS: raw_predictions.csv, ranked_review.csv; override có regression test | review_status/final_action tách dự đoán và duyệt cuối |
| ≥2 test + failure case | PASS: 56 passed, 39 GT-dependent skipped | 9 test riêng T02 gồm stale CSV và failed rerun |
| Clean start và tái lập | PASS: checkout mới không có out/, venv độc lập, raw/final khớp chính xác | Cùng wheel environment; drift Conda được lưu riêng |
| Report + đóng góp Git | PASS: group_report.md, metric_contract.md, team_contributions.csv | Làm cá nhân, không nhận code starter là tự viết |
| 3–5 slide demo | PASS: 5 slide PowerPoint có chart editable | Chưa giả hoạt động trình bày tại lớp |

## Phần do quy trình lớp quyết định

- GT ẩn và official hidden score do giảng viên chạy. Thiếu overlay không phải lý do tự tạo đáp án trong gt/.
- Showcase/debate cần diễn ra thực tế; bộ slide chuẩn bị không đồng nghĩa đã thuyết trình.
- Tag lưu timestamp thực, không backdate; tag tên demo-180m không tự chứng minh bonus thời gian.
- Không cam kết điểm số, real-world accuracy hoặc compliance pháp luật từ PoC.

## Ý nghĩa HOLD

Đã review đủ 20 ảnh. Tám ca được owner chuyển cấp, nên HOLD là kết quả cuối hợp lệ của risk gate. `pred_action=KEEP` không thay `final_action=HOLD`; các ảnh ngoài queue chưa được duyệt release. Audit append-only ghi lần áp dụng lại CSV khi tái lập, không cộng sự kiện lặp thành số ảnh review mới.

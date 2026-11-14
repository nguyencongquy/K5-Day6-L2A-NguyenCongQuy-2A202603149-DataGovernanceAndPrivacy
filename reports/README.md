# Evidence hiện tại — T02

`metrics_baseline.json`, `metrics_poc.json` và bảng so sánh hiện dùng bộ controlled-transform nội bộ 60 mẫu, không phải hidden GT fixture. Tái lập bằng `make reproduce`; phạm vi, seed và source nằm trong JSON và group_report.md.

- `ood_results.csv`: 10 ảnh stress synthetic mới; input/reference đã commit trước đo.
- `required_failure_cases.md`: đủ ba tình huống bắt buộc, kèm ảnh dev và phép đo.
- `owner_review.json` + `review_queue_reviewed.csv`: xác nhận thực tế 20 quyết định; 8 ESCALATE tiếp tục HOLD.
- `clean_environment_check.json` + `fresh_checkout_check.json`: venv độc lập và checkout mới đã kiểm chứng.
- Official evaluation do giảng viên có overlay GT chạy. Khi có, lưu kết quả riêng để không lẫn với benchmark nội bộ.

---

# reports/

| File | Ai tạo | Cách tạo |
|---|---|---|
| `group_report.md` | nhóm | điền template |
| `metric_contract.md` | nhóm | điền ở phút 30 |
| `metrics_baseline.json` | **script** | `python -m src.evaluate --track tXX --pred out/baseline/<file> --run-name baseline --out reports/metrics_baseline.json` |
| `metrics_poc.json` | **script** | `python -m src.evaluate --track tXX --pred out/poc/<file> --run-name poc --out reports/metrics_poc.json` |
| `table1_baseline_vs_poc.md` | **script** | `python -m src.compare reports/metrics_baseline.json reports/metrics_poc.json --out reports/table1_baseline_vs_poc.md` |
| `review_queue.csv` | pipeline + reviewer | copy từ `out/poc/review_queue.csv` sau khi review (có cột reviewer/decision) |
| `decision_log.csv` | pipeline | copy từ `out/poc/decision_log.csv` |
| `team_contributions.csv` | nhóm | khớp với `git shortlog -sne --all` |

Các file metrics/table **không được sửa tay** — giảng viên sẽ chạy lại lệnh để đối chiếu.

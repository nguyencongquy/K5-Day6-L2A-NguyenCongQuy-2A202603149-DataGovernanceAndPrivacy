# Metric contract — T02 (policy cố định)

- Chủ sở hữu: NguyenCongQuy; làm cá nhân, mã nội bộ SOLO-2A202603149.
- Primary: Defect Recall@B; higher better; đơn vị image; B=20.
- Numerator: số ảnh lỗi trong top-20; denominator: tổng ảnh lỗi trên pool eval.
- Secondary: Precision@B; defect-type accuracy; false alarm theo light; runtime/100 ảnh.
- Matching: image_id; output đủ mọi ID, không đổi split/pool.
- Fixture: 96 input, eval 40; GT ẩn chưa có, không tune trên eval labels.
- Benchmark riêng: 60 controlled transforms/12 scene, 48 positive; không phải fixture GT.
- Baseline: score=max(0,1-Laplacian/80); score cutoff 0.5 tương đương Laplacian≤40; PoC max bốn feature, ngưỡng trong src/pipeline.py.
- Các ngưỡng là giả định heuristic, không tuyên bố calibrate bằng dev labels.
- Freeze: policy được viết trước lần benchmark đầu; sau lỗi unit test, sửa denominator sharpness trước benchmark, không tune sau kết quả.
- Seed chạy 42; generator internal 20261114; scene bootstrap 500 lượt, seed 42.
- Slices: defect type và light; controlled benchmark chỉ có light=controlled, chưa đủ hard slices ảnh thật.
- Gate: HOLD tới khi toàn queue có reviewer và quyết định kết thúc hợp lệ.
- Không thay đổi metric/evaluator, không diễn giải primary hòa là cải tiến.

## Bổ sung kiểm chứng, không thay policy

- Giữ nguyên features/score_features và mọi threshold; AST đối chiếu commit 9f15f04 ở scoring_freeze_check.json.
- Giữ nguyên bộ internal 60 mẫu và evaluator; lịch sử Conda ở history/conda_v1. Kết quả canonical dùng venv PyPI tách biệt, libjpeg 6.2.
- OOD riêng: 10 ảnh procedural inspection-board, source camera/geometry/resolution mới; toàn bộ input + reference engineering expectations đã commit trước đo (9f15f04).
- Báo action agreement/false KEEP/false RECAPTURE trên OOD; không dùng Recall@20 khi N=10, không tuyên bố real-world OOD accuracy.
- Ba failure mode bắt buộc: ảnh dev img_18_1 (night useful), img_18_2 (small glare), img_00_0 và sweep img_00_1 (cam_B optics). Không giả nhãn GT cho quan sát.
- Human review chỉ xác nhận khi owner đã trả lời thực tế; skip/escalate tiếp tục HOLD. Hidden evaluation do giảng viên chạy, không phải dữ liệu học viên phải tự tạo.

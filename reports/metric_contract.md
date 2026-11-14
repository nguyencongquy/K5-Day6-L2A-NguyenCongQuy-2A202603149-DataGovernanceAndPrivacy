# Metric contract — T02 (policy cố định)

- Chủ sở hữu: NguyenCongQuy; làm cá nhân, mã nội bộ SOLO-2A202603149.
- Primary: Defect Recall@B; higher better; đơn vị image; B=20.
- Numerator: số ảnh lỗi trong top-20; denominator: tổng ảnh lỗi trên pool eval.
- Secondary: Precision@B; defect-type accuracy; false alarm theo light; runtime/100 ảnh.
- Matching: image_id; output đủ mọi ID, không đổi split/pool.
- Fixture: 96 input, eval 40; GT ẩn chưa có, không tune trên eval labels.
- Benchmark riêng: 60 controlled transforms/12 scene, 48 positive; không phải fixture GT.
- Baseline: global Laplacian threshold 80; PoC max bốn feature, ngưỡng trong src/pipeline.py.
- Các ngưỡng là giả định heuristic, không tuyên bố calibrate bằng dev labels.
- Freeze: policy được viết trước lần benchmark đầu; sau lỗi unit test, sửa denominator sharpness trước benchmark, không tune sau kết quả.
- Seed chạy 42; generator internal 20261114; scene bootstrap 500 lượt, seed 42.
- Slices: defect type và light; controlled benchmark chỉ có light=controlled, chưa đủ hard slices ảnh thật.
- Gate: HOLD tới khi toàn queue có reviewer và quyết định kết thúc hợp lệ.
- Không thay đổi metric/evaluator, không diễn giải primary hòa là cải tiến.

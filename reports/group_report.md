# Day06 · T02 — Raw QC Triage

## 00 · Thông tin

- Học viên: Nguyễn Công Quý — MSSV 2A202603149.
- Hình thức: cá nhân; mã làm việc nội bộ `SOLO-2A202603149`, cần giảng viên xác nhận cách nộp cá nhân.
- Repo: https://github.com/nguyencongquy/K5-Day6-L2A-NguyenCongQuy-2A202603149-DataGovernanceAndPrivacy
- Phạm vi: pipeline CPU offline, baseline, PoC, benchmark nội bộ, ablation, tests và giao diện review.
- Trạng thái: **HOLD — còn chờ người sở hữu xác nhận review 20 ảnh và đánh giá GT ẩn**. Không tuyên bố hoàn thành phần review hay hidden evaluation.
- Chưa tạo tag `demo-180m`/`final-24h`; không có bằng chứng thời hạn lớp để xác nhận bonus theo thời gian.

## 01 · Vấn đề và quyết định

Người kiểm dữ liệu có ngân sách hữu hạn. Nếu chỉ dựa vào độ nét toàn ảnh, ảnh đêm còn hữu ích có thể bị loại, trong khi vùng nhỏ bị lóa có thể bị bỏ sót. Mục tiêu là ưu tiên 20 ảnh nghi lỗi để người kiểm đưa ra KEEP/RECAPTURE hoặc chuyển cấp khi chưa rõ, thay vì tự động xóa ảnh.

Input là ảnh, metadata và manifest. Output gồm `ranked_review.csv`, `review_queue.csv`, contact sheet, dự đoán gốc, audit log và decision log. KEEP/RECAPTURE là gợi ý; không thay đổi hay xóa file nguồn. Cổng tổng giữ HOLD khi còn thiếu review, skip/escalate, review không tên hoặc dữ liệu không hợp lệ. GO chỉ có nghĩa kết quả triage đã được review; không chứng nhận dữ liệu tuân thủ pháp luật hay mọi ảnh đều đạt chất lượng.

## 02 · Dữ liệu và provenance

Fixture T02 có 96 ảnh synthetic, 320×180, 24 cảnh gốc; split do đề bài cung cấp, 40 ảnh eval. Không chia lại theo từng ảnh. Ảnh synthetic CC0; không dùng ảnh cá nhân, biển số thật hoặc model tải ngoài. `make verify` kiểm toàn repo: 14 manifests, 0 failing. Không đọc `fixtures/*/gt/`; runner bật cả offline guard và GT guard.

Benchmark nội bộ là **bộ riêng**, tạo bằng `tools/evaluate_internal_t02.py`: 12 cảnh mới, mỗi cảnh 5 biến thể (none/blur/dark/glare/compression), tổng 60 mẫu, 48 mẫu có phép biến đổi. Nhãn mô tả phép biến đổi đã áp dụng, **không phải gold set về mức độ sử dụng thực tế**. Seed sinh bộ này 20261114; seed chạy và bootstrap 42. Không dùng ID/tên ảnh fixture để suy đoán nhãn.

## 03 · Thiết kế

Luồng: verify manifest → đọc ảnh → tính feature → xếp hạng top-20 trong split eval → xuất HTML/CSV → nhận quyết định review → áp override, audit → HOLD/GO.

Baseline dùng duy nhất Laplacian variance, score `max(0, 1 - Laplacian/80)`. Ngưỡng toàn ảnh 80 là giả định thiết kế, không tuyên bố được tối ưu bằng nhãn dev.

PoC dùng max của bốn tín hiệu, giới hạn trong [0,1]:

- Blur: Laplacian variance chia `max(gray variance, 100)`; ngưỡng 0.04. Mẫu số sàn tránh ảnh gần đồng màu tạo tỷ lệ lớn do nhiễu lượng tử.
- Dark: brightness trung bình dưới 18. Ngưỡng thấp nhằm hạn chế loại ảnh đêm còn hữu ích; vẫn có thể báo nhầm.
- Glare: tỷ lệ pixel >245 trong tile 16×16 cao nhất; bắt đầu nghi ngờ khi >0.65.
- Compression: độ nhảy cường độ tại biên khối 8 pixel trừ trung bình độ nhảy; chuẩn hóa bằng 12.

Score ≥0.5 gợi ý RECAPTURE, thấp hơn gợi ý KEEP. Mọi ngưỡng là heuristic cố định, chưa được chứng minh tối ưu. Không chỉnh ngưỡng sau khi xem benchmark. Sắp xếp hòa điểm theo image_id để tái lập; tránh dùng hash order.

## 04 · Baseline và PoC — kết quả nội bộ

**Bảng dưới chỉ dùng bộ controlled-corruption 60 mẫu, không phải điểm 96 ảnh fixture hay hidden test.** Hai cách dùng cùng pool, B=20, cùng ảnh và seed. Metrics gọi evaluator chuẩn `eval_t02`; JSON/table sinh bằng script.

Baseline: `baseline` (git cf30d35, seed 42) · PoC: `poc` (git cf30d35, seed 42)

| Metric (unit) | Slice | Baseline | PoC | Δ abs | Δ rel | Better | N |
|---|---|---|---|---|---|---|---|
| **Defect Recall@B** (GT defects in top-B / GT defects) | all | 0.4167 | 0.4167 | 0.0000 | +0.0% | higher | 60 |
| Precision@B (GT defects in top-B / B) | all | 1.0000 | 1.0000 | 0.0000 | +0.0% | higher | 60 |
| Defect-type accuracy (GT defects) (fraction) | all | 0.2500 | 0.5208 | 0.2708 | +108.3% | higher | 48 |
| False alarm in top-B (clean images in top-B / clean images) | light=controlled | 0.0000 | 0.0000 | 0.0000 | baseline=0 | lower | 60 |
| Runtime / 100 items (s) | all | 0.1001 | 0.0997 | | | lower | |

Primary metric bằng nhau. Cả hai đạt trần budget 20/48; kết quả này không chứng minh PoC cải thiện khả năng truy hồi lỗi. Độ đúng loại lỗi là chỉ số phụ; mức tăng trên bộ biến đổi đơn giản không bảo đảm chuyển sang ảnh thật.

## 05 · Protocol và độ bất định

Defect Recall@20 = số ảnh lỗi nằm trong top-20 / tổng ảnh lỗi của pool eval. Precision@20 = số ảnh lỗi trong top-20 / 20. Ghép bằng image_id. Pipeline vẫn xuất đủ 96 dự đoán fixture; hàng đợi review chỉ chọn trong 40 ảnh eval để khớp budget chấm.

Benchmark bootstrap 500 lần theo cụm scene, không bootstrap từng biến thể độc lập. CI recall nội bộ: [0.4166666666666667, 0.4166666666666667]. Khoảng suy biến do cả top-20 đều là positive và mỗi scene có 4 lỗi; **không diễn giải thành chắc chắn trên dữ liệu thực tế**.

Chưa có GT ẩn của giảng viên. Không ghi metric hidden, không tự tạo file giả trong gt/. Khi giảng viên cung cấp overlay, chạy evaluator riêng trên fixture; không ghi đè số nội bộ mà không đổi tên/phạm vi báo cáo.

## 06 · Slices, ablation và failure cases

Slices nội bộ theo loại biến đổi có N=12 mỗi loại; xem `slices_poc.csv`. Top-20 có recall glare=1, blur=2/3, dark=0, compression=0. Hai slice dark/compression bị bỏ khỏi budget dù score có thể vẫn gợi ý lỗi.

Failure 1: compression có thể giữ cạnh mạnh hoặc trùng cạnh cấu trúc 8 pixel; feature blockiness thiếu ổn định. Trong benchmark, không ảnh compression nào lọt top-20. Cần thử nhiều mức JPEG và vùng có texture trước khi thay policy.

Failure 2: dùng max score khiến glare và blur chiếm toàn budget; các ảnh dark bị bỏ sau điểm hòa/budget. Không được kết luận dark không có lỗi. Có thể nghiên cứu quota theo slice, nhưng phải so với baseline trên cùng pool và budget ở thí nghiệm mới.

Failure 3: vùng trắng hợp lệ (tuyết, bảng trắng, bầu trời) có thể bị gọi glare; ảnh đêm có tín hiệu hữu ích có thể bị báo dark. Đây là rủi ro thiết kế chưa có bộ natural hard-negative đủ rộng để định lượng. Đối chiếu trực quan 20 ảnh fixture cũng xác nhận artifact nén ở một số ảnh được gợi ý KEEP; xem `visual_review.md`. Đây là phát hiện cần xác minh theo policy, không phải nhãn GT hoặc điểm lỗi chính thức.

Ablation bỏ glare, giữ nguyên các thành phần khác:

Baseline: `ablation_no_glare` (git cf30d35, seed 42) · PoC: `poc` (git cf30d35, seed 42)

| Metric (unit) | Slice | Baseline | PoC | Δ abs | Δ rel | Better | N |
|---|---|---|---|---|---|---|---|
| **Defect Recall@B** (GT defects in top-B / GT defects) | all | 0.4167 | 0.4167 | 0.0000 | +0.0% | higher | 60 |
| Precision@B (GT defects in top-B / B) | all | 1.0000 | 1.0000 | 0.0000 | +0.0% | higher | 60 |
| Defect-type accuracy (GT defects) (fraction) | all | 0.2708 | 0.5208 | 0.2500 | +92.3% | higher | 48 |
| False alarm in top-B (clean images in top-B / clean images) | light=controlled | 0.0000 | 0.0000 | 0.0000 | baseline=0 | lower | 60 |
| Runtime / 100 items (s) | all | 0.1005 | 0.0997 | | | lower | |

Ablation này là kiểm tra nội bộ, không phải hidden test. Primary không đổi, phân loại loại lỗi giảm; không nhận bonus chưa được giảng viên xác nhận.

## 07 · Review và audit

`reports/contact_sheet.html` chứa 20 ảnh ưu tiên, score, loại lỗi và gợi ý hành động. Trạng thái hiện tại: **0 review của học viên đã nhập**. Không dùng các reviewer giả từ unit test làm bằng chứng review thật; các test chạy trong thư mục tạm.

Reviewer nhập tên, chọn approve/edit/reject/escalate/skip và ghi lý do. Với edit/reject phải nhập KEEP hoặc RECAPTURE. Export CSV, chép vào `out/poc/review_queue_reviewed.csv`, chạy lại PoC. Pipeline kiểm ID thuộc queue, không trùng, action hợp lệ; giữ raw và final riêng, ghi JSONL append-only. Không thay đổi score bằng override hành động để tránh làm sai metric ranking. File review cũ có score/action/evidence khác queue hiện tại bị từ chối. File `visual_review_recommendations.csv` ghi 10 đề nghị RECAPTURE, 8 ESCALATE, 2 KEEP; chưa dùng làm chữ ký chủ sở hữu hoặc gold labels.

## 08 · Tái lập và tests

```bash
make setup
sh tools/reproduce_t02.sh
```

Hoặc chạy từng phần:

```bash
make baseline TRACK=t02
make run TRACK=t02
.venv/bin/python -m tools.evaluate_internal_t02
.venv/bin/python -m pytest -ra
```

Tests: **55 passed, 39 skipped in 5.01s**. 39 skipped là tests cần overlay GT; không tính là đã vượt qua kiểm tra hidden. Test riêng kiểm độ nét sau blur, ảnh quá nhỏ, output offline tái lập, HOLD khi chưa review, override/audit hợp lệ và từ chối review không tên. Test starter chờ NotImplemented đã đổi sang kiểm pipeline triển khai trả exit 0; không xóa kiểm tra offline/GT hoặc hạ điều kiện evaluator.

Máy: {'python': '3.13.9', 'platform': 'macOS-27.0.1-arm64-arm-64bit-Mach-O', 'processor': 'arm'}. Runtime fixture PoC: 0.2068 giây cho 96 ảnh trong lần đo; xem run_info. Runtime benchmark trong bảng là bộ khác, không trộn hai phép đo. Môi trường triển khai ban đầu dùng venv với system-site-packages; `requirements-lock.txt` ghi phiên bản dependency. Kết quả kiểm tra venv tách biệt, nếu đã chạy xong, nằm trong `clean_environment_check.json`; không suy ra đã kiểm chứng trên máy khác.

## 09 · Giới hạn và quyền riêng tư

Không dùng pretrained model hoặc API; demo chạy offline. Chỉ dùng fixtures và ảnh synthetic tự sinh. Đây là kiểm soát kỹ thuật PoC, không kết luận đạt GDPR hoặc luật Việt Nam. Chưa chứng minh hiệu quả trên ảnh thật, camera mới, đêm thật, 10 ảnh out-of-domain hay GT giảng viên. Khi scale 10× cần đo lại runtime, giới hạn kích thước input và năng lực review.

## 10 · Đóng góp và trạng thái nộp

Làm cá nhân: Nguyễn Công Quý chịu trách nhiệm integration, thiết kế, QA và báo cáo. `team_contributions.csv` ghi phần việc và Git identity đã dùng ở bài Day05. Commit nguồn cho lần chạy này: `cf30d35`; run_info ghi SHA tương ứng. Trạng thái push xác nhận bằng Git remote, không dùng tag phút 180 khi không có bằng chứng. Không có thành viên hay hoạt động showcase/debate giả.

Còn trước khi nộp: xác nhận review 20 ảnh synthetic trong queue, xuất CSV, chạy lại; xác nhận yêu cầu nộp cá nhân; gửi link repo/report trên LMS sau khi kiểm tra trạng thái cuối. GT ẩn và showcase do quy trình lớp quyết định. Phần mềm chạy được không đồng nghĩa toàn bộ rubric đã hoàn thành.

## 11 · Tài liệu

Ngày đọc: 2026-11-14.

- [Đề T02](../docs/tracks/T02.md): baseline Laplacian, budget, metric và failure modes.
- [README lab](../README.md): contract offline, reproducibility, rubric, GT guard.
- [Hạ tầng review](../src/common/review.py): schema, override và audit trail; tái sử dụng để giữ lịch sử quyết định.
- [Evaluator chuẩn](../src/metrics/tracks.py): định nghĩa metric; giữ nguyên để so sánh nhất quán.

## Kiểm tra môi trường bổ sung

Venv trống riêng đã khởi tạo, nhưng cài dependency dừng trong lúc tải SciPy chậm; không báo PASS cho cold install. Pipeline và tests đã chạy thành công với output mới trong môi trường hiện có. Xem `clean_environment_check.json`.

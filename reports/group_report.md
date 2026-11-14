# Day06 · T02 — Raw QC Triage

## 00 · Thông tin và phạm vi

Nguyễn Công Quý · MSSV 2A202603149 · làm cá nhân, mã nội bộ SOLO-2A202603149. Repo: https://github.com/nguyencongquy/K5-Day6-L2A-NguyenCongQuy-2A202603149-DataGovernanceAndPrivacy. Chọn một challenge T02 theo README; không làm cả 14, không có yêu cầu bốc thăm trong repo. Cần tuân theo hướng dẫn lớp nếu giảng viên phân đề riêng hoặc yêu cầu nhóm.

Source commit cho lần đo: `5b9b38d`; snapshot code/config có SHA256 trong `source_snapshot.json`. Không backdate commit/tag để nhận bonus thời gian. Bộ demo 5 slide đính kèm; không tuyên bố đã trình bày hoặc tham gia debate khi chưa có bằng chứng.

## 01 · Bài toán và điều kiện quyết định

Người kiểm chỉ có ngân sách B=20 ảnh. Input là ảnh, camera/light/split và manifest; output gồm score xếp hạng, gợi ý KEEP/RECAPTURE, queue, HTML review, override/diff, audit và decision. Năm bước: load+provenance → process → rank → review → decide. Không xóa hoặc sửa ảnh nguồn.

GO chỉ xác nhận kết quả triage đã được review đầy đủ, không chứng nhận mọi ảnh đạt chất lượng hay tuân thủ pháp luật. Thiếu review, skip hoặc escalate giữ HOLD. Input/manifest sai trả lỗi; rerun khởi đầu bằng HOLD để không để sót GO của lần trước. Owner và reason_code bắt buộc.

## 02 · Dữ liệu, split và provenance

- Fixture T02: 96 ảnh synthetic CC0, 24 cảnh gốc; 56 dev, 40 eval. Giữ split theo cảnh do đề cung cấp. `manifest_check.txt` kiểm 14 manifest gốc, không có lỗi. Pipeline không đọc GT ẩn, không dùng ID/file suffix để chấm điểm.
- Benchmark nội bộ: 12 cảnh tự sinh × 5 biến thể = 60 mẫu; 48 mẫu có phép biến đổi. Nhãn là **phép biến đổi được áp dụng**, không phải human usability gold. Giữ nguyên bộ, B=20, seed và evaluator; không đổi testset để tăng số.
- OOD: 10 ảnh synthetic inspection-board với hình học, camera ID, texture và kích thước khác road fixture. Ảnh, reference expectations và manifest đã commit trước khi đo (`9f15f04`). Không gọi đây là ảnh BDD thật hoặc bằng chứng generalization ngoài đời. `data/real` là tùy chọn và không sử dụng.

`src.main` bật offline/GT guard. Không pretrained model, không API ngoài, không PII thật. Khi cần nhãn chính thức, giảng viên chạy hidden evaluation; học viên không phải lấy hoặc tạo giả gt/.

## 03 · Thiết kế và policy đóng băng

Baseline: score=max(0,1−Laplacian variance/80), một ngưỡng toàn ảnh, dùng hàm chung của lab. Tham số 80 là mốc score về 0; cutoff hành động score≥0.5 tương đương Laplacian≤40. PoC lấy max của bốn tín hiệu trong [0,1]: sharpness chuẩn hóa tương phản (Laplacian/max(gray variance,100), ngưỡng 0.04); brightness thiếu sáng dưới 18; saturated fraction >0.65 trên tile ROI 16×16; chênh độ nhảy tại biên khối JPEG 8 pixel chuẩn hóa bằng 12. Score≥0.5 gợi ý RECAPTURE.

Ngưỡng là heuristic cố định; không tuyên bố được tối ưu trên dev labels. Không tune bằng nhãn eval. Sau review eval ở phiên trước, giữ nguyên feature/threshold; chỉ bổ sung kiểm chứng và sửa an toàn review. `scoring_freeze_check.json` so hàm scoring với commit đóng băng. Cam_B sensitivity chỉ dùng dev và không cập nhật policy sau sweep. ROI glare đáp ứng nhánh ROI ở yêu cầu +24h; phân tích dưới đây cho thấy hạn chế của ROI này.

## 04 · Baseline vs PoC

**Bảng chỉ áp dụng bộ controlled-transform nội bộ, không phải điểm trên 96 fixture hoặc hidden GT.** Pool, B=20, seed=42 và cách tính giống nhau. JSON/table do script + evaluator chuẩn sinh, không gõ tay.

Baseline: `baseline` (git 5b9b38d, seed 42) · PoC: `poc` (git 5b9b38d, seed 42)

| Metric (unit) | Slice | Baseline | PoC | Δ abs | Δ rel | Better | N |
|---|---|---|---|---|---|---|---|
| **Defect Recall@B** (GT defects in top-B / GT defects) | all | 0.4167 | 0.4167 | 0.0000 | +0.0% | higher | 60 |
| Precision@B (GT defects in top-B / B) | all | 1.0000 | 1.0000 | 0.0000 | +0.0% | higher | 60 |
| Defect-type accuracy (GT defects) (fraction) | all | 0.2500 | 0.5208 | 0.2708 | +108.3% | higher | 48 |
| False alarm in top-B (clean images in top-B / clean images) | light=controlled | 0.0000 | 0.0000 | 0.0000 | baseline=0 | lower | 60 |
| Runtime / 100 items (s) | all | 0.1004 | 0.1014 | | | lower | |

Primary bằng nhau và đều chạm trần B/#positive=20/48. Vì vậy chưa chứng minh PoC cải thiện truy hồi lỗi. Secondary loại lỗi tăng trên bộ biến đổi đơn giản; không suy ra tốt hơn trên ảnh thật. Báo cả số không tăng, không dùng tỷ lệ cải thiện khi baseline=0.

Ablation bỏ glare, giữ các thành phần khác:

Baseline: `ablation_no_glare` (git 5b9b38d, seed 42) · PoC: `poc` (git 5b9b38d, seed 42)

| Metric (unit) | Slice | Baseline | PoC | Δ abs | Δ rel | Better | N |
|---|---|---|---|---|---|---|---|
| **Defect Recall@B** (GT defects in top-B / GT defects) | all | 0.4167 | 0.4167 | 0.0000 | +0.0% | higher | 60 |
| Precision@B (GT defects in top-B / B) | all | 1.0000 | 1.0000 | 0.0000 | +0.0% | higher | 60 |
| Defect-type accuracy (GT defects) (fraction) | all | 0.2708 | 0.5208 | 0.2500 | +92.3% | higher | 48 |
| False alarm in top-B (clean images in top-B / clean images) | light=controlled | 0.0000 | 0.0000 | 0.0000 | baseline=0 | lower | 60 |
| Runtime / 100 items (s) | all | 0.0999 | 0.1014 | | | lower | |

Đây là ablation nội bộ; không tự nhận hidden-test/debate bonus. Các JSON cũ của môi trường Conda giữ trong `history/conda_v1` để đối chiếu.

## 05 · Protocol, metric và slices

Recall@20 = lỗi thật trong top-20 / tổng lỗi thật của pool eval; Precision@20 = lỗi thật trong top-20 /20. Ghép bằng image_id, cùng pool/split/seed. Xuất đủ 96 score, queue chỉ lấy từ 40 eval để đúng budget chấm. Không dùng override hành động để thay score, không dùng review queue tự chọn làm bộ GT đại diện cho toàn dataset.

Benchmark sinh seed=20261114; run/cluster bootstrap seed=42. Bootstrap 500 lượt theo scene, giữ các biến thể cùng cụm; CI nội bộ [0.4166666666666667, 0.4166666666666667]. CI suy biến do trần budget và cấu trúc artificial set; không diễn giải thành chắc chắn ngoài đời.

Slices theo defect ở `slices_poc.csv`; camera/light/split mô tả fixture ở `fixture_descriptive_slices.csv`. Khi chưa có nhãn fixture, số RECAPTURE theo camera chỉ là phân bố dự đoán, không phải false-positive rate. Bộ nội bộ không có đủ light slices thật; limitations được giữ rõ.

## 06 · Ba failure mode bắt buộc và 10 ảnh OOD

| case | image_id | camera_id | light | baseline_action | poc_action |
|---|---|---|---|---|---|
| night_useful | img_18_1 | cam_B | night | KEEP | KEEP |
| small_glare | img_18_2 | cam_B | night | KEEP | KEEP |
| cam_B_soft | img_00_0 | cam_B | day | KEEP | KEEP |

Ảnh minh họa, feature và root cause nằm trong [required_failure_cases.md](required_failure_cases.md):

1. Night useful: img_18_1 còn thấy mục tiêu; ngưỡng brightness ngây thơ 60 sẽ loại, trong khi baseline và PoC hiện giữ. Đây là counterfactual control, không gọi nó là baseline đã nộp.
2. Small glare: img_18_2 còn nét nhưng chi tiết gần biển số bị lóa. PoC vẫn KEEP vì vùng bão hòa nhỏ không vượt tiêu chí tile 16×16. Không dùng GT ẩn để khẳng định severity chính thức.
3. Cam_B soft optics: img_00_0 mềm hơn ảnh đối chiếu nhưng vẫn giữ ở policy hiện tại; không bịa false alarm. Sweep Gaussian 0/0.5/1/1.5 trên ảnh dev img_00_1 cho thấy khi radius=1.5 cả hai cách đề nghị RECAPTURE. Đây là độ nhạy với quang học; cần đánh giá theo nhiệm vụ trước khi loại.

OOD được đo sau đóng băng, không tune lại: **9/10** hành động khớp engineering reference; false KEEP=1, false RECAPTURE=0. JPEG3 ood07 bị giữ, là failure thật của stress này. Không báo Recall@20 trên N=10 vì chọn tất cả sẽ vô nghĩa. Ảnh và kết quả từng dòng: [ood_contact_sheet.html](ood_contact_sheet.html), `ood_results.csv`. Kỳ vọng thiết kế không thay nhãn sử dụng thực tế của người kiểm.

## 07 · Human review, override và audit

Đã ghi 20 quyết định theo xác nhận của chủ sở hữu; kết quả cổng HOLD, reason=REVIEW_ESCALATED.

Đối chiếu 20 ảnh ở `visual_review.md`: 10 đề nghị RECAPTURE, 2 KEEP, 8 ESCALATE cần policy mức độ hữu ích/chi tiết mục tiêu. Không dùng reviewer giả của unit test làm bằng chứng review thật. Owner xác nhận được ghi ở `owner_review.json` khi có, cùng CSV đã review; nội dung này không được tự sinh khi chạy lại benchmark.

Reviewer ghi approve/edit/reject/escalate/skip và lý do; edit/reject phải có KEEP/RECAPTURE. CSV phải thuộc queue hiện tại, ID không trùng, score/action/evidence trùng snapshot. Raw và final riêng; audit JSONL append-only, decision log có owner/reason. `pred_action` là gợi ý mô hình (hoặc override đã chấp thuận); `review_status` và `final_action` phân biệt quyết định cuối. Ảnh ESCALATE và ảnh ngoài queue chưa review giữ final_action=HOLD, không được hiểu KEEP dự đoán là cho phép release. HOLD là kết quả hợp lệ khi còn ca chưa rõ, không phải lý do để sửa score cho đẹp.

## 08 · Tái lập và kiểm thử

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
sh tools/reproduce_t02.sh
```

`make baseline TRACK=t02`, `make run TRACK=t02` chạy fixture. Lệnh chấm chính thức khi có overlay: `.venv/bin/python -m src.evaluate --track t02 --pred out/poc/ranked_review.csv`. Thiếu GT trả exit 2 có giải thích. Pipeline không dùng `--allow-gt-read`.

Tests: **56 passed, 39 skipped in 3.77s**. 39 skipped cần GT giảng viên; không tính thành hidden-test PASS. Tests bao gồm offline/GT guard, success/error, deterministic output, override/audit, review không tên, CSV stale, escalate và GO→rerun lỗi→HOLD. Môi trường sạch tách biệt: `PASS`; xem `clean_environment_check.json`, `clean_test_results.txt` và `clean_run_log.txt`.

Cùng Pillow version nhưng Conda libjpeg9 khác wheel libjpeg6.2 đã gây lệch thứ hạng (không đổi action); `environment_drift.json` lưu bằng chứng. Môi trường chuẩn hiện dùng wheel PyPI, không system-site-packages; đối chiếu với venv sạch độc lập. Không tuyên bố mọi OS/binary JPEG cho output bit-identical.

Máy và runtime fixture: {'python': '3.13.9', 'platform': 'macOS-27.0.1-arm64-arm-64bit-Mach-O', 'processor': 'arm'}; 0.1683 giây cho 96 ảnh ở lần đo này. Runtime benchmark trong bảng thuộc bộ khác, không trộn hai phép đo.

## 09 · Giới hạn, rủi ro và cải tiến

Small glare, JPEG và cảnh ít texture còn yếu. OOD chỉ là synthetic shift, N=10 nhỏ; không đủ để nhận định deployment. Chưa có human usability gold đại diện, official hidden score hoặc dữ liệu camera mới ngoài đời. Bước cải tiến tiếp theo là thiết kế dev gold theo mục tiêu gán nhãn, kiểm ROI nhỏ và camera-specific calibration trong protocol mới; không sửa testset đã báo cáo.

Không đưa người/biển số thật lên public/cloud. Không tuyên bố đạt GDPR/luật Việt Nam; cần data owner/legal xác nhận khi đổi sang dữ liệu thật. Khi scale 10× cần đo throughput, giới hạn kích thước ảnh và budget reviewer; runtime nhỏ trên fixture không thay bằng chứng vận hành.

## 10 · Đóng góp và demo

Làm cá nhân: Nguyễn Công Quý chịu trách nhiệm kết quả, quyết định review và nộp bài. Git identity và commit thực chất ở `team_contributions.csv`; `git shortlog -sne --all` còn chứa tác giả starter, không nhận phần starter là tự viết. Bộ demo 5 slide tại `demo/output/Day06_T02_NguyenCongQuy.pptx`. Chưa có bằng chứng showcase/debate tại lớp, không nhận điểm/bonus thay cho việc đó. Không giả mốc demo-180m.

## 11 · References

Ngày đọc 2026-11-14.

- [Đề T02](../docs/tracks/T02.md): contract, baseline, ROI/OOD và failure modes phải đáp ứng.
- [OpenCV Laplacian](https://docs.opencv.org/4.x/d5/db5/tutorial_laplace_operator.html): cơ sở đạo hàm bậc hai và độ nhạy cạnh/nhiễu; variance threshold là heuristic của bài làm, không phải chứng nhận chất lượng.
- [SciPy bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html): nguyên lý resampling và confidence interval; bài dùng percentile bootstrap theo scene, ghi rõ CI suy biến.
- [Evaluator chuẩn](../src/metrics/tracks.py) và [review helpers](../src/common/review.py): tái sử dụng định nghĩa metric và audit để tránh đổi cách chấm.

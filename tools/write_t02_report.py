"""Build report and evidence from actual runs; no invented review/GT/showcase."""
from pathlib import Path
import hashlib,json,shutil,subprocess
import pandas as pd
from src.common.io import git_sha

R=Path('reports')
def read(p): return json.loads(Path(p).read_text())
def md_table(df):
    df=df.fillna('');cols=list(df.columns)
    lines=['| '+' | '.join(cols)+' |','|'+'|'.join('---' for _ in cols)+'|']
    for row in df.itertuples(index=False,name=None): lines.append('| '+' | '.join(str(v).replace('|','/') for v in row)+' |')
    return '\n'.join(lines)

def main():
    R.mkdir(exist_ok=True);info=read('out/poc/run_info.json');clean=read(R/'clean_environment_check.json');ood=read(R/'ood_summary.json')
    protocol=read(R/'internal_protocol.json');sha=git_sha();tests=(R/'test_results.txt').read_text().strip().splitlines()[-1]
    review_count=info['stats'].get('n_reviewed',0);decision=read('out/poc/decision.json')
    own=read(R/'owner_review.json') if (R/'owner_review.json').exists() else {'confirmed':False}
    for f in ['review_queue.csv','decision_log.csv','decision.json','audit_log.jsonl','run_info.json','raw_predictions.csv','ranked_review.csv','contact_sheet.html']:
        shutil.copyfile(Path('out/poc')/f,R/f)
    if Path('out/poc/review_queue_reviewed.csv').exists():shutil.copyfile('out/poc/review_queue_reviewed.csv',R/'review_queue_reviewed.csv')
    data=read('reports/source_snapshot.json') if (R/'source_snapshot.json').exists() else {}
    pd.DataFrame([dict(member='NguyenCongQuy',git_author_name='NguyenCongQuy',git_email='26ai.quync@vinuni.edu.vn',role='Solo: integration, algorithm, QA, review decisions, report',modules_files='src/pipeline.py;tests/test_t02_submission.py;tools/;reports/',commit_shas=sha,evidence_note='See substantive commits and measured evidence; classroom presentation not claimed',presenter='not recorded')]).to_csv(R/'team_contributions.csv',index=False)
    review_state=(f"Đã ghi {review_count} quyết định theo xác nhận của chủ sở hữu; kết quả cổng {decision['status']}, reason={decision['reason_code']}." if own.get('confirmed') else 'Có 20 khuyến nghị kỹ thuật; chưa có xác nhận human review của chủ sở hữu. Cổng HOLD, không giả chữ ký reviewer.')
    failure=pd.read_csv(R/'required_failure_cases.csv')[['case','image_id','camera_id','light','baseline_action','poc_action']]
    report=f'''# Day06 · T02 — Raw QC Triage

## 00 · Thông tin và phạm vi

Nguyễn Công Quý · MSSV 2A202603149 · làm cá nhân, mã nội bộ SOLO-2A202603149. Repo: https://github.com/nguyencongquy/K5-Day6-L2A-NguyenCongQuy-2A202603149-DataGovernanceAndPrivacy. Chọn một challenge T02 theo README; không làm cả 14, không có yêu cầu bốc thăm trong repo. Cần tuân theo hướng dẫn lớp nếu giảng viên phân đề riêng hoặc yêu cầu nhóm.

Source commit cho lần đo: `{info['git_sha']}`; snapshot code/config có SHA256 trong `source_snapshot.json`. Không backdate commit/tag để nhận bonus thời gian. Bộ demo 5 slide đính kèm; không tuyên bố đã trình bày hoặc tham gia debate khi chưa có bằng chứng.

## 01 · Bài toán và điều kiện quyết định

Người kiểm chỉ có ngân sách B=20 ảnh. Input là ảnh, camera/light/split và manifest; output gồm score xếp hạng, gợi ý KEEP/RECAPTURE, queue, HTML review, override/diff, audit và decision. Năm bước: load+provenance → process → rank → review → decide. Không xóa hoặc sửa ảnh nguồn.

GO chỉ xác nhận kết quả triage đã được review đầy đủ, không chứng nhận mọi ảnh đạt chất lượng hay tuân thủ pháp luật. Thiếu review, skip hoặc escalate giữ HOLD. Input/manifest sai trả lỗi; rerun khởi đầu bằng HOLD để không để sót GO của lần trước. Owner và reason_code bắt buộc.

## 02 · Dữ liệu, split và provenance

- Fixture T02: {info['stats']['n_items']} ảnh synthetic CC0, 24 cảnh gốc; 56 dev, 40 eval. Giữ split theo cảnh do đề cung cấp. `manifest_check.txt` kiểm 14 manifest gốc, không có lỗi. Pipeline không đọc GT ẩn, không dùng ID/file suffix để chấm điểm.
- Benchmark nội bộ: 12 cảnh tự sinh × 5 biến thể = 60 mẫu; 48 mẫu có phép biến đổi. Nhãn là **phép biến đổi được áp dụng**, không phải human usability gold. Giữ nguyên bộ, B=20, seed và evaluator; không đổi testset để tăng số.
- OOD: 10 ảnh synthetic inspection-board với hình học, camera ID, texture và kích thước khác road fixture. Ảnh, reference expectations và manifest đã commit trước khi đo (`9f15f04`). Không gọi đây là ảnh BDD thật hoặc bằng chứng generalization ngoài đời. `data/real` là tùy chọn và không sử dụng.

`src.main` bật offline/GT guard. Không pretrained model, không API ngoài, không PII thật. Khi cần nhãn chính thức, giảng viên chạy hidden evaluation; học viên không phải lấy hoặc tạo giả gt/.

## 03 · Thiết kế và policy đóng băng

Baseline: score=max(0,1−Laplacian variance/80), một ngưỡng toàn ảnh, dùng hàm chung của lab. Tham số 80 là mốc score về 0; cutoff hành động score≥0.5 tương đương Laplacian≤40. PoC lấy max của bốn tín hiệu trong [0,1]: sharpness chuẩn hóa tương phản (Laplacian/max(gray variance,100), ngưỡng 0.04); brightness thiếu sáng dưới 18; saturated fraction >0.65 trên tile ROI 16×16; chênh độ nhảy tại biên khối JPEG 8 pixel chuẩn hóa bằng 12. Score≥0.5 gợi ý RECAPTURE.

Ngưỡng là heuristic cố định; không tuyên bố được tối ưu trên dev labels. Không tune bằng nhãn eval. Sau review eval ở phiên trước, giữ nguyên feature/threshold; chỉ bổ sung kiểm chứng và sửa an toàn review. `scoring_freeze_check.json` so hàm scoring với commit đóng băng. Cam_B sensitivity chỉ dùng dev và không cập nhật policy sau sweep. ROI glare đáp ứng nhánh ROI ở yêu cầu +24h; phân tích dưới đây cho thấy hạn chế của ROI này.

## 04 · Baseline vs PoC

**Bảng chỉ áp dụng bộ controlled-transform nội bộ, không phải điểm trên 96 fixture hoặc hidden GT.** Pool, B=20, seed=42 và cách tính giống nhau. JSON/table do script + evaluator chuẩn sinh, không gõ tay.

{(R/'table1_baseline_vs_poc.md').read_text()}

Primary bằng nhau và đều chạm trần B/#positive=20/48. Vì vậy chưa chứng minh PoC cải thiện truy hồi lỗi. Secondary loại lỗi tăng trên bộ biến đổi đơn giản; không suy ra tốt hơn trên ảnh thật. Báo cả số không tăng, không dùng tỷ lệ cải thiện khi baseline=0.

Ablation bỏ glare, giữ các thành phần khác:

{(R/'table2_ablation.md').read_text()}

Đây là ablation nội bộ; không tự nhận hidden-test/debate bonus. Các JSON cũ của môi trường Conda giữ trong `history/conda_v1` để đối chiếu.

## 05 · Protocol, metric và slices

Recall@20 = lỗi thật trong top-20 / tổng lỗi thật của pool eval; Precision@20 = lỗi thật trong top-20 /20. Ghép bằng image_id, cùng pool/split/seed. Xuất đủ 96 score, queue chỉ lấy từ 40 eval để đúng budget chấm. Không dùng override hành động để thay score, không dùng review queue tự chọn làm bộ GT đại diện cho toàn dataset.

Benchmark sinh seed=20261114; run/cluster bootstrap seed=42. Bootstrap 500 lượt theo scene, giữ các biến thể cùng cụm; CI nội bộ {protocol['bootstrap_scene_recall_ci95']}. CI suy biến do trần budget và cấu trúc artificial set; không diễn giải thành chắc chắn ngoài đời.

Slices theo defect ở `slices_poc.csv`; camera/light/split mô tả fixture ở `fixture_descriptive_slices.csv`. Khi chưa có nhãn fixture, số RECAPTURE theo camera chỉ là phân bố dự đoán, không phải false-positive rate. Bộ nội bộ không có đủ light slices thật; limitations được giữ rõ.

## 06 · Ba failure mode bắt buộc và 10 ảnh OOD

{md_table(failure)}

Ảnh minh họa, feature và root cause nằm trong [required_failure_cases.md](required_failure_cases.md):

1. Night useful: img_18_1 còn thấy mục tiêu; ngưỡng brightness ngây thơ 60 sẽ loại, trong khi baseline và PoC hiện giữ. Đây là counterfactual control, không gọi nó là baseline đã nộp.
2. Small glare: img_18_2 còn nét nhưng chi tiết gần biển số bị lóa. PoC vẫn KEEP vì vùng bão hòa nhỏ không vượt tiêu chí tile 16×16. Không dùng GT ẩn để khẳng định severity chính thức.
3. Cam_B soft optics: img_00_0 mềm hơn ảnh đối chiếu nhưng vẫn giữ ở policy hiện tại; không bịa false alarm. Sweep Gaussian 0/0.5/1/1.5 trên ảnh dev img_00_1 cho thấy khi radius=1.5 cả hai cách đề nghị RECAPTURE. Đây là độ nhạy với quang học; cần đánh giá theo nhiệm vụ trước khi loại.

OOD được đo sau đóng băng, không tune lại: **{ood['agreement_count']}/{ood['n']}** hành động khớp engineering reference; false KEEP={ood['false_keep_vs_reference']}, false RECAPTURE={ood['false_recapture_vs_reference']}. JPEG3 ood07 bị giữ, là failure thật của stress này. Không báo Recall@20 trên N=10 vì chọn tất cả sẽ vô nghĩa. Ảnh và kết quả từng dòng: [ood_contact_sheet.html](ood_contact_sheet.html), `ood_results.csv`. Kỳ vọng thiết kế không thay nhãn sử dụng thực tế của người kiểm.

## 07 · Human review, override và audit

{review_state}

Đối chiếu 20 ảnh ở `visual_review.md`: 10 đề nghị RECAPTURE, 2 KEEP, 8 ESCALATE cần policy mức độ hữu ích/chi tiết mục tiêu. Không dùng reviewer giả của unit test làm bằng chứng review thật. Owner xác nhận được ghi ở `owner_review.json` khi có, cùng CSV đã review; nội dung này không được tự sinh khi chạy lại benchmark.

Reviewer ghi approve/edit/reject/escalate/skip và lý do; edit/reject phải có KEEP/RECAPTURE. CSV phải thuộc queue hiện tại, ID không trùng, score/action/evidence trùng snapshot. Raw và final riêng; audit JSONL append-only, decision log có owner/reason. `pred_action` là gợi ý mô hình (hoặc override đã chấp thuận); `review_status` và `final_action` phân biệt quyết định cuối. Ảnh ESCALATE và ảnh ngoài queue chưa review giữ final_action=HOLD, không được hiểu KEEP dự đoán là cho phép release. HOLD là kết quả hợp lệ khi còn ca chưa rõ, không phải lý do để sửa score cho đẹp.

## 08 · Tái lập và kiểm thử

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
sh tools/reproduce_t02.sh
```

`make baseline TRACK=t02`, `make run TRACK=t02` chạy fixture. Lệnh chấm chính thức khi có overlay: `.venv/bin/python -m src.evaluate --track t02 --pred out/poc/ranked_review.csv`. Thiếu GT trả exit 2 có giải thích. Pipeline không dùng `--allow-gt-read`.

Tests: **{tests}**. 39 skipped cần GT giảng viên; không tính thành hidden-test PASS. Tests bao gồm offline/GT guard, success/error, deterministic output, override/audit, review không tên, CSV stale, escalate và GO→rerun lỗi→HOLD. Môi trường sạch tách biệt: `{clean.get('isolated_dependency_install')}`; xem `clean_environment_check.json`, `clean_test_results.txt` và `clean_run_log.txt`.

Cùng Pillow version nhưng Conda libjpeg9 khác wheel libjpeg6.2 đã gây lệch thứ hạng (không đổi action); `environment_drift.json` lưu bằng chứng. Môi trường chuẩn hiện dùng wheel PyPI, không system-site-packages; đối chiếu với venv sạch độc lập. Không tuyên bố mọi OS/binary JPEG cho output bit-identical.

Máy và runtime fixture: {info['machine']}; {info['runtime_seconds']} giây cho {info['stats']['n_items']} ảnh ở lần đo này. Runtime benchmark trong bảng thuộc bộ khác, không trộn hai phép đo.

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
'''
    (R/'group_report.md').write_text(report)
    for csv_path in R.glob('*.csv'):
        csv_path.write_text(csv_path.read_text())
    print('Report refreshed from actual evidence; owner confirmed:',own.get('confirmed',False))

if __name__=='__main__':main()

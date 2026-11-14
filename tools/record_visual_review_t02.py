"""Persist image-specific technical review recommendations; NOT owner sign-off or hidden GT."""
from pathlib import Path
import pandas as pd

# Observations made by inspecting the 20 queued images at source size,
# with enlarged views for ambiguous compression cases. Do not derive GT labels.
FINDINGS = {
'img_17_2':('RECAPTURE','Vùng lóa trắng lớn che một phần cảnh và mục tiêu; đề nghị chụp lại.'),
'img_15_2':('RECAPTURE','Mờ rõ toàn ảnh, cạnh người và xe mất chi tiết.'),
'img_13_3':('RECAPTURE','Ảnh đêm mờ rõ, hình người và xe nhòe; không chỉ tối đơn thuần.'),
'img_16_2':('RECAPTURE','Mờ toàn cảnh; cạnh xe và người không rõ.'),
'img_19_3':('RECAPTURE','Mờ toàn cảnh; suy giảm chi tiết xe và người.'),
'img_15_3':('RECAPTURE','Thiếu sáng nặng; phần lớn mục tiêu khó phân biệt.'),
'img_01_2':('RECAPTURE','Thiếu sáng nặng trên cảnh đêm; cần kiểm lại mức sử dụng mục tiêu.'),
'img_23_3':('RECAPTURE','Cảnh ngày bị tối nặng; nhiều vùng mục tiêu gần đen.'),
'img_17_3':('RECAPTURE','Cảnh ngày bị tối nặng; tín hiệu mục tiêu hạn chế.'),
'img_05_3':('RECAPTURE','Lóa cục bộ gần xe; cần kiểm mục tiêu trong vùng cháy sáng.'),
'img_05_2':('ESCALATE','KEEP cần xem lại: block và ringing quanh xe, mặt đường, nhà; không kết luận severity từ ảnh thu nhỏ.'),
'img_13_2':('ESCALATE','KEEP cần xem lại: ringing/block rõ quanh xe trên ảnh đêm; hình xe vẫn nhận ra.'),
'img_23_2':('ESCALATE','KEEP cần xem lại: cạnh nhà và mục tiêu có artifact dạng block/ringing.'),
'img_01_3':('ESCALATE','KEEP cần xem lại: artifact nén quanh xe và đèn; ảnh tối không tự động là lỗi.'),
'img_06_2':('ESCALATE','KEEP cần xem lại: artifact nén quanh mục tiêu trên nền đêm.'),
'img_03_3':('ESCALATE','KEEP cần xem lại: viền mục tiêu có artifact; cần policy mức độ suy giảm chấp nhận được.'),
'img_19_2':('ESCALATE','Chi tiết hơi mềm; vẫn thấy hình dạng mục tiêu. Không đủ căn cứ chốt RECAPTURE chỉ từ độ nét.'),
'img_05_0':('KEEP','Cạnh mục tiêu nhìn rõ trong đối chiếu; không thấy suy giảm lớn ở kích thước gốc.'),
'img_15_0':('KEEP','Cảnh dusk nhưng người và xe còn thấy rõ; không nên loại chỉ theo ánh sáng.'),
'img_16_3':('ESCALATE','KEEP cần xem lại: artifact nén ở nhà, xe và rìa vật thể; ảnh phóng to xác nhận cấu trúc block/ringing.'),
}


def main():
    q=pd.read_csv('reports/review_queue.csv').fillna('')
    rows=[]
    for r in q.itertuples(index=False):
        action,note=FINDINGS[r.item_id]
        rows.append(dict(item_id=r.item_id,pipeline_action=r.suggested_action,
            proposed_action=action,observation=note,evidence_path=r.evidence_path,
            status='OWNER_CONFIRMATION_PENDING'))
    pd.DataFrame(rows).to_csv('reports/visual_review_recommendations.csv',index=False)
    lines=['# T02 — đối chiếu trực quan 20 ảnh',
        '', 'Khuyến nghị kỹ thuật sau đối chiếu ảnh. Không phải GT giảng viên, không thay chữ ký reviewer của học viên. Không đổi scoring policy sau khi xem eval.',
        '', '| Image | Pipeline | Đề nghị | Quan sát |','|---|---|---|---|']
    lines += [f"| {r['item_id']} | {r['pipeline_action']} | {r['proposed_action']} | {r['observation']} |" for r in rows]
    Path('reports/visual_review.md').write_text('\n'.join(lines)+'\n')
    print(pd.DataFrame(rows).proposed_action.value_counts().to_dict())

if __name__=='__main__': main()

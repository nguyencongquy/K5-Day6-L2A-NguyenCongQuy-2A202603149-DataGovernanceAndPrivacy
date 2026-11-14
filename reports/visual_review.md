# T02 — đối chiếu trực quan 20 ảnh

Chủ sở hữu đã xác nhận 10 RECAPTURE, 2 KEEP, 8 ESCALATE; xem owner_review.json và CSV đã review. Tám ca ESCALATE tiếp tục HOLD. Không phải GT giảng viên; scoring policy không đổi sau khi xem eval.

| Image | Pipeline | Đề nghị | Quan sát |
|---|---|---|---|
| img_17_2 | RECAPTURE | RECAPTURE | Vùng lóa trắng lớn che một phần cảnh và mục tiêu; đề nghị chụp lại. |
| img_15_2 | RECAPTURE | RECAPTURE | Mờ rõ toàn ảnh, cạnh người và xe mất chi tiết. |
| img_13_3 | RECAPTURE | RECAPTURE | Ảnh đêm mờ rõ, hình người và xe nhòe; không chỉ tối đơn thuần. |
| img_16_2 | RECAPTURE | RECAPTURE | Mờ toàn cảnh; cạnh xe và người không rõ. |
| img_19_3 | RECAPTURE | RECAPTURE | Mờ toàn cảnh; suy giảm chi tiết xe và người. |
| img_15_3 | RECAPTURE | RECAPTURE | Thiếu sáng nặng; phần lớn mục tiêu khó phân biệt. |
| img_01_2 | RECAPTURE | RECAPTURE | Thiếu sáng nặng trên cảnh đêm; cần kiểm lại mức sử dụng mục tiêu. |
| img_23_3 | RECAPTURE | RECAPTURE | Cảnh ngày bị tối nặng; nhiều vùng mục tiêu gần đen. |
| img_17_3 | RECAPTURE | RECAPTURE | Cảnh ngày bị tối nặng; tín hiệu mục tiêu hạn chế. |
| img_05_3 | RECAPTURE | RECAPTURE | Lóa cục bộ gần xe; cần kiểm mục tiêu trong vùng cháy sáng. |
| img_05_2 | KEEP | ESCALATE | KEEP cần xem lại: block và ringing quanh xe, mặt đường, nhà; không kết luận severity từ ảnh thu nhỏ. |
| img_13_2 | KEEP | ESCALATE | KEEP cần xem lại: ringing/block rõ quanh xe trên ảnh đêm; hình xe vẫn nhận ra. |
| img_23_2 | KEEP | ESCALATE | KEEP cần xem lại: cạnh nhà và mục tiêu có artifact dạng block/ringing. |
| img_01_3 | KEEP | ESCALATE | KEEP cần xem lại: artifact nén quanh xe và đèn; ảnh tối không tự động là lỗi. |
| img_06_2 | KEEP | ESCALATE | KEEP cần xem lại: artifact nén quanh mục tiêu trên nền đêm. |
| img_03_3 | KEEP | ESCALATE | KEEP cần xem lại: viền mục tiêu có artifact; cần policy mức độ suy giảm chấp nhận được. |
| img_19_2 | KEEP | ESCALATE | Chi tiết hơi mềm; vẫn thấy hình dạng mục tiêu. Không đủ căn cứ chốt RECAPTURE chỉ từ độ nét. |
| img_05_0 | KEEP | KEEP | Cạnh mục tiêu nhìn rõ trong đối chiếu; không thấy suy giảm lớn ở kích thước gốc. |
| img_15_0 | KEEP | KEEP | Cảnh dusk nhưng người và xe còn thấy rõ; không nên loại chỉ theo ánh sáng. |
| img_16_3 | KEEP | ESCALATE | KEEP cần xem lại: artifact nén ở nhà, xe và rìa vật thể; ảnh phóng to xác nhận cấu trúc block/ringing. |

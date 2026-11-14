# Demo T02 — 5 slides
1. Vấn đề: 96 ảnh, ngân sách review 20; ảnh đêm và glare là trade-off.
2. Data flow: provenance → feature → ranking → review → audit → gate.
3. Chạy make baseline TRACK=t02 và make run TRACK=t02; mở reports/contact_sheet.html.
4. So sánh nội bộ và ablation: recall hòa; phân loại lỗi cải thiện, compression/dark còn yếu.
5. HOLD: review chủ sở hữu và hidden GT còn thiếu; giới hạn, bước tiếp theo.

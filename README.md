# SEN Image Commands

© Sentechtipsvn — menu tiếng Việt chọn nhiều mã và sao chép Clipboard.

## Bản đang kiểm thử: v1.1 (sửa lỗi nối biến)

**[Tải trực tiếp SEN Image Commands v1.1.shortcut](https://github.com/dammeiosvn/SENImageCommands/raw/refs/heads/main/dist/SEN%20Image%20Commands%20v1.1.shortcut)**

- Gói đã ký qua RoutineHub HubSign, dạng AEA1.
- SHA-256: `bacb3ea23657ef23f56edb0cd6ca8d6351cf15b5a0cd778be54df99b2bc96042`
- Đã qua bộ kiểm tra tĩnh bắt buộc: không thiếu các WFInput quan trọng, các If có cấu hình, các nhóm điều khiển cân bằng, không có action ID ngoài whitelist.
- **Chưa được kiểm thử chạy trên iPhone thật.** Đây là bản để nghiệm thu.

### Lỗi v1.0 đã xử lý

1. Bổ sung tham chiếu UUID tường minh cho Set Variable, Choose from List, Get Dictionary Value và các input khác.
2. Bọc biến điều kiện theo định dạng `{Type:"Variable", Variable: ...}` bắt buộc.
3. Dùng đúng mã điều kiện `99` (contains) để bỏ mã trùng.
4. Bỏ tác vụ `trimwhitespace` không nhận diện; dùng Replace Text có đầu vào.
5. Đổi trạng thái rỗng thành sentinel không trắng `__SEN__` để iOS không để trống điều kiện.
6. Thêm `scripts/validate_shortcut.py` chạy trước bước ký.

### Quy trình thử trên iPhone

1. Nhập **v1.1**, kiểm tra trong trình sửa không còn tác vụ không xác định và không có điều kiện đỏ.
2. Chạy; chọn `Chế độ & ảnh tham chiếu`, chọn nhóm, tích `Chỉnh sửa ảnh đã cung cấp`.
3. Quay Menu chính; mở `Khóa nhận diện`, chọn `Khóa nhận diện nhân vật chính` hoặc `/senlock` nếu có.
4. Xem mã đã chọn, sau đó **Hoàn tất & Sao chép**; kết quả chỉ có các mã, mỗi dòng một mã.
5. Chạy lại, chọn trùng một mã trong phiên rồi kiểm tra đầu ra không nhân đôi.

Nếu có lỗi, chụp vùng tác vụ đỏ hoặc ghi lại bước gặp lỗi. Không cần chỉnh sửa thủ công cấu trúc.

### Dữ liệu và mã nguồn

- `data/commands.v1.json`: 357 mã trong 12 danh mục và 19 nhóm.
- `docs/SEN_IMAGE_COMMANDS_v1.txt`: bộ quy ước gốc.
- `scripts/build_sen_shortcut.py`: sinh plist.
- `scripts/validate_shortcut.py`: kiểm tra tĩnh chặt hơn.
- `.github/workflows/hubsign-linux.yml`: sinh, kiểm tra, ký và phát hành.
- `dist/SEN Image Commands v1.1.shortcut`: bản signed trực tiếp.

Bản v1.0 cũ (`dist/SEN Image Commands.shortcut`) có lỗi, không nên cài.

### Giới hạn v1.1

Có menu vCard chính, chọn nhóm, chọn nhiều mã, loại trùng, xem lệnh, xóa toàn bộ và Clipboard. Chưa hoàn thiện mẫu lệnh nhanh, cảnh báo xung đột nâng cao, xóa từng mã, hoặc phiên lưu iCloud.

Mã riêng như `/senlock` cần AI có bảng quy ước để hiểu ý nghĩa.

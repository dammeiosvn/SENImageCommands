# SEN Image Commands

**© Sentechtipsvn** — Bộ tạo lệnh AI từ Menu tiếng Việt trên Apple Shortcuts.

## Bản phát triển đầu tiên

- 12 danh mục, 19 nhóm, 357 mã từ bộ quy ước người dùng.
- Menu chính dạng vCard (Contacts in-memory), Menu con tiếng Việt, chọn nhiều khóa.
- Giữ tất cả lựa chọn trong RAM suốt phiên; tra cứu dữ liệu trong Dictionary; không gọi API hoặc iCloud mỗi lần quay lại Menu.
- Clipboard chỉ xuất các mã quy ước, mỗi mã một dòng. Mã trùng được bỏ qua.
- Menu có **Xem mã / Hoàn tất & sao chép / Xóa lựa chọn**.
- 150 lượt duyệt Menu cho một phiên; đóng/tắt Shortcut kết thúc phiên.

## Cấu trúc repository

| File | Vai trò |
| --- | --- |
| `docs/SEN_IMAGE_COMMANDS_v1.txt` | Tài liệu quy ước gốc |
| `data/commands.v1.json` | Từ điển chuẩn 357 mã |
| `scripts/build_sen_shortcut.py` | Sinh plist XML từ JSON |
| `.github/workflows/build-and-sign.yml` | Build, ký và xuất tệp trên macOS |
| `dist/*.signed.shortcut.b64` | Tệp đã ký được mã hóa base64 (nếu workflow ký thành công) |
| `dist/*.manifest.json` | Kích thước, checksum, phương thức ký |

## Chạy lại quy trình build

Từ máy có Python 3:

```bash
python3 scripts/build_sen_shortcut.py data/commands.v1.json 'build/SEN Image Commands.unsigned.shortcut'
```

Tệp build local là **unsigned**, không được coi là bản cài đặt. GitHub Actions sẽ chạy ký, kiểm tra magic bytes `AEA1` trước khi xuất bản bản signed. Trường hợp không thể ký bằng công cụ Apple trên macOS CI, workflow có thể gửi **chỉ nội dung phím tắt công khai** đến RoutineHub HubSign để ký; không chứa thông tin cá nhân hoặc mã thông báo.

## Lưu ý kiểm thử

- Kiểm thử tĩnh Python/plistlib chỉ xác minh cấu trúc; không chứng minh tương thích iOS thực tế.
- Bộ quy ước là cú pháp tự định nghĩa, AI cần được cung cấp từ điển quy ước để hiểu đầy đủ.
- Phiên bản đầu tập trung vào vòng chọn nhiều mã, loại trùng và Clipboard. Chức năng mẫu lệnh, lưu phiên iCloud và bộ cảnh báo xung đột đầy đủ sẽ cần kiểm thử trong bản nâng cấp sau.
- Hủy thao tác tại hộp chọn của iOS có thể hủy cả Shortcut; không xử lý vòng quay bằng chờ đợi hay gọi lại Shortcut.

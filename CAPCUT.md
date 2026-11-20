# Khung Mẫu trong CapCut

Bản ghi lấy từ CapCut PC 9.8.0. Ba bản sao timeline và `draft_content.json` ở thư mục dự án có cùng nội dung tại thời điểm kiểm tra. JSON giữ nguyên các trường kỹ thuật và ID liên kết, với đường dẫn chuyển thành `local-media://` hoặc `capcut-cache://`. Các định danh máy, mã truy vấn nội bộ và liên kết ảnh ký hạn được bỏ trống.

## Khung và lớp

Khung dọc **1080 × 1920**, tỷ lệ **9:16**, **30 FPS**. Cả năm segment dài `17_933_333 µs` (khoảng 17,933 giây), bắt đầu ở `0 µs`. Các mốc `*_timerange` tính bằng microgiây.

| `track_render_index` | `render_index` | Lớp | Thiết lập chính |
| ---: | ---: | --- | --- |
| 0 | 0 | Video chính | Scale 1 × 1, x = y = 0, alpha 1, tốc độ 1, volume 1. Có audio nhúng trong nguồn. |
| 1 | 3 | Ảnh đen và mặt nạ A | Scale 1 × 1, x = y = 0, alpha 1. Mặt nạ xoay 180°. |
| 2 | 2 | Ảnh đen và mặt nạ B | Scale 1 × 1, x = y = 0, alpha 1. Mặt nạ xoay 0°. |
| 3 | 14000 | Sticker sóng âm trắng | Scale 1,25 × 1,25, x = 0, y = −0,2864583333333333, alpha 1. |
| 4 | 11000 | Nhấp nháy cổ điển | `apply_target_type: 2`, `bind_segment_id` rỗng, giá trị effect 1. |

Giữ riêng hai chỉ số render vì thứ tự track trong JSON khác `render_index` của một số lớp. Timeline lưu video nền có tiếng, hai ảnh, sticker và hiệu ứng. Số track text và track audio riêng đều bằng 0.

## Hai lớp đen

Hai track dùng chung một ảnh JPEG. Toàn bộ pixel giải mã có RGB `(0, 0, 0)`. Dùng ảnh [nen-den.jpg](nen-den.jpg) và nhân đôi layer với hai mặt nạ **Tách**, loại `line`, `resource_id` `7374020197990011409`.

| Trường native | Mặt nạ A · `track_render_index = 1` | Mặt nạ B · `track_render_index = 2` |
| --- | ---: | ---: |
| `width` | 0.28 | 0.28 |
| `height` | 0 | 0 |
| `centerX` | 0 | 0 |
| `centerY` | −0.4553775743707094 | 0.782608695652174 |
| `rotation` | 180 | 0 |
| `feather` | 0.65 | 1.0 |
| `expansion` · `roundCorner` | 0 · 0 | 0 · 0 |
| `invert` · `aspectRatio` | false · 1 | false · 1 |

Mỗi ảnh có bản ghi HSL bật, với hue, saturation và lightness đều bằng 0 và `custom_color = "#FFE64444"`. Màu ảnh là đen. `is_color_clip` và `is_gradient` đều `false`. Độ chuyển mềm đến từ mặt nạ. Dùng nguyên các giá trị chuẩn hóa của mặt nạ khi dựng lại.

## Hiệu ứng và sticker

- **Nhấp nháy cổ điển** thuộc danh mục **Cổ điển** (`27302`). `effect_id` và `resource_id` cùng là `7618619632592620805`. `effects_adjust_background_animation = 0.2` (mặc định 0.5), `effects_adjust_speed = 0.0` (mặc định 0.33333333333333). `enable_mask = true` và danh sách `effect_mask` trống.
- **Interface EN Music Sound Waveform White** có `sticker_id` và `resource_id` cùng là `7460473405519744309`. Tọa độ transform đặt tâm sticker ở giữa ngang và thấp hơn tâm khung 275 px theo quy ước trục y của CapCut. Xoay 0°, không lật, `cycle_setting = true`, màu tô trắng `#FFFFFF`, alpha 1, không viền hay bóng.
- Phần cache của sticker trỏ tới một ảnh động GIF **280 × 280**, **250 khung ở 25 FPS**, dài **10 giây**. Chuyển động lên xuống nằm trong chính ảnh động. Draft có `common_keyframes` rỗng trên mọi segment và danh sách keyframe toàn dự án cũng trống. Ảnh động tự chạy theo thời gian của sticker, với cờ lặp đã bật.

Tìm thông số của từng segment trong `tracks[].segments[]`. Đối chiếu `material_id` và `extra_material_refs` với các `id` bên trong `materials`. Clip nền cần thay bằng footage của dự án mới. Kho công khai chứa JSON tham chiếu với đường dẫn thay thế và ảnh đen, cùng thông tin để chọn lại hiệu ứng và sticker trong CapCut.

# Khung Mẫu CapCut và phụ đề 10KVideo

Bộ tham chiếu để AI đọc lại thông số của dự án **Khung Mẫu** và học cách 10KVideo chia dòng, đồng bộ và nhấn từ cho phụ đề tiếng Việt.

| Tệp | Nội dung |
| --- | --- |
| [CAPCUT.md](CAPCUT.md) | Thời lượng, thứ tự lớp, hai mặt nạ đen, hiệu ứng và sticker sóng nhạc |
| [capcut-draft.json](capcut-draft.json) | Timeline gốc dạng JSON với thông số CapCut và liên kết giữa các vật liệu |
| [nen-den.jpg](nen-den.jpg) | Ảnh đen 1080 × 1920 dùng chung cho hai lớp |
| [10KVIDEO.md](10KVIDEO.md) | Quy trình nhận dạng giọng nói, gom dòng, karaoke và trộn nhạc |
| [10kvideo-style.json](10kvideo-style.json) | Cấu hình phụ đề hiệu lực trên máy và thiết lập nhạc nền trong bản 10KVideo được đọc |
| [vi-du-sub.json](vi-du-sub.json) | Từ có mốc thời gian, thứ tự đoạn và nhóm chữ trong ví dụ tổng hợp |
| [vi-du-sub.ass](vi-du-sub.ass) · [vi-du-sub.srt](vi-du-sub.srt) | Hai đầu ra từ cùng ví dụ, một bản karaoke và một bản chữ thuần |
| [10kvideo-music.json](10kvideo-music.json) | Danh mục chín tệp nhạc nền, thời lượng, codec và SHA-256 |

**Khi dùng với AI**, gửi `CAPCUT.md`, `capcut-draft.json`, `10KVIDEO.md` và `10kvideo-style.json` trước. Dùng các tệp ví dụ để kiểm tra việc đổi mốc thời gian sau khi cắt và đảo đoạn. Chọn lại các tài nguyên CapCut theo ID hoặc tên khi dựng trên máy khác. Gói công khai chứa thông số và danh mục âm thanh. Ảnh động và hiệu ứng có sẵn trong CapCut, còn các bài nhạc độc lập đi kèm gói cục bộ.

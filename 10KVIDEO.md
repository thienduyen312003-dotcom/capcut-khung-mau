# Cách 10KVideo làm phụ đề tiếng Việt

Tham chiếu từ bản cài **v1.260914.002**. Ví dụ dùng lời tự soạn và mốc thời gian tổng hợp, chạy qua trình dựng ASS/SRT của chính bản này. Hai luồng dưới đây có đầu ra khác nhau.

## Dựng video có chữ karaoke

1. Trích âm thanh thành **WAV PCM 16-bit, mono, 16 kHz**. Ưu tiên nạp `<video>.words.json` có mốc từng từ và dấu nhận diện video khớp. Nếu có `<video>.srt`, chia đều thời lượng mỗi cue để ước lượng mốc từ. Nếu hai nguồn vắng mặt, gọi **ElevenLabs Scribe `scribe_v1` với `vi`** và lấy token `word` cùng `start`/`end`. Bản này báo lỗi khi cần bóc mới mà Scribe thất bại.
2. Lọc đoạn nhận dạng ảo ở đuôi. Khâu soát chính tả tùy cấu hình có thể sửa chữ từ nguồn mới hoặc SRT và lưu lại cache word-level. Giữ chỉ số từ và mốc âm thanh đã nhận dạng khi chỉnh nội dung chữ. Xác định các khoảng cắt bằng mốc từ và khoảng lặng audio. Cấu hình trên máy dùng ngưỡng lặng 0,6 giây, giữ hơi thở 0,25 giây và đệm biên 80 ms.
3. Đổi mốc sang timeline xuất theo đúng thứ tự phát. Với từ có tâm nằm trong đoạn giữ, lấy `out_start + (word_mid - src_start)` làm tâm mới rồi cộng trừ nửa thời lượng từ. Xếp theo mốc mới. Giữ chỉ số từ gốc để màn sửa phụ đề biết đang sửa chữ nào. Đoạn phát lại có thể sinh nhiều cue dùng cùng một chỉ số từ gốc.
4. Gom chữ theo ý. Ưu tiên đổi đoạn, khoảng lặng trên 0,6 giây, cuối câu hoặc dấu phẩy, và dấu hiệu mở câu mới như chữ hoa. Sau ít nhất ba từ, có thể ngắt trước từ mở mệnh đề như *hãy, nếu, khi, mà, nhưng, vì*. Giới hạn mềm là **5 từ**, có thể giữ token mang chữ số đi cùng cụm trước trong giới hạn cộng thêm 2. Số thứ tự kiểu `1.` mở dòng và được miễn khi đếm giới hạn mềm. Từ lẻ được gộp ngược nếu sát trong 0,6 giây, cùng đoạn, còn chỗ và không vượt ranh giới câu.
5. Một cue SRT cho mỗi nhóm chữ. Kết cue ở cuối từ cuối hoặc sớm hơn điểm vào nhóm sau 10 ms. ASS dùng lại toàn bộ dòng trong từng event, mỗi event đổi màu và scale **114%** cho từ đang đọc. Từ khóa được chọn giữ màu vàng trong các event khác. Event đầu dòng fade vào **70 ms**, event ngắn hơn **20 ms** bị bỏ. ASS làm tròn tới 1/100 giây, SRT tới 1/1000 giây.
6. Xếp B-roll trước khi burn ASS bằng FFmpeg/libass. Sau đó chèn đồ họa và nối outro nếu có. Nếu dùng tốc độ toàn clip khác 1, app đổi tốc độ ở cuối chuỗi render, sau khi burn chữ. Mốc ví dụ trong kho là của timeline dựng ở tốc độ 1×.

### Kiểu chữ hiệu lực trên máy

| Thuộc tính | Giá trị |
| --- | --- |
| Khung thiết kế ASS | 1080 × 1920 |
| Font và cỡ | Be Vietnam Pro, Bold, 88 |
| Màu chữ thường | Trắng `#FFFFFF` · ASS `&H00FFFFFF` |
| Màu từ đang nói và từ khóa | Vàng `#F4DF0D` · ASS `&H000DDFF4` |
| Viền · bóng | Đen, viền 5, bóng 2 |
| Căn dòng · lề ngang | Dưới giữa (`Alignment=2`), trái và phải 60 |
| `margin_v` | **500** theo thiết lập UI trên máy, ghi đè mặc định YAML **680** |

Callout hai dòng tắt theo cấu hình nền. Khi bật thẻ hook, ASS có thể ẩn nhóm karaoke trong lúc thẻ hiện, còn SRT vẫn có nội dung. Một flash trắng ở mối nối hook có thể xuất hiện trong lớp ASS riêng tùy cấu hình. `vi-du-sub.json` ghi thứ tự phát đảo so với nguồn để kiểm tra phép đổi mốc. Hai đầu ra thực tế có trong `vi-du-sub.ass` và `vi-du-sub.srt`.

## Bóc sub từ link để lấy lời và làm kịch bản

Luồng **Bóc sub** nhận link clip, tải video bằng yt-dlp, kiểm tra có stream âm thanh rồi xuất WAV 16 kHz mono. Scribe cung cấp mốc từng từ. App ghép từ thành dòng văn bản, tách khi khoảng lặng đạt 0,6 giây hoặc dòng chạm ngưỡng mềm 180 ký tự, sau đó viết transcript TXT/SRT và lọc các dòng lặp hoặc có dấu hiệu nhận dạng ảo. Bước soạn lại thành kịch bản dùng AI, chạy sau khâu bóc lời. Nếu nhận dạng thất bại, trạng thái lỗi tách riêng với trường hợp đã nhận dạng được nhưng clip không có lời dùng được.

## Nhạc nền và mức âm

Thư viện hiện hành có **9 tệp**. Cấu hình nền ưu tiên tên chứa `Windy Hill`, volume **0.12** (hệ số tuyến tính, khoảng −18,4 dB), `music_ducking: false` và đích **−14 LUFS**. Clip có thể lưu bài riêng, chọn tự động, tắt nhạc hoặc bù âm lượng trong khoảng **−24 đến +12 dB**. Khi tự chọn, 10KVideo sắp danh sách tệp rồi chọn một vị trí ổn định từ mã băm tên clip.

Nhạc loop rồi cắt đúng thời lượng. Khi có outro, mức nhạc có thể tăng dần tới gấp đôi trong 0,8 giây và fade 1,2 giây cuối. Nếu bật ducking, sidechain dùng ngưỡng 0.05, tỷ lệ 4:1, attack 200 ms, release 1000 ms. Khâu trộn dùng limiter và chuẩn hóa với trần true peak −1,5 dBTP khi đặt đích LUFS.

[Danh mục nhạc](10kvideo-music.json) ghi tên đúng như tệp nguồn. Một số bản phát hành từ bên thứ ba giới hạn việc phân phối lại tệp độc lập. *Inspiring Acoustic* có nguồn và điều khoản trực tiếp từ nhà phát hành. [Trang bài nhạc](https://shop.ashamaluevmusic.com/products/inspiring-acoustic) · [Điều khoản AShamaluevMusic](https://shop.ashamaluevmusic.com/policies/terms-of-service).

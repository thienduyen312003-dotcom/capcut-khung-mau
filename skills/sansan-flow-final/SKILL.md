---
name: sansan-flow-final
description: Dựng final MP4 dọc kiểu Khung Mẫu từ video đã xuất trong Google Flow hoặc SanSan Studio. Dùng khi người dùng gửi MP4 và gọi SanSan Final, yêu cầu hoàn thiện video Flow theo mẫu final, hoặc muốn thêm lớp đen, sticker sóng nhạc, Nhấp nháy cổ điển, nhạc MASTER ANH ĐỨC và sub kiểu 10K.
---

# SanSan Flow Final

Quy trình của người dùng là **kịch bản → tạo và tải MP4 trong Flow → đưa MP4 vào Codex để dựng final**. Thực hiện bước cuối theo yêu cầu, trên tệp người dùng đưa. Với video SanSan Studio, ưu tiên MP4 đã ghép có tiếng nói. Xác định video từ tệp đính kèm hoặc đường dẫn được chỉ định. Khi chỉ có một lần tải phù hợp mà người dùng nói “file vừa tải”, dùng tệp `SanSan_Video_Nhanh*.mp4` mới nhất đã tải xong. Khi có nhiều nguồn khả dĩ, xác minh tệp trước khi render.

## Dựng final

Chạy `render_final.py` cạnh file này bằng Python của **10KVideo**. Trên máy tác giả, môi trường là `~/10KVideo/.venv/Scripts/python.exe`. Đặt đích `final.mp4` trong thư mục đầu ra của chat. Dùng tên thư mục riêng cho mỗi video nếu dựng một loạt.

```powershell
& "$env:USERPROFILE/10KVideo/.venv/Scripts/python.exe" -B -X utf8 `
  "<thư mục skill>/render_final.py" "<video nguồn>.mp4" --output "<đường dẫn tuyệt đối>/final.mp4"
```

Script dựng hai dải tối, phối lớp phim dọc của hiệu ứng Nhấp nháy cổ điển từ tài nguyên CapCut `7618619632592620805`, rồi áp GIF sóng nhạc. 10KVideo cung cấp bộ tạo chữ karaoke Việt, trộn bài MASTER ANH ĐỨC và render 1080 × 1920. Giữ mạch lời và tăng tốc toàn clip 1,1× sau khi ghép hình, phụ đề và tiếng. Phần phụ đề dùng ElevenLabs Scribe và khâu soát chính tả theo cấu hình 10K của người dùng. Codex đăng nhập với ChatGPT là cơ chế xác thực cho khâu soát chữ nếu 10K đang dùng Codex. Script hỗ trợ `--words <tệp JSON>` khi đã có mốc từng từ để render lại mà không gọi các dịch vụ nhận dạng hoặc sửa chữ.

Xác nhận lệnh báo hoàn thành, MP4 có hình 1080 × 1920 và có audio. Soi ít nhất ở đầu, giữa và cuối clip để kiểm lớp đen, sóng nhạc, phụ đề và dấu bụi/xước phim. Dùng tiếng Việt khi báo kết quả và liên kết đến MP4, kèm điểm nào khác mẫu nếu có.

## Dùng trên máy khác

- Cần 10KVideo đã cài và cấu hình phần nhận dạng. Nếu thư mục app khác mặc định, truyền `--app-dir`; FFmpeg và FFprobe phải có trên `PATH` hoặc truyền `--ffmpeg` và `--ffprobe`. Bản render đã kiểm trên Windows.
- Cấp cho script đường dẫn đến checkout hoặc bản giải nén của [repo tài nguyên riêng tư](https://github.com/thienduyen312003-dotcom/capcut-khung-mau-assets) qua `--assets`. Thư mục này cần có `sticker-song-nhac.gif` và `hieu-ung-nhap-nhay-co-dien.zip`. Nhạc được lấy từ `library/music` của 10K hoặc cùng thư mục tài nguyên. `--music` cho phép chọn tệp có quyền sử dụng nếu người dùng có yêu cầu đổi nhạc.
- Mỗi người dùng 10K tự thiết lập tài khoản nhận dạng và phiên đăng nhập Codex của họ nếu bật soát chính tả. Chỉ đưa các tệp media được phép dùng vào bộ cài của họ.

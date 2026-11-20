"""Render a SanSan Studio MP4 on demand with the user's existing 10KVideo app."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile


SKILL = Path(__file__).resolve().parent
MASTER = "NHẠC NỀN - MASTER ANH ĐỨC.MP3"
FILM_ENTRY = "hieu-ung/AmazingFeature/resource/video/Potrait.mp4"

# The right half of the 9:16 CapCut texture stores a premultiplied white film
# layer. Screen blending reproduces white premultiplied alpha composition.
# The project sliders map to 0.50 playback speed and 0.40 opacity.
VIDEO_GRAPH = ";".join([
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
    "crop=1080:1920,setsar=1,fps=30[base]",
    "[1:v]format=rgba[matte]",
    "[base][matte]overlay=shortest=1,format=gbrp[shaded]",
    "[2:v]crop=iw/2:ih:iw/2:0,scale=1080:1920:flags=bilinear,format=gbrp,"
    "setsar=1,setpts=2*(PTS-STARTPTS),fps=30[film]",
    "[shaded][film]blend=all_mode=screen:all_opacity=0.4:shortest=1[aged]",
    "[3:v]format=rgba,scale=540:540,setsar=1[wave]",
    "[aged][wave]overlay=270:965:shortest=1[video]",
])


def probe(path, ffprobe):
    return json.loads(subprocess.check_output([
        ffprobe, "-v", "error", "-show_entries",
        "stream=codec_type,width,height:format=duration", "-of", "json", str(path),
    ]))


def require_file(path):
    if not path.is_file():
        raise RuntimeError(f"Không tìm thấy tệp {path}")
    return path


def prepare(source, scratch, assets, ffmpeg):
    sticker = require_file(assets / "sticker-song-nhac.gif")
    mask = require_file(SKILL / "black-matte.png")
    film = scratch / "film.mp4"
    cache_zip = require_file(assets / "hieu-ung-nhap-nhay-co-dien.zip")
    with ZipFile(cache_zip) as archive:
        film.write_bytes(archive.read(FILM_ENTRY))
    staged = scratch / "video-khung-mau.mp4"
    subprocess.run([
        ffmpeg, "-nostdin", "-y", "-v", "error", "-i", str(source),
        "-loop", "1", "-framerate", "30", "-i", str(mask),
        "-stream_loop", "-1", "-i", str(film), "-ignore_loop", "0", "-i", str(sticker),
        "-filter_complex_threads", "3", "-filter_complex", VIDEO_GRAPH,
        "-map", "[video]", "-map", "0:a:0", "-shortest", "-c:v", "libx264",
        "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "16", "-c:a", "copy", str(staged),
    ], check=True)
    return staged


def run_10k(source, staged, scratch, args, music):
    sys.path.insert(0, str(args.app_dir))
    from app.models.app_config import load_config
    from app.models.edit_decisions import EditDecisions, Word
    from app.pipeline import build_ass_subtitles, clean_transcript, extract_audio
    from app.pipeline import fix_transcript_spelling, transcribe_speech, transcript_cache
    from app.pipeline.detect_fillers_and_cuts import detect_audio_silences, detect_candidates, merge_cuts
    from app.pipeline.render_ffmpeg_timeline import render

    cfg = load_config(args.app_dir / "config.yaml")
    wav = extract_audio.extract_audio(source, scratch, args.ffmpeg)
    cached = transcript_cache.load_words(source) if args.words is None else None
    review_words = args.words is None and (cached is None or cached[1] == "srt")
    if args.words:
        payload = json.loads(args.words.read_text(encoding="utf-8-sig"))
        if "words" in payload:
            words = [Word.model_validate(word) for word in payload["words"]]
        else:
            words = [Word(text=word["w"], start=word["s"], end=word["e"])
                     for segment in payload["segments"] for word in segment["words"]]
    elif cached:
        words = cached[0]
    else:
        print("Bóc lời bằng cấu hình 10KVideo…", flush=True)
        words = transcribe_speech.transcribe(wav, cfg)

    words, _ = clean_transcript.clean(words)
    if not words:
        raise RuntimeError("10KVideo không nhận được lời thoại để làm phụ đề.")
    if review_words and cfg.get("llm", {}).get("subfix_enabled", True):
        print("Soát chữ theo thiết lập 10KVideo…", flush=True)
        fix_transcript_spelling.fix_spelling(words, channel_brief=cfg.get("channel", {}).get("brief", ""),
                                             timeout=cfg.get("llm", {}).get("timeout_seconds", 240))

    duration = extract_audio.probe_duration(staged, args.ffprobe)
    cutting = cfg["cutting"]
    silence, breath = cutting["min_silence"], cutting["keep_breath"]
    cuts = detect_candidates(words, duration, cutting["filler_words"], silence, breath, cutting["padding_ms"])
    cuts = merge_cuts(cuts + detect_audio_silences(wav, args.ffmpeg, words, silence, breath))
    decisions = EditDecisions(source_path=str(staged), duration=duration, words=words, cuts=cuts,
                              video_format="nguyen-mach", speed=1.1, hook_enabled=False, cta="",
                              music_file=music.name)
    style = {**cfg["subtitles"], "font_name": "Be Vietnam Pro", "font_size": 88,
             "margin_v": 500, "max_words_per_event": 5, "outline": 5, "callout": False,
             "primary_color": "&H00FFFFFF", "active_color": "&H000DDFF4", "emphasis_color": "&H000DDFF4",
             "hook_card": False, "hook_flash": False}
    render_config = {**cfg["render"], "width": 1080, "height": 1920}
    render_config.update(out_width=1080, out_height=1920)
    audio_config = {**cfg["audio"], "music_enabled": True, "music_dir": str(music.parent),
                    "music_volume": 0.12, "music_ducking": False, "target_lufs": -14}
    ass, _ = build_ass_subtitles.build_subtitles(decisions, scratch, style, render_config)
    print(f"Dựng phụ đề và trộn nhạc ({len(words)} từ có mốc)…", flush=True)
    return render(decisions, ass, scratch, render_config, ffmpeg_cmd=args.ffmpeg,
                  audio_cfg=audio_config, out_name="rendered.mp4")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assets", type=Path, default=SKILL / "private-assets")
    parser.add_argument("--app-dir", type=Path, default=Path.home() / "10KVideo")
    parser.add_argument("--music", type=Path)
    parser.add_argument("--words", type=Path, help="Mốc từ có sẵn để dựng lại không gọi ASR hoặc AI.")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    args.app_dir = args.app_dir.resolve()
    source = require_file(args.source.resolve())
    output = args.output.resolve()
    if source.suffix.lower() != ".mp4" or output.suffix.lower() != ".mp4":
        parser.error("Đầu vào và đầu ra phải là MP4.")
    if output.exists():
        parser.error(f"Đích đã tồn tại: {output}. Chọn đường dẫn mới.")
    if not shutil.which(args.ffmpeg) or not shutil.which(args.ffprobe):
        parser.error("Thiếu FFmpeg hoặc FFprobe.")
    require_file(args.app_dir / "config.yaml")
    require_file(args.app_dir / "app/assets/fonts/BeVietnamPro-Bold.ttf")
    music = args.music or args.app_dir / "library/music" / MASTER
    if args.music is None and not music.is_file():
        music = args.assets / MASTER
    music = require_file(music.resolve())
    source_streams = {stream["codec_type"] for stream in probe(source, args.ffprobe)["streams"]}
    if not {"video", "audio"} <= source_streams:
        parser.error("MP4 nguồn phải có cả hình và tiếng.")
    output.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(prefix="sansan-final-", dir=output.parent) as directory:
        scratch = Path(directory)
        print("Áp lớp đen, sticker và lớp phim cổ điển…", flush=True)
        staged = prepare(source, scratch, args.assets, args.ffmpeg)
        rendered = run_10k(source, staged, scratch, args, music)
        video = probe(rendered, args.ffprobe)
        main_video = next(s for s in video["streams"] if s["codec_type"] == "video")
        if (main_video.get("width"), main_video.get("height")) != (1080, 1920):
            raise RuntimeError("Độ phân giải bản xuất khác 1080 × 1920.")
        if not any(s["codec_type"] == "audio" for s in video["streams"]):
            raise RuntimeError("Bản xuất không có audio.")
        subprocess.run([args.ffmpeg, "-nostdin", "-v", "error", "-xerror", "-i", str(rendered),
                        "-f", "null", "-"], check=True)
        rendered.rename(output)  # Windows refuses to overwrite a file created by a concurrent run.
    print(json.dumps({"output": str(output), "seconds": float(video["format"]["duration"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()

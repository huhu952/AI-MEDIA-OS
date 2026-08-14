#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-MEDIA-OS 统一视频分析器

子命令：
  info        <video>                      读取视频元数据（时长/分辨率/编码/码率等）
  audio       <video> --out <wav>          抽取音频（默认 16k 单声道 wav，便于 Whisper）
  frames      <video> --out <dir>          抽帧（--every 秒 / --count 张 / --scene 场景帧）
  transcribe  <video|audio> --model tiny   语音转文字 -> txt + srt + json
  shots       <video>                      镜头切分（场景检测）
  hook        <video>                      前 3 秒 Hook 分析（亮度/运动/切变/音量）
  rhythm      <video>                      节奏分析（镜头时长分布、切点密度）
  report      <video> --out <dir>          综合报告（info+shots+hook+rhythm+可选转写）

依赖：ffmpeg/ffprobe（PATH）、可选 cv2/numpy/faster-whisper。
"""

import argparse
import json
import os
import re
import subprocess
import sys
from fractions import Fraction

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace")


def need(cmd):
    r = run(cmd)
    return r.returncode == 0


def ffprobe_json(path):
    if not need(["ffprobe", "-version"]):
        raise RuntimeError("ffprobe 不可用，请确认 FFmpeg 已安装并加入 PATH")
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path])
    if r.returncode != 0:
        raise RuntimeError("ffprobe 读取失败: " + r.stderr[-500:])
    return json.loads(r.stdout)


def fmt_sec(s):
    try:
        return str(datetime_timedelta(seconds=float(s)))
    except Exception:
        return f"{s}s"


def datetime_timedelta(seconds):
    import datetime
    return datetime.timedelta(seconds=seconds)


def parse_rate(rate):
    try:
        f = Fraction(rate)
        return float(f)
    except Exception:
        return None


def cmd_info(args):
    data = ffprobe_json(args.video)
    fmt = data.get("format", {})
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    lines = [
        f"文件: {args.video}",
        f"时长: {fmt_sec(fmt.get('duration', 0))}",
        f"大小: {int(fmt.get('size', 0)) / 1024 / 1024:.1f} MB",
        f"封装: {fmt.get('format_name', '?')}",
        f"总码率: {int(fmt.get('bit_rate', 0)) / 1000:.0f} kbps",
    ]
    if v:
        lines += [
            f"视频: {v.get('codec_name')}  {v.get('width')}x{v.get('height')}  "
            f"{parse_rate(v.get('r_frame_rate')) or '?'} fps",
            f"像素: {v.get('pix_fmt')}  总帧数: {v.get('nb_frames', '?')}",
        ]
    if a:
        lines.append(
            f"音频: {a.get('codec_name')}  {a.get('sample_rate')}Hz  "
            f"{a.get('channels')}ch  {a.get('channel_layout', '')}"
        )
    print("\n".join(lines))
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return data


def cmd_audio(args):
    if not need(["ffmpeg", "-version"]):
        raise RuntimeError("ffmpeg 不可用")
    out = args.out or os.path.splitext(args.video)[0] + ".wav"
    if args.format == "mp3":
        r = run(["ffmpeg", "-y", "-i", args.video, "-vn", "-acodec", "libmp3lame",
                 "-q:a", "2", out])
    else:
        r = run(["ffmpeg", "-y", "-i", args.video, "-vn", "-acodec", "pcm_s16le",
                 "-ar", "16000", "-ac", "1", out])
    if r.returncode != 0:
        raise RuntimeError("音频提取失败: " + r.stderr[-500:])
    print(f"已输出: {out}（{os.path.getsize(out) / 1024:.0f} KB）")
    return out


def cmd_frames(args):
    if not need(["ffmpeg", "-version"]):
        raise RuntimeError("ffmpeg 不可用")
    data = ffprobe_json(args.video)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    dur = float(data.get("format", {}).get("duration", 0) or 0)
    outdir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.video)),
                                      os.path.splitext(os.path.basename(args.video))[0] + "_frames")
    os.makedirs(outdir, exist_ok=True)
    pattern = os.path.join(outdir, "frame_%03d.jpg")
    if args.scene:
        vf = f"select='gt(scene,{args.scene})',showinfo"
        r = run(["ffmpeg", "-y", "-i", args.video, "-vf", vf, "-vsync", "vfr",
                 "-q:v", "3", pattern])
        times = re.findall(r"pts_time:([0-9.]+)", r.stderr)
        print(f"场景帧: {len(times)} 张 -> {outdir}")
        return outdir
    if args.count and dur > 0:
        fps = max(1.0, args.count / max(dur, 0.1))
        r = run(["ffmpeg", "-y", "-i", args.video, "-vf", f"fps={fps:.4f}",
                 "-frames:v", str(args.count), "-q:v", "3", pattern])
    else:
        every = args.every or 1
        r = run(["ffmpeg", "-y", "-i", args.video, "-vf", f"fps=1/{every}",
                 "-q:v", "3", pattern])
    if r.returncode != 0:
        raise RuntimeError("抽帧失败: " + r.stderr[-500:])
    n = len([f for f in os.listdir(outdir) if f.startswith("frame_")])
    print(f"已抽帧: {n} 张 -> {outdir}")
    return outdir


def cmd_transcribe(args):
    src = args.video
    if os.path.splitext(src)[1].lower() not in (".wav", ".mp3", ".flac", ".m4a", ".aac"):
        src = cmd_audio(argparse.Namespace(
            video=args.video, out=args.audio_out, format="wav"))
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("faster-whisper 未安装: pip install faster-whisper")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    seg_iter, info = model.transcribe(src, language=args.language or None,
                                      vad_filter=True, beam_size=args.beam)
    segments = [{"start": round(s.start, 2), "end": round(s.end, 2),
                 "text": s.text.strip()} for s in seg_iter]
    base = args.out or os.path.splitext(src)[0]
    txt = "\n".join(s["text"] for s in segments if s["text"])
    srt = "".join(
        f"{i}\n{_srt_ts(s['start'])} --> {_srt_ts(s['end'])}\n{s['text']}\n\n"
        for i, s in enumerate(segments, 1) if s["text"])
    with open(base + ".txt", "w", encoding="utf-8-sig") as f:
        f.write(txt)
    with open(base + ".srt", "w", encoding="utf-8-sig") as f:
        f.write(srt)
    with open(base + ".segments.json", "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    print(f"语音转写完成: {len(segments)} 段, {len(txt)} 字")
    print("输出: " + base + ".{txt,srt,segments.json}")
    return segments


def _srt_ts(sec):
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def cmd_shots(args):
    if not need(["ffmpeg", "-version"]):
        raise RuntimeError("ffmpeg 不可用")
    data = ffprobe_json(args.video)
    dur = float(data.get("format", {}).get("duration", 0) or 0)
    vf = f"select='gt(scene,{args.threshold})',showinfo"
    r = run(["ffmpeg", "-i", args.video, "-vf", vf, "-f", "null", "-"])
    times = sorted(set(float(t) for t in re.findall(r"pts_time:([0-9.]+)", r.stderr)))
    cuts = [0.0] + times + [dur]
    shots = [{"start": round(cuts[i], 2), "end": round(cuts[i + 1], 2),
              "duration": round(cuts[i + 1] - cuts[i], 2)} for i in range(len(cuts) - 1)]
    print(f"镜头数: {len(shots)}（阈值 {args.threshold}）")
    for s in shots:
        print(f"  {s['start']:>8.2f}s - {s['end']:>8.2f}s  时长 {s['duration']:>6.2f}s")
    return shots


def cmd_hook(args):
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise RuntimeError("hook 分析需要 opencv-python 与 numpy")
    data = ffprobe_json(args.video)
    dur = float(data.get("format", {}).get("duration", 0) or 0)
    hook_len = min(3.0, dur)
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise RuntimeError("无法打开视频")
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    max_frames = int(hook_len * fps)
    frames = []
    for _ in range(max_frames):
        ok, fr = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY))
    cap.release()
    if not frames:
        raise RuntimeError("未读取到帧")
    bright = float(np.mean(frames)) / 255
    motion = []
    for i in range(1, len(frames)):
        motion.append(float(np.mean(np.abs(frames[i].astype(int) - frames[i - 1].astype(int)))) / 255)
    avg_motion = float(np.mean(motion)) if motion else 0
    max_motion = float(np.max(motion)) if motion else 0
    scene_changes = sum(1 for m in motion if m > 0.25)
    audio_peak = "?"
    r = run(["ffmpeg", "-i", args.video, "-t", str(hook_len), "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"max_volume:\s*(-?[0-9.]+)\s*dB", r.stderr)
    if m:
        audio_peak = m.group(1) + " dB"
    out = {
        "hook_seconds": hook_len, "avg_brightness": round(bright, 3),
        "avg_motion": round(avg_motion, 3), "max_motion": round(max_motion, 3),
        "scene_changes": scene_changes, "audio_max_volume_db": audio_peak,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return out


def cmd_rhythm(args):
    shots = cmd_shots(argparse.Namespace(video=args.video, threshold=args.threshold))
    durs = [s["duration"] for s in shots if s["duration"] > 0]
    total = sum(durs)
    n = len(durs)
    avg = total / n if n else 0
    med = sorted(durs)[n // 2] if n else 0
    cuts_per_min = max(0, (n - 1)) / (total / 60) if total else 0
    out = {
        "shots": n, "avg_shot_sec": round(avg, 2), "median_shot_sec": round(med, 2),
        "min_shot_sec": round(min(durs), 2) if durs else None,
        "max_shot_sec": round(max(durs), 2) if durs else None,
        "cuts_per_minute": round(cuts_per_min, 1),
        "pace": "快" if avg < 3 else ("中" if avg < 6 else "慢"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return out


def cmd_report(args):
    data = ffprobe_json(args.video)
    dur = float(data.get("format", {}).get("duration", 0) or 0)
    outdir = args.out or os.path.join(
        os.path.dirname(os.path.abspath(args.video)),
        os.path.splitext(os.path.basename(args.video))[0] + "_analysis")
    os.makedirs(outdir, exist_ok=True)
    info = cmd_info(argparse.Namespace(video=args.video, json=False))
    shots = cmd_shots(argparse.Namespace(video=args.video, threshold=args.threshold))
    hook = cmd_hook(argparse.Namespace(video=args.video))
    rhythm = cmd_rhythm(argparse.Namespace(video=args.video, threshold=args.threshold))
    segs = []
    if args.transcribe:
        segs = cmd_transcribe(argparse.Namespace(
            video=args.video, model=args.transcribe, language=args.language,
            beam=5, out=os.path.join(outdir, "transcript"), audio_out=None))
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    lines = [
        f"# 视频分析报告 — {os.path.basename(args.video)}",
        "",
        f"- 时长：{fmt_sec(dur)}",
        f"- 分辨率：{v.get('width')}x{v.get('height')} @ {parse_rate(v.get('r_frame_rate')) or '?'}fps",
        f"- 格式：{data.get('format', {}).get('format_name')} / 大小 {int(data.get('format', {}).get('size', 0)) / 1048576:.1f}MB",
        "",
        "## 镜头结构",
        f"共 {len(shots)} 个镜头（阈值 {args.threshold}）：",
        "",
        "| # | 起 (s) | 止 (s) | 时长 (s) |",
        "| --- | --- | --- | --- |",
    ]
    lines += [f"| {i+1} | {s['start']} | {s['end']} | {s['duration']} |" for i, s in enumerate(shots)]
    lines += [
        "",
        "## 节奏分析",
        f"- 平均镜头 {rhythm['avg_shot_sec']}s / 中位 {rhythm['median_shot_sec']}s",
        f"- 每分钟切点数 {rhythm['cuts_per_minute']} → 节奏{rhythm['pace']}",
        "",
        "## 前 3 秒 Hook",
        f"- 亮度 {hook['avg_brightness']}（0-1） | 平均运动 {hook['avg_motion']} | 场景突变 {hook['scene_changes']} 次",
        f"- 音频峰值 {hook['audio_max_volume_db']}",
        "",
    ]
    if segs:
        lines += ["## 字幕 / 转写", ""]
        lines += [f"- [{s['start']}s-{s['end']}s] {s['text']}" for s in segs if s["text"]]
        lines += [""]
    lines += ["## 结论（待人工补充）", ""]
    md = os.path.join(outdir, "report.md")
    with open(md, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))
    print(f"报告已生成: {md}")
    return md


def main():
    p = argparse.ArgumentParser(description="AI-MEDIA-OS 统一视频分析器")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_text):
        sp = sub.add_parser(name, help=help_text)
        sp.set_defaults(fn=fn)
        return sp

    sp = add("info", cmd_info, "读取视频元数据")
    sp.add_argument("video"); sp.add_argument("--json", action="store_true")

    sp = add("audio", cmd_audio, "抽取音频")
    sp.add_argument("video"); sp.add_argument("--out"); sp.add_argument("--format", default="wav")

    sp = add("frames", cmd_frames, "抽帧")
    sp.add_argument("video"); sp.add_argument("--out")
    sp.add_argument("--every", type=float)
    sp.add_argument("--count", type=int)
    sp.add_argument("--scene", type=float, help="场景检测阈值 0-1")

    sp = add("transcribe", cmd_transcribe, "语音转文字")
    sp.add_argument("video"); sp.add_argument("--out"); sp.add_argument("--audio-out")
    sp.add_argument("--model", default="tiny")
    sp.add_argument("--language"); sp.add_argument("--beam", type=int, default=5)

    sp = add("shots", cmd_shots, "镜头切分")
    sp.add_argument("video"); sp.add_argument("--threshold", type=float, default=0.35)

    sp = add("hook", cmd_hook, "前 3 秒 Hook 分析")
    sp.add_argument("video")

    sp = add("rhythm", cmd_rhythm, "节奏分析")
    sp.add_argument("video"); sp.add_argument("--threshold", type=float, default=0.35)

    sp = add("report", cmd_report, "综合报告")
    sp.add_argument("video"); sp.add_argument("--out")
    sp.add_argument("--threshold", type=float, default=0.35)
    sp.add_argument("--transcribe", help="转写模型 tiny/base/small")
    sp.add_argument("--language")

    args = p.parse_args()
    try:
        args.fn(args)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

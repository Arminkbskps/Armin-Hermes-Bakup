"""
_project_manager.py — Per-run project folder management with Persian-safe slugs.

Place next to your automation script. Each run creates:
  projects/YYYY-MM-DD_<persian-slug>/
    info.json, narration_fa.txt, youtube_post.txt, telegram_post.txt,
    results.txt, audio.wav
"""
from __future__ import annotations
import json
import re
import shutil
import time
from pathlib import Path
from typing import Optional


# Persian-safe slug generation
_SAFE_CHARS = {
    " ": "-", "/": "-", "\\": "-", ":": "-", "?": "", "!": "",
    ".": "", ",": "", "'": "", '"': "", "#": "", "$": "", "%": "",
    "&": "-", "*": "", "+": "-", "=": "-", "@": "", "`": "", "~": "",
    "(": "", ")": "", "[": "", "]": "", "{": "", "}": "", "<": "", ">": "", "|": "",
}


def _persian_slug(text: str, max_len: int = 50) -> str:
    """Convert Persian/English text to a URL-safe slug preserving Persian chars."""
    cleaned = []
    for ch in text.strip():
        if (
            "\u0600" <= ch <= "\u06FF"  # Persian/Arabic
            or "\u0750" <= ch <= "\u077F"  # Arabic Supplement
            or "\u08A0" <= ch <= "\u08FF"  # Arabic Extended-A
            or "\u0660" <= ch <= "\u0669"  # Eastern Arabic numerals
            or "\u06F0" <= ch <= "\u06F9"  # Persian numerals
            or "a" <= ch.lower() <= "z"
            or "0" <= ch <= "9"
        ):
            cleaned.append(ch)
        elif ch in _SAFE_CHARS:
            cleaned.append(_SAFE_CHARS[ch])
        else:
            cleaned.append("-")
    slug = re.sub(r"-{2,}", "-", "".join(cleaned)).strip("-")
    return slug[:max_len].rstrip("-") if len(slug) > max_len else slug


def _folder_name(topic: str) -> str:
    return f"{time.strftime('%Y-%m-%d')}_{_persian_slug(topic)}"


class ProjectManager:
    def __init__(self, root: Path):
        self._root = root
        self._projects_dir = root / "projects"
        self._projects_dir.mkdir(parents=True, exist_ok=True)

    def create_run(self, topic: str) -> tuple[Path, str]:
        folder_name = _folder_name(topic)
        proj_dir = self._projects_dir / folder_name
        proj_dir.mkdir(parents=True, exist_ok=True)
        info = {
            "topic": topic,
            "folder_name": folder_name,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "started",
            "steps_completed": [],
        }
        self._write_json(proj_dir / "info.json", info)
        return proj_dir, folder_name

    def save_narration(self, proj_dir: Path, text: str) -> None:
        (proj_dir / "narration_fa.txt").write_text(text, encoding="utf-8")
        self._append_step(proj_dir, "narration_extracted")

    def save_youtube_post(self, proj_dir: Path, text: str) -> None:
        (proj_dir / "youtube_post.txt").write_text(text, encoding="utf-8")
        self._append_step(proj_dir, "youtube_post_saved")

    def save_telegram_post(self, proj_dir: Path, text: str) -> None:
        (proj_dir / "telegram_post.txt").write_text(text, encoding="utf-8")
        self._append_step(proj_dir, "telegram_post_saved")

    def save_results(self, proj_dir: Path, label: str, text: str) -> None:
        with (proj_dir / "results.txt").open("a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n{label}\n{'='*60}\n{text.strip()}\n\n")

    def copy_audio(self, proj_dir: Path, src: Path) -> Optional[Path]:
        if not src or not src.is_file():
            return None
        dest = proj_dir / "audio.wav"
        try:
            shutil.copy2(str(src), str(dest))
            return dest
        except Exception:
            return None

    def mark_completed(self, proj_dir: Path) -> None:
        self._append_step(proj_dir, "completed")
        self._update_status(proj_dir, "completed")

    def mark_error(self, proj_dir: Path, error: str) -> None:
        self._append_step(proj_dir, f"error: {error}")
        self._update_status(proj_dir, "error")

    # -- listing (for dashboard) --

    def list_projects(self) -> list[dict]:
        if not self._projects_dir.is_dir():
            return []
        projects = []
        for entry in sorted(self._projects_dir.iterdir(),
                            key=lambda p: p.stat().st_mtime, reverse=True):
            if not entry.is_dir():
                continue
            info = {}
            ip = entry / "info.json"
            if ip.is_file():
                try:
                    info = json.loads(ip.read_text(encoding="utf-8"))
                except Exception:
                    pass
            projects.append({
                "folder": entry.name,
                "topic": info.get("topic", ""),
                "status": info.get("status", "unknown"),
                "created_at": info.get("created_at", ""),
                "has_audio": (entry / "audio.wav").is_file(),
                "has_narration": (entry / "narration_fa.txt").is_file(),
                "has_youtube": (entry / "youtube_post.txt").is_file(),
                "has_telegram": (entry / "telegram_post.txt").is_file(),
            })
        return projects

    # -- internal --

    def _write_json(self, path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _update_status(self, proj_dir: Path, status: str) -> None:
        ip = proj_dir / "info.json"
        if ip.is_file():
            try:
                d = json.loads(ip.read_text(encoding="utf-8"))
                d["status"] = status
                self._write_json(ip, d)
            except Exception:
                pass

    def _append_step(self, proj_dir: Path, step: str) -> None:
        ip = proj_dir / "info.json"
        if ip.is_file():
            try:
                d = json.loads(ip.read_text(encoding="utf-8"))
                steps = d.setdefault("steps_completed", [])
                if step not in steps:
                    steps.append(step)
                self._write_json(ip, d)
            except Exception:
                pass

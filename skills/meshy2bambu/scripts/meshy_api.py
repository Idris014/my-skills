#!/usr/bin/env python3
"""Run one Meshy2Bambu upstream stage without chaining into later stages."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://api.meshy.ai"
TERMINAL_STATUSES = {"SUCCEEDED", "FAILED", "CANCELED"}


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_data_uri(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(suffix)
    if mime is None:
        raise ValueError(f"Unsupported image type: {path}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def api_key() -> str:
    value = os.environ.get("MESHY_API_KEY", "").strip()
    if not value:
        raise RuntimeError("MESHY_API_KEY is not set")
    return value


def api_json(method: str, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + endpoint,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Meshy2Bambu/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Meshy HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Meshy request failed: {exc.reason}") from exc


def wait_for_task(task_type: str, task_id: str, poll_seconds: float, timeout: float) -> dict[str, Any]:
    endpoint = f"/openapi/v1/{task_type}/{task_id}"
    deadline = time.monotonic() + timeout
    latest: dict[str, Any] = {}
    while time.monotonic() < deadline:
        latest = api_json("GET", endpoint)
        status = str(latest.get("status", "UNKNOWN"))
        progress = latest.get("progress", 0)
        print(f"{status} {progress}%", flush=True)
        if status in TERMINAL_STATUSES:
            return latest
        time.sleep(poll_seconds)
    raise TimeoutError(f"Task {task_id} did not finish within {timeout:.0f} seconds")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Meshy2Bambu/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response:
        destination.write_bytes(response.read())


def suffix_from_url(url: str, fallback: str) -> str:
    clean = url.split("?", 1)[0]
    suffix = Path(clean).suffix.lower()
    return suffix if suffix else fallback


def archive_result(task_type: str, result: dict[str, Any], output_dir: Path) -> list[Path]:
    downloaded: list[Path] = []
    json_write(output_dir / "task-result.json", result)

    if task_type == "image-to-image":
        for index, url in enumerate(result.get("image_urls", []), start=1):
            destination = output_dir / "previews" / f"view_{index:02d}{suffix_from_url(url, '.png')}"
            download(url, destination)
            downloaded.append(destination)
    else:
        model_urls = result.get("model_urls", {})
        for file_format, url in model_urls.items():
            if not isinstance(url, str) or file_format not in {"glb", "obj", "fbx", "stl", "3mf"}:
                continue
            filename = "source.glb" if file_format == "glb" else f"source.{file_format}"
            destination = output_dir / filename
            download(url, destination)
            downloaded.append(destination)

        thumbnail = result.get("thumbnail_url")
        if isinstance(thumbnail, str):
            destination = output_dir / "previews" / f"front{suffix_from_url(thumbnail, '.png')}"
            download(thumbnail, destination)
            downloaded.append(destination)

        for role, url in result.get("thumbnail_urls", {}).items():
            if not isinstance(url, str):
                continue
            destination = output_dir / "previews" / f"{role}{suffix_from_url(url, '.png')}"
            download(url, destination)
            downloaded.append(destination)

    checksums = {str(path.relative_to(output_dir)): sha256(path) for path in downloaded}
    json_write(output_dir / "SHA256SUMS.json", checksums)
    return downloaded


def make_multiview(args: argparse.Namespace) -> tuple[str, dict[str, Any], dict[str, Any]]:
    image = Path(args.image).expanduser().resolve()
    if not image.is_file():
        raise FileNotFoundError(image)
    payload = {
        "ai_model": args.ai_model,
        "prompt": args.prompt,
        "reference_image_urls": [file_data_uri(image)],
        "generate_multi_view": True,
    }
    archive = {
        **payload,
        "reference_image_urls": [
            {"local_path": str(image), "sha256": sha256(image)}
        ],
    }
    return "image-to-image", payload, archive


def common_3d_payload(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "ai_model": "latest",
        "should_texture": not args.no_texture,
        "enable_pbr": not args.no_texture,
        "texture_resolution": args.texture_resolution,
        "image_enhancement": args.image_enhancement,
        "remove_lighting": True,
        "should_remesh": False,
        "pose_mode": "",
        "auto_size": False,
        "target_formats": ["glb"],
        "moderation": True,
    }


def make_single_3d(args: argparse.Namespace) -> tuple[str, dict[str, Any], dict[str, Any]]:
    image = Path(args.image).expanduser().resolve()
    if not image.is_file():
        raise FileNotFoundError(image)
    payload = common_3d_payload(args)
    payload["image_url"] = file_data_uri(image)
    archive = {
        **payload,
        "image_url": {"local_path": str(image), "sha256": sha256(image)},
    }
    return "image-to-3d", payload, archive


def make_multi_3d(args: argparse.Namespace) -> tuple[str, dict[str, Any], dict[str, Any]]:
    images = [Path(value).expanduser().resolve() for value in args.images]
    if not 1 <= len(images) <= 4:
        raise ValueError("Multi-Image to 3D requires 1 to 4 images")
    missing = [path for path in images if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(map(str, missing)))
    payload = common_3d_payload(args)
    payload["image_urls"] = [file_data_uri(path) for path in images]
    archive = {
        **payload,
        "image_urls": [
            {"local_path": str(path), "sha256": sha256(path)}
            for path in images
        ],
    }
    return "multi-image-to-3d", payload, archive


def add_3d_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--texture-resolution", choices=("2k", "4k", "8k"), default="4k")
    parser.add_argument("--no-texture", action="store_true")
    parser.add_argument(
        "--image-enhancement",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Default is disabled to preserve approved reference images.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Write request.json without API calls.")
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=1800.0)
    subparsers = parser.add_subparsers(dest="command", required=True)

    multiview = subparsers.add_parser("multiview", help="Generate candidate multiview images.")
    multiview.add_argument("--image", required=True)
    multiview.add_argument("--prompt", required=True)
    multiview.add_argument(
        "--ai-model",
        required=True,
        choices=("nano-banana", "nano-banana-2", "nano-banana-pro", "gpt-image-2"),
        help="Required so the user approves the credit/quality choice.",
    )
    multiview.add_argument("--output-dir", required=True)

    single = subparsers.add_parser("single-3d", help="Create one Image to 3D task.")
    single.add_argument("--image", required=True)
    single.add_argument("--output-dir", required=True)
    add_3d_options(single)

    multi = subparsers.add_parser("multi-3d", help="Create one Multi-Image to 3D task.")
    multi.add_argument("--images", nargs="+", required=True)
    multi.add_argument("--output-dir", required=True)
    add_3d_options(multi)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    builders = {
        "multiview": make_multiview,
        "single-3d": make_single_3d,
        "multi-3d": make_multi_3d,
    }
    task_type, payload, archive = builders[args.command](args)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_write(output_dir / "request.json", archive)

    if args.dry_run:
        print(json.dumps(archive, indent=2, ensure_ascii=False))
        return 0

    response = api_json("POST", f"/openapi/v1/{task_type}", payload)
    task_id = response.get("result")
    if not isinstance(task_id, str) or not task_id:
        raise RuntimeError(f"Meshy did not return a task id: {response}")
    json_write(output_dir / "create-result.json", response)
    print(f"Task ID: {task_id}", flush=True)

    result = wait_for_task(task_type, task_id, args.poll_seconds, args.timeout)
    json_write(output_dir / "task-result.json", result)
    if result.get("status") != "SUCCEEDED":
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        return 2

    files = archive_result(task_type, result, output_dir)
    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

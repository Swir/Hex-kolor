"""Build, exercise and publish an immutable Windows release."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "release-config.json").read_text(encoding="utf-8"))
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", VERSION):
    raise ValueError("VERSION must contain a numeric major.minor.patch version")
TAG = "v" + VERSION
ZIP_NAME = f"{CONFIG['package']}-{TAG}-Windows-x64.zip"


def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_sha():
    value = os.environ.get("GITHUB_SHA")
    if not value:
        value = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
            value += "-local-changes"
    return value


def smoke(executable, report):
    report.unlink(missing_ok=True)
    run([str(executable.resolve()), "--self-test", str(report.resolve())], timeout=90,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    result = json.loads(report.read_text(encoding="utf-8"))
    if result.get("passed") is not True or result.get("version") != VERSION:
        raise RuntimeError(f"Frozen runtime verification failed: {result}")
    return result


def build():
    if sys.platform != "win32":
        raise RuntimeError("Windows release builds must run on Windows")
    output = ROOT / "release"
    output.mkdir(exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    results = []
    for app in CONFIG["applications"]:
        command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
                   "--specpath", "build", "--name", app["name"]]
        for package in app.get("collect", []):
            command.extend(["--collect-all", package])
        run(command + [app["entry"]])
        exe = ROOT / "dist" / (app["name"] + ".exe")
        results.append(smoke(exe, ROOT / "build" / (app["name"] + "-self-test.json")))
        shutil.copy2(exe, output / exe.name)
    info = {"version": VERSION, "source_sha": source_sha(), "python": sys.version,
            "dependencies": {name: importlib.metadata.version(name) for name in CONFIG.get("dependencies", []) + ["pyinstaller"]}}
    (output / "BUILD_INFO.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    (output / "runtime-verification.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    with zipfile.ZipFile(output / ZIP_NAME, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for app in CONFIG["applications"]:
            exe_name = app["name"] + ".exe"
            archive.write(output / exe_name, exe_name)
        for name in [CONFIG["readme"], "CHANGELOG.md", "VERSION"]:
            archive.write(ROOT / name, "README.md" if name == CONFIG["readme"] else name)
        for directory in ["assets/readme", "docs/screenshots"]:
            if (ROOT / directory).is_dir():
                for path in sorted((ROOT / directory).rglob("*")):
                    if path.is_file():
                        archive.write(path, path.relative_to(ROOT).as_posix())
        archive.write(output / "BUILD_INFO.json", "BUILD_INFO.json")
        archive.write(output / "runtime-verification.json", "runtime-verification.json")
    names = [app["name"] + ".exe" for app in CONFIG["applications"]] + [ZIP_NAME, "BUILD_INFO.json", "runtime-verification.json"]
    (output / "SHA256SUMS.txt").write_text("".join(f"{sha256(output / name)}  {name}\n" for name in names), encoding="utf-8")
    verify(output)


def verify(directory):
    checksums = {}
    for line in (directory / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        if Path(name).name != name or not re.fullmatch(r"[0-9a-f]{64}", digest) or name in checksums:
            raise ValueError("Invalid checksum manifest")
        checksums[name] = digest
        if sha256(directory / name) != digest:
            raise RuntimeError(f"Checksum mismatch: {name}")
    expected = {app["name"] + ".exe" for app in CONFIG["applications"]} | {ZIP_NAME, "BUILD_INFO.json", "runtime-verification.json"}
    if set(checksums) != expected:
        raise RuntimeError("Release asset manifest does not match the application configuration")
    info = json.loads((directory / "BUILD_INFO.json").read_text(encoding="utf-8"))
    if info["version"] != VERSION or info["source_sha"] != source_sha():
        raise RuntimeError("Package version/source provenance mismatch")
    scratch = ROOT / "build"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="package-check-", dir=scratch) as temp:
        target = Path(temp).resolve()
        if not target.is_relative_to(scratch.resolve()):
            raise RuntimeError("Unexpected verification directory")
        with zipfile.ZipFile(directory / ZIP_NAME) as archive:
            for member in archive.infolist():
                if not (target / member.filename).resolve().is_relative_to(target):
                    raise RuntimeError("Unsafe package member")
            archive.extractall(target)
        if json.loads((target / "BUILD_INFO.json").read_text(encoding="utf-8")) != info:
            raise RuntimeError("ZIP provenance mismatch")
        for app in CONFIG["applications"]:
            name = app["name"] + ".exe"
            if sha256(target / name) != checksums[name]:
                raise RuntimeError("Packaged EXE does not match the release EXE")
            smoke(target / name, target / (app["name"] + "-verified.json"))
    print(f"Verified {TAG}: checksums, source provenance and extracted Windows runtime")


def publish():
    repo = os.environ["GITHUB_REPOSITORY"]
    commit = os.environ["GITHUB_SHA"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("A full release source SHA is required")
    verify(ROOT / "release")
    existing = subprocess.run(["gh", "release", "view", TAG, "--repo", repo, "--json", "isDraft,targetCommitish"], cwd=ROOT, capture_output=True, text=True)
    asset_names = [app["name"] + ".exe" for app in CONFIG["applications"]] + [ZIP_NAME, "SHA256SUMS.txt", "BUILD_INFO.json", "runtime-verification.json"]
    assets = [str(ROOT / "release" / name) for name in asset_names]
    if existing.returncode == 0:
        data = json.loads(existing.stdout)
        if not data["isDraft"] or data["targetCommitish"] != commit:
            raise RuntimeError("This version already exists; public releases and other candidates are never overwritten")
        run(["gh", "release", "upload", TAG, *assets, "--clobber", "--repo", repo])
    else:
        run(["gh", "release", "create", TAG, *assets, "--draft", "--target", commit, "--title", f"{CONFIG['title']} {TAG}", "--notes-file", "RELEASE_NOTES.md", "--repo", repo])
    fresh = ROOT / "fresh-download"
    fresh.mkdir(exist_ok=True)
    run(["gh", "release", "download", TAG, "--repo", repo, "--dir", str(fresh), "--clobber"])
    verify(fresh)
    run(["gh", "release", "edit", TAG, "--draft=false", "--latest", "--repo", repo])
    print(f"Published https://github.com/{repo}/releases/tag/{TAG}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "build":
        build()
    elif mode == "verify":
        verify(Path(sys.argv[2]).resolve())
    elif mode == "publish":
        publish()
    else:
        raise SystemExit("Expected build, verify or publish")
